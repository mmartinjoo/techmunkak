from techmunkak.nlp.services import model_loader
from techmunkak.nlp import DISABLED_PIPES, SKILL_LABEL

def inference(text: str) -> list[str]:
    nlp = model_loader.get_model()
    nlp.select_pipes(disable=DISABLED_PIPES)
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == SKILL_LABEL]
