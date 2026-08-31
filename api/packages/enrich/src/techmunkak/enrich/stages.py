import traceback

from techmunkak.enrich.services import embedder, enrichment_queue, enrichment_results
from techmunkak.enrich.services import translation, main_skill_extraction
from techmunkak.enrich.services.main_skill_extraction import MainSkillExtractionResult

def enqueue_stage() -> int:
    return enrichment_queue.enqueue_next_batch()    
    
def translation_stage():
    jobs = enrichment_queue.dequeue_for_translation()
    finished = 0
    failed = 0
    
    for job in jobs:
        try:
            enrichment_queue.mark_translation_in_progress(job_key=job.job_key)
            translator = translation.get_translator(site_name=job.site_name)
            job_translation_result = translator.translate(job_key=job.job_key)
            enrichment_results.update_translation(job_key=job.job_key, job_translation_result=job_translation_result)
            enrichment_queue.mark_translation_finished(job_key=job.job_key)            
            finished += 1
        except Exception as exc:
            enrichment_queue.mark_translation_failed(job_key=job.job_key, error=traceback.format_exc())
            failed += 1
            print(exc)
            
    return (finished, failed)

def main_skill_extraction_stage():
    jobs = enrichment_queue.dequeue_for_main_skill_extraction()
    finished = 0
    failed = 0
    
    for job in jobs:
        try:
            enrichment_queue.mark_main_skill_extraction_in_progress(job_key=job.job_key)
            main_skill_extractor = main_skill_extraction.get_main_skill_extractor(site_name=job.site_name)
            result: MainSkillExtractionResult = main_skill_extractor.extract(job_key=job.job_key)
            enrichment_results.update_main_skill(job_key=job.job_key, main_skill_site_suggested=result.site_suggested, main_skill_nlp_suggested=result.nlp_suggested)
            enrichment_queue.mark_main_skill_extraction_finished(job_key=job.job_key)            
            finished += 1
        except Exception as exc:
            enrichment_queue.mark_main_skill_extraction_failed(job_key=job.job_key, error=traceback.format_exc())
            failed += 1
            print(exc)
            
    return (finished, failed)
            
def embedding_stage():
    jobs = enrichment_queue.dequeue_for_embedding()
    finished = 0
    failed = 0
        
    for job in jobs:
        try:
            enrichment_queue.mark_embedding_in_progress(job_key=job.job_key)
            ids = embedder.embed(job=job)
            enrichment_results.update_chroma_ids(job_key=job.job_key, chroma_ids=ids)
            enrichment_queue.mark_embedding_finished(job_key=job.job_key)
            finished += 1
        except Exception as exc:
            enrichment_queue.mark_embedding_failed(job_key=job.job_key, error=traceback.format_exc())
            failed += 1
            print(exc)
            
    return (finished, failed)