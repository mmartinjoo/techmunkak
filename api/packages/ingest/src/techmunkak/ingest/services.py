from techmunkak.core.db import connection
from techmunkak.ingest import selectors
from techmunkak.ingest.models import ScrapeRun, ScrapeRunItem

def create_scrape_run(site_id: int, search_term_id: int):
    with connection() as conn:
        row = conn.execute("""
            insert into ops.scrape_runs(site_id, search_term_id)
            values (%s, %s)          
            returning id
        """, (site_id, search_term_id,)).fetchone()
        
        conn.commit()
        
        return selectors.find_scrape_run(id=row[0])
    
def update_discovered_count(scrape_run_id: int, discovered_count: int):
    with connection() as conn:
        conn.execute("""
            update ops.scrape_runs
            set 
                discovered_count = %s,
                status = %s
            where id = %s             
        """, (discovered_count, "discovered", scrape_run_id,))
        
        conn.commit()
        
def add_scrape_run_item(scrape_run_id: int, site_id: int, url: str, url_hash: str) -> ScrapeRunItem | None:
    with connection() as conn:
        row = conn.execute("""
            insert into ops.scrape_run_items(scrape_run_id, site_id, url, url_hash, last_fetched_at, status)
            values(%s, %s, %s, %s, now(), %s)
            on conflict (site_id, url_hash) do nothing
            returning id
        """, (
            scrape_run_id,
            site_id,
            url,
            url_hash,            
            'pending',
        )).fetchone()
        
        conn.commit()
        
        # URL already fetched
        if row is None:
            return None
        
        return selectors.find_scrape_run_item(id=row[0])
    
def mark_scrape_run_item(scrape_run_item_id: int, status: str, error: str | None = None):
    with connection() as conn:
        conn.execute("""
            update ops.scrape_run_items
            set 
                status = %s,
                error = %s
            where id = %s
        """, (status, error, scrape_run_item_id,))
        
        conn.commit()