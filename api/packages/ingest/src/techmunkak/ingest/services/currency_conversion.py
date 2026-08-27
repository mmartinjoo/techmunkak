import requests
from datetime import datetime, timedelta
from techmunkak.core.db import pool

def refresh_exchange_rates():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    with pool().connection() as conn:
        rows = conn.execute("""
            select from_currency_code, to_currency_code
            from bronze.currency_conversions             
        """).fetchall()
        
        for row in rows:
            resp = requests.get(f"https://fxds-public-exchange-rates-api.oanda.com/cc-api/currencies?base={row[1]}&quote={row[0]}&data_type=chart&start_date={yesterday}&end_date={today}")
            resp.raise_for_status()
            data = resp.json()
            
            assert "response" in data, f"invalid format from exchange API: {data}"
            
            exchange_rates = resp.json()["response"]
            last_exchange_rate = exchange_rates[-1]
            value = last_exchange_rate["average_bid"]
            
            conn.execute("""
                update bronze.currency_conversions           
                set 
                    value = %s,
                    updated_at = now()
                where from_currency_code = %s
                and to_currency_code = %s
            """, (
                value,
                row[0],
                row[1],
            ))