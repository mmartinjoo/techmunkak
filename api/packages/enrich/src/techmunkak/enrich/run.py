from techmunkak.enrich import stages
from techmunkak.enrich.services.main_skill_extraction import get_main_skill_extractor

def main():
    print("enqueueing...")
    count = stages.enqueue_stage()
    print(f"enqueue done: {count} jobs")
    
    print("translating...")
    (finished, failed) = stages.translation_stage()
    print(f"translation done: {finished} finished, {failed} failed")
    
    print("extracting main skill...")
    (finished, failed) = stages.main_skill_extraction_stage()
    print(f"extraction done: {finished} finished, {failed} failed")
    
    print("embedding...")
    (finished, failed) = stages.embedding_stage()
    print(f"embedding done: {finished} finished, {failed} failed")
    
def extract():
    print("extracting main skill...")
    (finished, failed) = stages.main_skill_extraction_stage()
    print(f"extraction done: {finished} finished, {failed} failed")