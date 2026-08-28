from techmunkak.ingest import runner
from techmunkak.ingest.services.currency_conversion import refresh_exchange_rates

def main():
    print("ingesting...")
    (finished, failed) = runner.run()
    print(f"ingestion done: {finished} new jobs, {failed} failed")
    
def run_refresh_exchange_rates():
    print("refreshing exchange rates")
    count = refresh_exchange_rates()
    print(f"refreshing done: {count} refreshed")