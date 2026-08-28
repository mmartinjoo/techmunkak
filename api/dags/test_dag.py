import pendulum
from airflow.sdk import dag, task

@dag(
    dag_id="test_dag",
    start_date=pendulum.datetime(2026, 8, 23, tz="UTC"),
    catchup=False,
    tags=["test"]
)
def test_dag():
    @task()
    def extract():
        return {"a": 1, "b": 2}

    @task(multiple_outputs=True)
    def transform(data: dict):
        total = 0
        for value in data.values():
            total += value
            
        return {"total": total}
    
    @task()
    def load(total: float):
        print(f"total order value: {total:.2f}")
        
    data = extract()
    total = transform(data=data)
    load(total["total"])
    
test_dag()