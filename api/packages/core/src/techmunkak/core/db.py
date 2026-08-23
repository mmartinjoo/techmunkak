from contextlib import contextmanager
from functools import lru_cache
from typing import Generator

import psycopg
from psycopg_pool import ConnectionPool

from techmunkak.core.config import settings


# --- for batch jobs: ingest, migrate ------------------------------

@contextmanager
def connection() -> Generator[psycopg.Connection, None, None]:
    """One short-lived connection with an explicit transaction."""
    with psycopg.connect(
        str(settings.database_url),
        autocommit=False,
        options="-c statement_timeout=300000",
    ) as conn:
        yield conn


# --- for the API: a pool, created once, lazily ---------------------

@lru_cache(maxsize=1)
def pool() -> ConnectionPool:
    return ConnectionPool(
        str(settings.database_url),
        min_size=1,
        max_size=10,
        open=True,
    )
