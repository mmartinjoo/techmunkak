import pendulum
from airflow.sdk import Asset, dag, task
from techmunkak.core.logging import setup_logging
from techmunkak.skill_model import run

setup_logging()

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