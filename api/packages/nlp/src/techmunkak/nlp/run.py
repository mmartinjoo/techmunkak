from techmunkak.nlp import services

def train():
    services.train_skill_model()
    
def inference():
    skills = services.inference("Full Stack Developer (.NET / React) | 100% zdalnie")
    print(skills)