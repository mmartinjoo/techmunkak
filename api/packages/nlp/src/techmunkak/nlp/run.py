from techmunkak.nlp.services import train as train_service
from techmunkak.nlp.services import inference as inference_service

def train():
    train_service.train_skill_model()
    
def inference():
    skills = inference_service.inference("Full Stack Developer (.NET / React) | 100% zdalnie")
    print(skills)