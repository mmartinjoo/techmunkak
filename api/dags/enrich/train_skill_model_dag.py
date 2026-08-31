import pendulum
from airflow.sdk import dag, task, Asset
from techmunkak.nlp import run

@dag(
    dag_id="train_skill_model",
    catchup=False,
    schedule=Asset("x-enrichment-results://ready"),
    start_date=pendulum.datetime(2029, 9, 30, tz="UTC")
)
def train_skill_model():
    @task
    def train():
        run.train()
        
    train()

train_skill_model()