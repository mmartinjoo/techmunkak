import traceback

from techmunkak.embed.services import embedder, embedding_queue
from techmunkak.embed.services import translation, translated_jobs, embedded_jobs

def enqueue_stage():
    return embedding_queue.enqueue_next_batch()    
    
def translation_stage():
    jobs = embedding_queue.dequeue_for_translation()
    finished = 0
    failed = 0
    
    for job in jobs:
        try:
            translator = translation.get_translator(site_name=job.site_name)
            job_translation_result = translator.translate(job_key=job.job_key)
            translated_jobs.create_translated_job(job_key=job.job_key, job_translation_result=job_translation_result)
            embedding_queue.mark_translation_finished(job_key=job.job_key)            
            finished += 1
        except Exception as exc:
            embedding_queue.mark_translation_failed(job_key=job.job_key, error=traceback.format_exc())
            failed += 1
            print(exc)
            
    return (finished, failed)
            
def embedding_stage():
    jobs = embedding_queue.dequeue_for_embedding()
    finished = 0
    failed = 0
        
    for job in jobs:
        try:
            ids = embedder.embed(job=job)
            embedded_jobs.create_embedded_job(job_key=job.job_key, chroma_ids=ids)
            embedding_queue.mark_embedding_finished(job_key=job.job_key)
            finished += 1
        except Exception as exc:
            embedding_queue.mark_embedding_failed(job_key=job.job_key, error=traceback.format_exc())
            failed += 1
            print(exc)
            
    return (finished, failed)