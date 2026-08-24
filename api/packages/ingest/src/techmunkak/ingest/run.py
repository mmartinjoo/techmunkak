from techmunkak.ingest import selectors

def main():
    next = selectors.fetch_next_site_search_terms()
    print(next)