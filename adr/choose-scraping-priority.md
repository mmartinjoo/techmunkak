## Choosing the order of scraping keywords and sites

The problem: many job sites, dozens of keywords to scrape. What sites or keywords take precedence over others when rate limits are given?

I went with a simple importance score that is unique for each keyword. 

It takes two facts into consideration:
- Priority: `0..100` value assigned to each keyword by me
- ET: elapsed time since last scrape

Priority takes `60%` weight while ET takes `40%`.

The `importance_score` is a simple weight:
```sql
coalesce(
    round(0.4 * date_part('day', age(now(), sst.last_run_at))::numeric, 2)
    , 0
) + round(0.6 * (st.priority::numeric/10), 2) as importance_score
```

Priority is scaled down to `0..10` because ET realistically would be in ranges like `0..14`

This gives a balanced importance score (IS) for values such as these:

|ET  |PRIO |IS  |
|----|-----|----|
|12  |8    |9.60|
|7   |10   |8.80|
|15  |4    |8.40|
|5   |8    |6.80|

It prefers keywords with the highest priority scores but doesn't abandon lower priority keywords with high ET either. 

Sites are not prioritized. All of them is equal until proven otherwise.

2026-08-24