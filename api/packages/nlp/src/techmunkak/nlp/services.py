import re
import spacy
import random
from spacy.training import Example
from techmunkak.core.db import pool


def train_technology_model():
    with pool().connection() as conn:
        rows = conn.execute("""
            select
                concat_ws(' ', j.title, j.description) as content,
                array_agg(s.name) as skills
            from silver.fact_job as j
            join silver.job_skills as js on js.job_key = j.job_key
            join silver.dim_skill as s on s.skill_key = js.skill_key
            group by 1
        """).fetchall()
        
    training_data = []
    for content, skills in rows:
        mentioned_skills = _find_skill_mentions(content=content, skills=skills)
        if mentioned_skills:
            training_data.append((content, {"entities": mentioned_skills}))

    nlp = spacy.load("en_core_web_sm")            
    ner = nlp.get_pipe("ner")
    ner.add_label("TECH")
    nlp.select_pipes(disable=["tagger", "parser", "attribute_ruler", "lemmatizer"])
    
    optimizer = nlp.initialize()
    for epoch in range(20):
        random.shuffle(training_data)
        for i in range(0, len(training_data), 32):
            batch = [Example.from_dict(nlp.make_doc(t), a) for t, a in training_data[i:i+32]]
            nlp.update(batch, sgd=optimizer)
            
    nlp.to_disk("./packages/nlp/models/ner")
    
def _find_skill_mentions(content: str, skills: list[str]) -> list[tuple[int, int, str]]:
    found = []
    for skill in skills:
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
        for m in re.finditer(pattern, content, re.IGNORECASE):
            found.append((m.start(), m.end(), "TECH"))
            
    # if there are multiple instances, the first one wins
    found.sort(key=lambda s: (s[1] - s[0], s[0]), reverse=True)
    kept = []
    for s in found:
        if not any(not (s[1] <= k[0] or s[0] >= k[1]) for k in kept):
            kept.append(s)
    return kept