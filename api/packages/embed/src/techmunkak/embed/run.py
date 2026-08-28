from techmunkak.embed.services import embedding_queue
from techmunkak.embed.services import translation

def main():
    print("embed")
    
def enqueue_next_batch():
    translator = translation.get_translator("JustJoinIT")
    print(translator.need_translation(job_key="42ebe17f52a0b0025d325857d0e0717a"))