from techmunkak.embed import stages

def main():
    print("enqueueing...")
    count = stages.enqueue_stage()
    print(f"enqueue done: {count} jobs")
    
    print("translating...")
    (finished, failed) = stages.translation_stage()
    print(f"translation done: {finished} finished, {failed} failed")
    
    print("embedding...")
    (finished, failed) = stages.embedding_stage()
    print(f"embedding done: {finished} finished, {failed} failed")