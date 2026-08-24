from techmunkak.ingest import selectors
from techmunkak.ingest import services
from techmunkak.ingest.scrapers import nofluffjobs
from techmunkak.ingest import storage

def run():
    next_site_search_terms = selectors.fetch_next_site_search_terms()
    for site_search_term in next_site_search_terms:
        if site_search_term.site.name != "NoFluffJobs":
            continue
        
        scrape_run = services.create_scrape_run(
            site_id=site_search_term.site.id,
            search_term_id=site_search_term.search_term.id,
        )
        
        pages = nofluffjobs.discover(site_search_term)
        for i, data in enumerate(pages):
            storage.put_listing_page(
                site="NoFluffJobs",
                search_term=site_search_term.search_term.term,
                data=data,
                page=i+1,
                scrape_run_id=scrape_run.id,
            )
            
            
            