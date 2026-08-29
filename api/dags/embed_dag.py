import pendulum
from datetime import timedelta
from airflow.sdk import dag, task
from techmunkak.embed.stages import enqueue_stage, translation_stage, embedding_stage

@dag(
    dag_id="embed",
    start_date=pendulum.datetime(2026, 8, 28, tz="UTC"),
    catchup=False,
    schedule="@daily",
)
def embed():
    @task(retries=3, retry_delay=timedelta(minutes=3))
    def enqueue() -> int:
        count = enqueue_stage()
        print(f"enqueued {count} jobs")
        return count
        
    @task(retries=3, retry_delay=timedelta(minutes=15))
    def translate() -> tuple[int, int]:
        (finished, failed) = translation_stage()
        print(f"translate: {finished} finished, {failed} failed")
        return (finished, failed)
    
    @task(retries=3, retry_delay=timedelta(minutes=10))
    def embed():
        (finished, failed) = embedding_stage()
        print(f"embed: {finished} finished, {failed} failed")
        return (finished, failed)
    
    enqueue() >> translate() >> embed()
        
embed()