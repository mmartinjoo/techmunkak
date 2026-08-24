from techmunkak.ingest import selectors
from techmunkak.ingest.scrapers import nofluffjobs
from techmunkak.ingest import storage

def run():
    next_site_search_terms = selectors.fetch_next_site_search_terms()
    for site_search_term in next_site_search_terms:
        if site_search_term.site.name != "NoFluffJobs":
            continue
        
        pages = nofluffjobs.discover(site_search_term)
        storage.put_listing_pages(
            site="NoFluffJobs",
            search_term=site_search_term.search_term.term,
            pages=pages,
            run_id=1,
        )