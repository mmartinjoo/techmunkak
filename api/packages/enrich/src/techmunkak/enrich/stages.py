import logging
import traceback

from techmunkak.embeddings.services import vector_store
from techmunkak.enrich.services import (
    enrichment_queue,
    enrichment_results,
    main_skill_extraction,
    translation,
)
from techmunkak.enrich.services.main_skill_extraction import MainSkillExtractionResult

logger = logging.getLogger(__name__)

def enqueue_stage() -> int:
    return enrichment_queue.enqueue_next_batch()    
    
def translation_stage():
    jobs = enrichment_queue.dequeue_for_translation()
    finished = 0
    failed = 0
    
    for job in jobs:
        try:
            logger.info(f"translating {job.job_key}")
            enrichment_queue.mark_translation_in_progress(job_key=job.job_key)
            translator = translation.get_translator(site_name=job.site_name)
            job_translation_result = translator.translate(job_key=job.job_key)
            enrichment_results.update_translation(job_key=job.job_key, job_translation_result=job_translation_result)
            enrichment_queue.mark_translation_finished(job_key=job.job_key)            
            logger.info(f"translated {job.job_key}, title: {job_translation_result.title}")
            finished += 1
        except Exception:
            enrichment_queue.mark_translation_failed(job_key=job.job_key, error=traceback.format_exc())
            logger.exception("translation failed for job %s", job.job_key)
            failed += 1
            
    return (finished, failed)

def main_skill_extraction_stage():
    jobs = enrichment_queue.dequeue_for_main_skill_extraction()
    finished = 0
    failed = 0
    
    for job in jobs:
        try:
            logger.info(f"extracting main skill for {job.job_key}")
            enrichment_queue.mark_main_skill_extraction_in_progress(job_key=job.job_key)
            main_skill_extractor = main_skill_extraction.get_main_skill_extractor(site_name=job.site_name)
            result: MainSkillExtractionResult = main_skill_extractor.extract(job_key=job.job_key)
            enrichment_results.update_main_skill(job_key=job.job_key, main_skill_site_suggested=result.site_suggested, main_skill_nlp_suggested=result.nlp_suggested)
            enrichment_queue.mark_main_skill_extraction_finished(job_key=job.job_key)            
            logger.info(f"extracted {job.job_key}, skills: {result.nlp_suggested}")
            finished += 1            
        except Exception:
            enrichment_queue.mark_main_skill_extraction_failed(job_key=job.job_key, error=traceback.format_exc())
            failed += 1
            logger.exception("main skill extraction failed for job %s", job.job_key)
            
    return (finished, failed)
            
def embedding_stage():
    jobs = enrichment_queue.dequeue_for_embedding()
    finished = 0
    failed = 0
        
    for job in jobs:
        try:
            logger.info(f"embedding {job.job_key}")
            enrichment_queue.mark_embedding_in_progress(job_key=job.job_key)
            ids = vector_store.store_job(content=job.content, metadata={"job_key": job.job_key})
            enrichment_results.update_chroma_ids(job_key=job.job_key, chroma_ids=ids)
            enrichment_queue.mark_embedding_finished(job_key=job.job_key)
            logger.info(f"embedded {job.job_key}, chroma IDs: {ids}")
            finished += 1
        except Exception:
            enrichment_queue.mark_embedding_failed(job_key=job.job_key, error=traceback.format_exc())
            failed += 1
            logger.exception("embedding failed for job %s", job.job_key)
            
    return (finished, failed)