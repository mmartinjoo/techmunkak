from techmunkak.embed.services import embedding_queue
from techmunkak.embed.services import translation

def main():
    print("embed")
    
def enqueue_next_batch():
    translator = translation.get_translator("NoFluffJobs")
    translator.need_translation(job_key="085b3c379dcf4b63b42ed4a59b1e8f94")
    job = translator.translate(job_key="085b3c379dcf4b63b42ed4a59b1e8f94")
    
    print(job)