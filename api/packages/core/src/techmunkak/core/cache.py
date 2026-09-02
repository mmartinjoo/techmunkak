import hashlib
import json
import logging
from datetime import date, datetime, timedelta

from techmunkak.core.db import pool
from techmunkak.core.json import EnhancedJSONEncoder

logger = logging.getLogger(__name__)

DEFAULT_TTL_MIN = 10

def key(**kwargs) -> str:
    return hashlib.sha1(
        json.dumps(kwargs, sort_keys=True, cls=EnhancedJSONEncoder).encode("utf-8")
    ).hexdigest()

def has(key: str) -> bool:
    with pool().connection() as conn:
        row = conn.execute("""
            select exists(
                select 1
                from ops.cache 
                where key = %s
            )            
        """, (key,)).fetchone()
        
        return row[0]
    
def get(key: str) -> dict | None:
    with pool().connection() as conn:
        row = conn.execute("""
            select value
            from ops.cache
            where key = %s             
            limit 1
        """, (key,)).fetchone()
        
        assert row is not None, f"cache returned None for {key}"
        
        if row is None:
            logger.warning(f"cache miss for key {key}")
            
        return row[0]
    
def set(key_sha1: str, value: any, expires_at: datetime | None = None):
    if len(key_sha1) != len(key(foo="foo")):
        logger.warning("set: key must be sha1")
        return
    
    if expires_at is None or expires_at <= datetime.now():
        expires_at_corrected = datetime.now() + timedelta(minutes=DEFAULT_TTL_MIN)
    else:
        expires_at_corrected = expires_at
    
    value_json = ""
    try:
        value_json = json.dumps(value, cls=EnhancedJSONEncoder)
    except Exception:
        logger.exception(f"set: unable to serialize value {value} for key {key_sha1}")
        return
    
    if value_json == "":
        logger.error(f"set: unable to serialize value {value} for key {key_sha1}")
        return
    
    with pool().connection() as conn:
        conn.execute("""
            insert into ops.cache(key, value, expires_at)
            values(%s, %s, %s)
            on conflict (key)
            do update set
                value = %s,
                expires_at = %s
        """, (
            key_sha1,
            value_json,
            expires_at_corrected,
            value_json,
            expires_at_corrected,
        ))
        
def evict():
    with pool().connection() as conn:
        ids = conn.execute("""
            delete from ops.cache
            where expires_at <= now()   
            returning old.id          
        """).fetchall()
        
        logger.info(f"{len(ids)} items are evicted from cache")