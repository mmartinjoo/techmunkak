import random
from datetime import datetime
import json
from pathlib import Path
import spacy
from spacy.matcher import PhraseMatcher
from spacy.training import Example
from spacy.tokens import Span
from techmunkak.core.db import pool

LABEL = "SKILL"
EPOCHS = 50
BATCH_SIZE = 8
DISABLED_PIPES = ["tagger", "parser", "senter", "attribute_ruler", "lemmatizer"]

def load_skills() -> list[str]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select s.name
            from silver.dim_skill as s
            left join silver.blacklisted_skills as bs 
            on regexp_replace(lower(btrim(bs.name)), '\W', '-', 1, 0, 'i') = regexp_replace(lower(btrim(s.name)), '\W', '-', 1, 0, 'i')
            where bs.name is null        
        """)
        
    return sorted({row[0].strip() for row in rows if row[0].strip()})

def load_job_contents() -> list[str]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select
                case
                    when ej.id is not null then concat_ws(' ', ej.title_translated, ej.description_translated)
                    else concat_ws(' ', j.title, j.description)
                end as content
            from silver.fact_job as j 
            left join ops.enriched_jobs as ej on ej.job_key = j.job_key             
        """)
        
    return [row[0] for row in rows if row[0].strip()]

def build_skill_matcher(nlp: spacy.language.Language, skills: list[str]) -> PhraseMatcher:
    """
    Token-level matching: 'Go' matches only the standalone word, never 'Googlers'.
    This is what eliminates W030 warnings caused by regex, and .find() type matchers
    """
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    matcher.add("SKILLS", [nlp.make_doc(skill) for skill in skills])
    return matcher

def reject_overlaps(spans: list[Span]) -> list[Span]:
    """
    Returns a list, where spans do not have any overlaps with each other
    
    Overlap examples:
        (0,6) and (0,1) -> second one inside the first one, such as "Go" inside "Google"
        (0,3) and (1,4) -> second one starts in the first one        
        
    For an input like this:
    (3,5), (2,3), (8,10), (15,22), (18,20), (20,22)
    
    It returns a clean list like this:
    (3,5), (8,10), (15,22)
    
    This is important because otherwise "Go" would be recognized inside "Google" or "C" inside "C++" as a dedicated skill
    """
    
    spans = sorted(spans, key=lambda s: (s.end - s.start, s.start), reverse=True)
    kept = []
    for span in spans:
        # (1,4) vs (7,10) -> True -> aligns well without overlap 
        # (0,3) vs (2,4) -> False -> overlaps        
        aligns_without_overlap = lambda span, k: span.start > k.end or span.end < k.start
        
        # all([]) -> True so for empty 'kept', it returns True, 
        all_aligns_without_overlap = all([aligns_without_overlap(span, k) for k in kept])
        if all_aligns_without_overlap:
            kept.append(span)
            
    return kept

def build_training_examples(
    nlp: spacy.Language, 
    matcher: PhraseMatcher, 
    contents: list[str],
) -> list[Example]:
    examples = []
    for content in contents:
        doc = nlp.make_doc(text=content)
        spans = []
        
        for _, start, end in matcher(doc):
            span = doc[start:end]
            span.label_ = LABEL
            spans.append(span)
            
        spans = reject_overlaps(spans=spans)
        print("----SPANS----")
        print(spans)
        print("-------------")
        if not spans:
            continue
        
        doc.ents = spans
        examples.append(Example(predicted=doc, reference=doc))
    return examples

def evaluate(nlp: spacy.Language, dev: list[Example]) -> tuple[float, float]:
    """
    tp: true positives. Predictions that are actually true
    fp: false positives. Predictions that are false
    fn: false negatives. Missed predictions
    precision: what percentage of predicitons are true
    recall: what percentage of gold it "remembers"
    
    Example:
    gold = [1,2,3,4,5]
    got = [3,4,6,7]
    
    tp = [3,4] - true ones
    fp = [6,7] - false ones
    fn = [1,2,5] - missed ones
    
    precision = 0.5 (3,4 -> 3,4,6,7)
    recall = 0.4 (3,4 -> 1,2,3,4,5)
    
    """
    
    tp = fp = fn = 0
    for ex in dev:
        predicted = nlp(ex.reference.text)
        gold = {(e.start_char, e.end_char) for e in ex.reference.ents}
        got = {(e.start_char, e.end_char) for e in predicted.ents if e.label_ == LABEL}
        tp += len(gold & got)
        fp += len(got - gold)
        fn += len(gold - got)
    
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall

def save_model(nlp: spacy.Language):
    path = Path("./packages/nlp/models/ner")
    path.mkdir(parents=True, exist_ok=True)
    version = datetime.now().strftime("v%Y%m%d-%H%M%S")
    tmp = path / f"{version}.tmp"
    nlp.to_disk(tmp)
    final = path / version
    tmp.rename(final)
    (path / "current.json").write_text(json.dumps({"version": version}))
    print(f"model saved to {final}")

def train_skill_model():
    contents = load_job_contents()
    skills = load_skills()
    
    nlp = spacy.load("en_core_web_sm")
    ner = nlp.get_pipe("ner")
    ner.add_label(LABEL)
    nlp.select_pipes(disable=DISABLED_PIPES)
    
    matcher = build_skill_matcher(nlp, skills)
    examples = build_training_examples(nlp, matcher, contents)
    if len(examples) < 20:
        raise RuntimeError(f"not enough examples: {len(examples)}")
    
    avg_gold = sum(len(e.reference.ents) for e in examples) / len(examples)
    print(f"examples={len(examples)}, avg_gold_per_doc={avg_gold:.2f}")
    
    random.shuffle(examples)
    split = int(len(examples) * 0.9)
    train, dev = examples[:split], examples[split:]
    print(f"training set: {len(train)}, dev set: {len(dev)}")
    
    optimizer = nlp.initialize()
    for epoch in range(EPOCHS):
        print(f"training epoch {epoch}/{EPOCHS}")
        random.shuffle(train)
        for i in range(0, len(train), BATCH_SIZE):
            nlp.update(train[i : i + BATCH_SIZE], sgd=optimizer, drop=0.1)
            
    for ex in dev[:3]:
        pred = nlp(ex.reference.text)
        print("gold:", [(e.text, e.label_) for e in ex.reference.ents][:6],
              "| pred:", [(e.text, e.label_) for e in pred.ents][:6])    
        
    precision, recall = evaluate(nlp, dev)
    print(f"precision={precision:.2f}, recall={recall:.2f}")
    save_model(nlp)
    
def inference(text: str) -> list[str]:
    with open("./packages/nlp/models/ner/current.json", "r") as f:
        content = f.read()
        data = json.loads(content)
        nlp = spacy.load(f"./packages/nlp/models/ner/{data["version"]}")
        nlp.select_pipes(disable=DISABLED_PIPES)
        doc = nlp(text)
        return [ent.text for ent in doc.ents if ent.label_ == "SKILL"]