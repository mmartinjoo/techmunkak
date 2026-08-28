import pendulum
from datetime import timedelta
from airflow.sdk import dag, task
from techmunkak.ingest.services import currency_conversion

@dag(
    dag_id="refresh_exchange_rates",
    start_date=pendulum.datetime(2026, 8, 28, tz="UTC"),
    catchup=False,
    schedule="@daily",
)
def refresh_exchange_rates():
    @task(retries=2, retry_delay=timedelta(minutes=15))
    def refresh():
        count = currency_conversion.refresh_exchange_rates()
        print(f"refreshed {count} currencies")
        return count
        
    refresh()
        
refresh_exchange_rates()