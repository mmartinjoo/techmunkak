from techmunkak.embed import stages

def main():
    print("enqueueing...")
    stages.enqueue_stage()
    print("enqueue done")
    
    print("translating...")
    stages.translation_stage()
    print("translation done")
    
    print("embedding...")
    stages.embedding_stage()
    print("embedding done")