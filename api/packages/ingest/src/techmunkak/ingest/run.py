from techmunkak.ingest import runner
from techmunkak.ingest.services.currency_conversion import refresh_exchange_rates

def main():
    runner.run()
    
def run_refresh_exchange_rates():
    refresh_exchange_rates()