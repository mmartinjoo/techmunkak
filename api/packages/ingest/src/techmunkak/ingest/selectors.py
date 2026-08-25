from techmunkak.core.db import connection
from techmunkak.ingest.models import JobUrl, ScrapeRun, SearchTerm, SiteSearchTerm, Site, ScrapeRunItem

def fetch_next_site_search_terms() -> list[SiteSearchTerm]:
    results = []
    with connection() as conn:
        rows = conn.execute("""
            select                 
                s.id as site_id,
                st.id as search_term_id,                
                sst.id as site_search_term_id,
                sst.params,
                coalesce(
                    round(0.4 * date_part('day', age(now(), sst.last_run_at))::numeric, 2)
                    , 0
                ) + round(0.6 * (st.priority::numeric/10), 2) as importance_score
            from ops.site_search_terms as sst
            join ops.search_terms as st on st.id = sst.search_term_id
            join ops.sites as s on s.id = sst.site_id
            where 
                s.is_active = true
                and st.is_active = true
            order by importance_score desc          
        """).fetchall()
        
    for row in rows:
        site = find_site(id=row[0])
        search_term = find_search_term(id=row[1])
        site_search_term = SiteSearchTerm(
            id=row[2],
            params=row[3],
            importance_score=row[4],
            site=site,
            search_term=search_term,
        )
        results.append(site_search_term)
        
    return results
        
def find_search_term(id: int) -> SearchTerm:
    with connection() as conn:
        row = conn.execute("""
            select id, term, is_active, priority, created_at 
            from ops.search_terms 
            where id = %s
        """, (id,)).fetchone()
        
        return SearchTerm(
            id=row[0],
            term=row[1],
            is_active=row[2],
            priority=row[3],
            created_at=row[4],
        )
        
def find_site(id: int) -> Site:
    with connection() as conn:
        row = conn.execute("""
            select id, name, base_url, is_active, created_at 
            from ops.sites 
            where id = %s
        """, (id,)).fetchone()
        
        return Site(
            id=row[0],
            name=row[1],
            base_url=row[2],
            is_active=row[3],
            created_at=row[4],
        )
        
def find_scrape_run(id: int) -> ScrapeRun:
    with connection() as conn:
        row = conn.execute("""
            select id, site_id, search_term_id, started_at, finished_at, status, discovered_count 
            from ops.scrape_runs
            where id = %s
        """, (id,)).fetchone()
        
        return ScrapeRun(
            id=row[0],
            site=find_site(row[1]),
            search_term=find_search_term(row[2]),
            started_at=row[3],
            finished_at=row[4],
            status=row[5],
        )

def find_scrape_run_item(id: int) -> ScrapeRunItem:
    with connection() as conn:
        row = conn.execute("""
            select id, scrape_run_id, site_id, url, url_hash, first_seen_at, last_fetched_at, status
            from ops.scrape_run_items
            where id = %s
        """, (id,)).fetchone()
        
        scrape_run = find_scrape_run(id=row[1])
        site = find_site(id=row[2])
        
        return ScrapeRunItem(
            id=row[0],
            scrape_run=scrape_run,
            site=site,
            url=row[3],
            url_hash=row[4],
            first_seen_at=row[5],
            last_fetched_at=row[6],
            status=row[7],
        )
        
def find_job_url(id: int) -> JobUrl:
    with connection() as conn:
        row = conn.execute("""
            select id, scrape_run_id, site_id, url, url_hash, first_seen_at, last_fetched_at, status
            from bronze.job_urls
            where id = %s
        """, (id,)).fetchone()
        
        scrape_run = find_scrape_run(id=row[1])
        site = find_site(id=row[2])
        
        return JobUrl(
            id=row[0],
            scrape_run=scrape_run,
            site=site,
            url=row[3],
            url_hash=row[4],
            first_seen_at=row[5],
            last_fetched_at=row[6],
            status=row[7],
        )