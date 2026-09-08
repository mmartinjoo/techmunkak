# Techmunkak

Techmunkak is a job-market intelligence platform. It continuously discovers and scrapes software-job postings from [JustJoinIT](https://justjoin.it) and [NoFluffJobs](https://nofluffjobs.com), lands them in an append-only object store, transforms them through a **medallion** data architecture (`bronze → silver → gold`) with [dbt](https://www.getdbt.com/), enriches them with LLMs and neural networks (translation, main-skill extraction with NER, embeddings), and exposes analytics plus a CV/skill-gap matching service through a FastAPI + Vue application. The whole pipeline is orchestrated with Apache Airflow.

---

## Table of contents

1. [What it does](#what-it-does)
2. [High-level architecture](#high-level-architecture)
3. [Repository layout](#repository-layout)
4. [Technology stack](#technology-stack)
5. [Data architecture (medallion)](#data-architecture-medallion)
6. [Version & history management](#version--history-management)
7. [Airflow scheduling](#airflow-scheduling)
8. [Ingestion queue and process](#ingestion-queue-and-process)
9. [Enrichment queue and process](#enrichment-queue-and-process)
10. [End-to-end pipeline](#end-to-end-pipeline)
11. [Packages (uv workspace)](#packages-uv-workspace)
12. [API surface](#api-surface)
13. [Running & deploying](#running--deploying)
14. [Architecture decision records](#architecture-decision-records)

---

## What it does

- **Discovers** job URLs per `site × search term` using a priority/recency importance score.
- **Fetches** raw listing and detail JSON, stored verbatim in S3-compatible storage (MinIO).
- **Loads** raw payloads into an append-only Postgres landing zone.
- **Transforms** the raw payloads with dbt into a normalized star schema (facts + dimensions) and analytical marts.
- **Enriches** jobs with LLMs: translation to English, main-skill extraction (site-suggested + NLP-suggested), and vector embeddings in Chroma.
- **Trains** a custom spaCy NER model that recognizes skills in job text and CVs.
- **Serves** salary/skill analytics, **CV→job matching**, and **skill-gap analysis** through a REST API and a Vue 3 frontend.

---

## High-level architecture

```
                         ┌─────────────────────────────────────────────────────────────┐
                         │                        Apache Airflow 3.x                    │
                         │  scheduler · dag-processor · celery worker · triggerer       │
                         └───────────────┬───────────────────────────┬─────────────────┘
                                          │ schedules DAGs            │ schedules DAGs
                                          ▼                           ▼
   ┌────────────────────────┐   ┌──────────────────────────────────────────────────────┐
   │  JustJoinIT /          │   │  techmunkak packages (uv workspace)                   │
   │  NoFluffJobs           │   │  ingest → transform(dbt) → enrich → embed → models   │
   └───────────┬────────────┘   └───┬──────────────────┬───────────────┬───────────────┘
               │  HTTP (JSON)       │                  │               │
               ▼                    ▼                  ▼               ▼
        ┌──────────────┐   ┌───────────────┐   ┌────────────┐   ┌─────────────┐
        │  MinIO (S3)  │   │   Postgres    │   │   Chroma   │   │  FastAPI    │
        │ raw objects  │   │ bronze/silver │   │  vector    │   │  + Vue 3    │
        │  + models    │   │ /gold/ops     │   │  store     │   │  frontend   │
        └──────────────┘   └───────────────┘   └────────────┘   └─────────────┘
```

Two Docker Compose stacks share a common network (`techmunkak_shared`):

- **`docker-compose.yml`** — the application stack: `proxy` (Caddy), `frontend` (Vue/Vite), `api` (FastAPI), `migrate` (one-shot), `minio`, `postgres`, `chroma`.
- **`docker-compose.airflow.yml`** — the scheduling stack: `airflow-postgres`, `airflow-redis`, `airflow-apiserver`, `airflow-scheduler`, `airflow-dag-processor`, `airflow-worker`, `airflow-triggerer`, plus `flower`/`airflow-cli` behind Compose profiles.
- **`docker-compose.prod.yml`** — a small overlay that switches the frontend to its production build target.

---

## Repository layout

```
.
├── adr/                          # Architecture Decision Records
├── airflow/                      # Airflow image + config (airflow.cfg)
├── api/                          # Python monorepo (uv workspace)
│   ├── dags/                     # Airflow DAG definitions
│   │   ├── ingest/               #   discover, fetch, load, refresh_exchange_rates
│   │   ├── enrich/               #   enrich, train_skill_model
│   │   └── transform/            #   transform (dbt)
│   ├── db/migrations/            # Ordered, tracked SQL migrations (ops.schema_migrations)
│   ├── packages/                 # Individual Python packages (see below)
│   └── transform/                # dbt project (models, seeds, macros, tests)
├── deploy/                       # Caddyfile, nginx conf, deploy.sh, init_db.sql
├── frontend/                     # Vue 3 + Vite + TypeScript app
├── logs/                         # dbt logs
├── docker-compose.yml
├── docker-compose.airflow.yml
├── docker-compose.prod.yml
└── Makefile                      # up / upairflow targets
```

---

## Technology stack

| Layer              | Technology                                                                 |
| ------------------ | -------------------------------------------------------------------------- |
| Orchestration      | Apache Airflow 3.3.1 (CeleryExecutor, TaskFlow 3.x DAG API, assets)        |
| Ingestion          | Python `requests`, boto3 (S3 API), psycopg                                  |
| Object storage     | MinIO (S3-compatible)                                                       |
| Warehouse          | PostgreSQL 18 (app) / PostgreSQL 16 (Airflow metadata)                      |
| Transformation     | dbt-core 1.12 + dbt-postgres, `dbt_utils`, `dbt_expectations`               |
| Vector store       | ChromaDB (LangChain-Chroma integration)                                     |
| LLM/embeddings     | LangChain + Mistral (`mistral-embed`, translation & skill-gap models)       |
| NER                | spaCy (`en_core_web_sm` base, custom `SKILL` entity)                        |
| API                | FastAPI + Uvicorn                                                           |
| Frontend           | Vue 3, Vue Router, Vite, TypeScript                                         |
| Packaging / deps   | `uv` workspace, Python 3.12                                                  |
| Reverse proxy      | Caddy (local) / Nginx (production static frontend)                           |

---

## Data architecture (medallion)

Data flows through three analytical schemas plus an operational schema, all inside a single Postgres database (`techmunkak`), with raw object payloads mirrored to MinIO.

### The four schemas

| Layer  | Schema     | Contents                                                                    | Written by             |
| ------ | ---------- | --------------------------------------------------------------------------- | ---------------------- |
| Bronze | `bronze`   | Append-only landing zone: raw payloads, job URLs, currency conversions      | Ingestion packages     |
| Silver | `silver`   | Normalized, tested, conformed dimensions + facts                            | dbt (staging + inter.) |
| Gold   | `gold`     | Analytical marts (aggregations)                                             | dbt (marts)            |
| Ops    | `ops`      | Operational state: queues, sites, search terms, cache, migration ledger     | Ingestion & API        |

Schemas are created in `api/db/migrations/001_create_schemas.sql` (`bronze`, `silver`, `gold`, `ops`); `public` is dropped in migration `002`.

### Bronze — the landing zone

Bronze is **append-only**. Nothing is updated or deleted; every scrape of a job produces a *new* row, which is the foundation of the history model (see [Version & history management](#version--history-management)).

- **`bronze.raw_jobs`** — one row per fetched snapshot. Columns: `site_id`, `job_url_id`, `url`, `payload jsonb` (the verbatim site JSON), `fetched_at`, `created_at`.
- **`bronze.job_urls`** — discovered URLs with `url_hash = sha256(url)`, `first_seen_at`, `last_fetched_at`, `s3_key`.
- **`bronze.currency_conversions`** — a seed of `from → to` FX rates used to normalize salaries to EUR, refreshed daily from the OANDA fxds API.

The *raw object* counterpart lives in MinIO under:

```
<site>/<unix-ts>/search_terms/<term>/page-<n>.json   # listing pages
<site>/<unix-ts>/jobs/<url_hash>.json                # job detail pages
models/ner/<version>.tar.gz  +  models/ner/current.json   # versioned NER models
CVs/<slug>.pdf                                        # uploaded CVs
```

### Silver — conformed views & tables (dbt)

Silver is produced by dbt and is organized in two model folders:

**Staging (`models/staging`)** — source-specific views that parse the JSON `payload` into typed columns.

- `stg_justjoinit__jobs` — `external_id`, `title`, `body`, salary/employment types, skills, country, seniority.
- `stg_nofluffjobs__jobs` — `external_id`, `title`, daily tasks, category, seniority, salary types (`b2b`/`permanent`), regions, musts/nices, `basics.technology`.

Both select from the dbt `bronze` source (`raw_jobs`), joined to `ops.sites` to isolate the correct site.

**Intermediate (`models/intermediate`)** — the conformed star schema and business logic.

- `int_job_versions` — deduplication + version assignment per `external_id` (history).
- `int_jobs` — the "latest" (version = 1) rows, with salary normalized to EUR and monthly.
- `int_accepted_jobs` / `int_rejected_jobs` — quality gate split on salary completeness/ranges, `currency_code = 'EUR'`, `salary_period = 'month'`.
- Dimensions — `dim_company`, `dim_country`, `dim_contract_type`, `dim_seniority`, `dim_skill` (surrogate keys via `md5(...)`).
- `fact_job` — the accepted-jobs fact table, keyed by `job_key`, referencing all dimension keys.
- `job_skills` — bridge table between `fact_job` and `dim_skill` with a `required` boolean.
- `int_skill_candidates` — deduplicated skill names (slugged) before dimension resolution.
- `int_enriched_jobs` — joins `fact_job` to `ops.enrichment_results` (English title/description, main skill, Chroma IDs).

**Materialization** (from `dbt_project.yml`):

```yaml
staging:      +materialized: view  +schema: silver
intermediate: +materialized: view  +schema: silver
marts:        +materialized: table +schema: gold
```

Individual intermediate models override to tables where they are queried repeatedly: `dim_*`, `fact_job`, `job_skills`, `int_enriched_jobs`.

### Gold — analytical marts

Four aggregate tables (materialized as tables) in the `gold` schema:

- `most_popular_main_skills_by_month` — top main skills by job count, per month.
- `top_paying_main_skills_by_month` — top main skills by median salary, per month.
- `most_popular_skills_by_month` — top skills (from `job_skills`) by job count, per month.
- `top_paying_skills_by_month` — top skills by median salary, per month.

Ranking is controlled by dbt vars (`top_skills_limit`, `min_coccurrence_to_be_top_kill`, salary range filters).

### Seeds & canonical mappings

dbt `seeds/` are loaded into `silver` and drive entity canonicalization:

- `contract_type_aliases.csv`, `country_aliases.csv`, `seniority_aliases.csv`, `skill_aliases.csv` — raw → canonical name mappings.
- `blacklisted_skills.csv` — skills excluded from `dim_skill`/`job_skills` (e.g. generic words like "operations", "testing").

### Data quality

dbt models are guarded by `dbt_utils` + `dbt_expectations` tests plus a custom `not_empty` generic test:

- `not_null`, `not_empty`, `unique`, `accepted_values`, `accepted_range`, `relationships`, `unique_combination_of_columns`.
- Source **freshness** on `bronze.raw_jobs` (`warn_after` / `error_after` = 2 days) so stale ingestion surfaces as a test failure.
- Declarative `constraints` (unique keys) on `int_job_versions`, `int_jobs`, `fact_job`, `int_enriched_jobs`.

---

## Version & history management

History is preserved through **append-only ingestion** plus **reconstruction at transform time** rather than in-place updates.

### 1. Append-only bronze

`bronze.raw_jobs` is never mutated after insert. Each fetch of a job inserts a new row (with its own `fetched_at` and `bronze_id`). This means the complete time-series of every job listing is retained and can be reconstructed at any later point.

### 2. URL lifecycle tracking

`bronze.job_urls` records `first_seen_at` and `last_fetched_at` for each discovered URL (deduplicated by `site_id × url_hash`). The operational queue (`ops.ingestion_queue`) tracks the fetch/load lifecycle per URL without mutating history: `waiting_for_fetch → fetch_in_progress → waiting_for_load → load_in_progress → finished` (plus `fetch_failed`/`load_failed`/`not_found` with retry backoff).

### 3. Version assignment in `int_job_versions`

dbt assigns a monotonically ordered version number to every snapshot of a given job:

```sql
row_number() over (
    partition by external_id
    order by fetched_at desc, bronze_id desc
) as version
```

- `version = 1` is the **latest** snapshot.
- `int_jobs` filters `version = 1` to expose only current data to the rest of the model graph.
- The model enforces `unique(job_key, version)`, so a job can appear once per version — i.e. a full history is available for point-in-time reconstruction.

> `snapshot-paths` is configured in `dbt_project.yml`, but the project uses this window-function approach instead of dbt snapshots for job history.

### 4. The job grain (`job_key`)

Per ADR [`grain.md`](adr/grain.md), `job_key` encodes the **external ID + contract type**:

```sql
md5(concat_ws('||', external_id, contract_type))
```

This is because the same posting is often advertised both as a contractor (`b2b`) and a full-time (`permanent`) role — each is treated as a distinct fact row. Jobs advertised in multiple countries are grouped into one `job_key`.

### 5. Structural versioning — schema migrations

Database structure is versioned with ordered, idempotently-tracked SQL migrations in `api/db/migrations/`:

- Applied in filename order by the `migrate` console script (`techmunkak.core.migrate`).
- The ledger `ops.schema_migrations(filename, applied_at)` records what has run, so only new files execute.
- Migrations are linear and cumulative (e.g. `015_create_raw_jobs.sql` → `017_add_url_to_raw_jobs.sql` → `021_add_fetched_at_to_raw_jobs.sql`), capturing the schema's evolution.

### 6. Model versioning in object storage

The trained NER model is versioned in MinIO (`storage.put_ner_model` / `get_ner_model`):

- Each training run writes `models/ner/v<YYYYMMDD>-<HHMMSS>.tar.gz`.
- `models/ner/current.json` is a pointer (`{"version": ...}`) to the active version, giving atomic model promotion and rollback.

---

## Airflow scheduling

Airflow 3.3.1 runs on **CeleryExecutor** with a dedicated PostgreSQL metadata DB and Redis broker. It shares the `techmunkak_shared` external network so workers can reach the app Postgres, MinIO, and Chroma.

### Cluster components

| Service              | Role                                             |
| -------------------- | ------------------------------------------------ |
| `airflow-postgres`   | Airflow metadata database (PostgreSQL 16)        |
| `airflow-redis`      | Celery broker / result backend transport         |
| `airflow-apiserver`  | Airflow 3.x API server (execution API endpoint)  |
| `airflow-scheduler`  | Schedules DAG runs                               |
| `airflow-dag-processor` | Parses and processes DAG files               |
| `airflow-worker`     | Executes Celery tasks                            |
| `airflow-triggerer`  | Runs deferrable/triggered tasks                  |
| `flower` (profile)   | Celery monitoring UI                             |
| `airflow-cli` (profile) | Debug shell                                   |

Key config (`docker-compose.airflow.yml`):

```yaml
AIRFLOW__CORE__DAGS_FOLDER: /opt/techmunkak/dags
AIRFLOW__CORE__EXECUTOR: CeleryExecutor
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
```

The Airflow image (`airflow/Dockerfile`) installs every `techmunkak-*` package editable, plus `dbt-core`/`dbt-postgres` and the spaCy model, so DAG tasks can call package functions directly and run `dbt` via BashOperator.

### The DAGs

DAGs live in `api/dags/` and are written with the TaskFlow 3.x `airflow.sdk` API (`@dag` / `@task` / `@task_group`).

| DAG                    | Trigger                        | What it runs                                                                 |
| ---------------------- | ------------------------------ | ---------------------------------------------------------------------------- |
| `discover`             | `timedelta(60 min)`¹           | `select()` ranks site×term rows by importance score, then a task group expands over the top 5 to run `run.discover_one` per row. |
| `fetch`                | `timedelta(3 min)`¹            | `run.fetch()` → `fetch_stage()` — pulls job detail JSON into MinIO.          |
| `load`                 | `timedelta(1 min)`¹            | `run.load()` → `load_stage()` — reads MinIO and inserts `bronze.raw_jobs`.   |
| `refresh_exchange_rates` | `@daily` (retries=2)         | `currency_conversion.refresh_exchange_rates()` against OANDA fxds API.       |
| `transform`            | cron `0 2 * * *`               | `dbt deps → seed → run → test` via BashOperator; emits `Asset("x-fact-job://ready")`. |
| `enrich`               | `Asset("x-fact-job://ready")`  | `enqueue → translate → main_skill_extraction → embed`; emits `Asset("x-enrichment-results://ready")`. |
| `train_skill_model`    | `Asset("x-enrichment-results://ready")` | `run.train()` — retrains the spaCy NER model (start date in the future → effectively manual/paused). |

¹ The interval is read from `settings.scheduler_*_schedule_minutes` (environment variables `SCHEDULER_DISCOVER_SCHEDULE_MINUTES`, `SCHEDULER_FETCH_SCHEDULE_MINUTES`, `SCHEDULER_LOAD_SCHEDULE_MINUTES`).

### Asset-driven flow

The enrichment and training DAGs use Airflow **assets** to express dependencies across DAGs without hard-coding schedules:

```
transform ──(x-fact-job://ready)──▶ enrich ──(x-enrichment-results://ready)──▶ train_skill_model
```

- `transform`'s `dbt_run` task declares `outlets=[Asset("x-fact-job://ready")]`.
- `enrich` is scheduled on that asset, and its `embed` task declares `outlets=[Asset("x-enrichment-results://ready")]`.
- `train_skill_model` is scheduled on the enrichment asset.

### Retry / backoff

Tasks use bounded retries with backoff:

- `enrich` translation/main-skill/embed tasks: `retries=3` (3–15 min delays).
- `refresh_exchange_rates`: `retries=2` (15 min delay).
- Queue-level retries are additionally capped inside the packages (`attempts <= 5` for ingestion, `<= 12` for enrichment) with a `next_attempt_at` backoff of ~5 hours on failure.

---

## Ingestion queue and process

The ingestion layer turns job postings into `bronze.raw_jobs` rows. It runs as a **three-stage pipeline** — **discover** (find URLs), **fetch** (download the raw JSON), **load** (persist to Postgres) — with the fetch/load work tracked in an operational queue so it is idempotent, resumable, and safe across concurrent workers.

### Overview

Three Airflow DAGs drive ingestion:

```
discover (60 min) → fetch (3 min) → load (1 min)
```

- **Discover** walks the site's search-result pages, extracts job URLs, creates `bronze.job_urls` rows, and *enqueues* each URL.
- **Fetch** and **Load** are pull-based stages that drain the queue: fetch downloads the detail JSON into MinIO; load reads it back and inserts a `bronze.raw_jobs` row.

The queue decouples discovery from the slower fetch/load work, so discovery can enqueue a burst of URLs and the worker DAGs chew through them at their own cadence.

### Three tables

**`bronze.job_urls`** — the discovered-job register, one row per URL.

| Column                        | Purpose                                        |
| ----------------------------- | ---------------------------------------------- |
| `id`                          | surrogate key referenced by the queue and raw jobs |
| `site_id`                     | FK to `ops.sites`                              |
| `url`                         | the job detail URL                             |
| `url_hash`                    | `sha256(url)` identity key                     |
| `first_seen_at` / `last_fetched_at` | lifecycle timestamps                    |
| `s3_key`                      | MinIO key of the fetched detail JSON           |

**`ops.ingestion_queue`** — the fetch/load state machine, one row per enqueued `job_url_id`.

| Column                        | Purpose                                                             |
| ----------------------------- | ------------------------------------------------------------------- |
| `job_url_id`                  | FK to `bronze.job_urls`                                             |
| `attempts`                    | retry counter for the current stage (dequeue gate: `attempts <= 5`) |
| `next_attempt_at`             | backoff gate; rows are only dequeued once this is in the past       |
| `fetched` / `loaded`          | boolean stage-completion flags                                      |
| `status`                      | current state in the state machine                                  |
| `error`                       | last failure's traceback                                            |
| `discovered_at`, `created_at`, `fetched_at`, `loaded_at` | timestamps                          |

**`bronze.raw_jobs`** — the append-only landing rows produced by the load stage.

| Column                        | Purpose                                            |
| ----------------------------- | -------------------------------------------------- |
| `id`                          | surrogate key (`bronze_id`) referenced by dbt staging |
| `site_id`                     | FK to `ops.sites`                                  |
| `job_url_id`                  | FK to `bronze.job_urls`                            |
| `url`                         | job URL                                            |
| `payload jsonb`               | verbatim site JSON                                 |
| `fetched_at` / `created_at`   | timestamps                                         |

### State machine

`ops.ingestion_queue.status` progresses through:

```
            discover_stage() → enqueue()
                      │
                      ▼
        ┌───────────────────────────┐
        │ waiting_for_fetch         │
        └───────────────┬───────────┘
                        │ fetch_stage()
                        ▼
        fetch_in_progress ──(404)──▶ fetch_failed (error = 'not_found', no retry)
                │
                │ (success)                      ┌──(other error)──▶ fetch_failed (5h backoff)
                ▼                               │
        ┌───────────────────────────┐           │
        │ waiting_for_load          │           │
        └───────────────┬───────────┘           │
                        │ load_stage()          │
                        ▼                       │
        load_in_progress ──(failure)──▶ load_failed (5h backoff)
                │
                │ (success)
                ▼
            finished
```

- `fetch_failed` rows re-enter the fetch queue after the backoff — except `not_found` rows, whose `next_attempt_at` is `NULL` and are therefore permanently excluded.
- `load_failed` rows re-enter the load queue after the backoff.

### Stage 1 — Discover (`discover_stage`)

Per site×search-term, `discover_one`:

1. resolves the scraper from the site name,
2. paginates the search results (`max_pages=10`, `per_page_limit=30`) and saves each raw page to MinIO,
3. parses and dedupes job URLs from the pages,
4. for each URL: creates a `bronze.job_urls` row (`tracking.create_job_url`) and enqueues it (`ingestion_queue.enqueue`),
5. records `last_run_at` on the site×search-term row (which drives the importance score).

The dedupe step is site-specific:

- **NoFluffJobs** — groups near-identical URLs with Levenshtein similarity (`ratio > 0.8`) because the same posting is returned once per region, then picks the "root" URL prefix that best represents the group.
- **JustJoinIT** — a no-op (URLs are already unique per posting).

Deduplication happens at the scraper level within a single discovery run; `create_job_url` is a plain INSERT with no database-level uniqueness guard.

### Stage 2 — Fetch (`fetch_stage`)

`dequeue_for_fetching(limit=25)` selects up to 25 rows where `fetched = false`, `status in ('waiting_for_fetch', 'fetch_failed')`, `attempts <= 5`, and `next_attempt_at <= now()`, ordered oldest-first with `FOR UPDATE SKIP LOCKED`.

For each dequeued URL:

1. `mark_fetch_in_progress` (status → `fetch_in_progress`, `attempts += 1`),
2. `scraper.fetch_job_details(url)` downloads the JSON,
3. `storage.put_job_details_page(...)` writes it to MinIO under `{site}/{ts}/jobs/{url_hash}.json`,
4. `tracking.update_job_url_s3_key(...)` records the key on `bronze.job_urls`,
5. `mark_fetch_finished` (status → `waiting_for_load`, `fetched_at = now()`).

Failure handling: a `404` is terminal (marked not-found with `next_attempt_at = NULL`); any other exception records the traceback and backs off 5 hours (`mark_fetch_failed`) for retry.

### Stage 3 — Load (`load_stage`)

`dequeue_for_loading(limit=25)` selects up to 25 rows where `fetched = true`, `loaded = false`, `status in ('waiting_for_load', 'load_failed')`, `attempts <= 5`, and `next_attempt_at <= now()`.

For each dequeued URL:

1. `mark_load_in_progress` (status → `load_in_progress`, `attempts += 1`),
2. `storage.get_job_details_page(s3_key)` reads the JSON back from MinIO,
3. `create_raw_job(...)` inserts a new `bronze.raw_jobs` row (append-only),
4. `mark_load_finished` (status → `finished`, `loaded_at = now()`).

On failure, `mark_load_failed` records the traceback and backs off 5 hours.

### Concurrency, retries, and idempotency

- **Bounded batches** — fetch and load each drain at most 25 rows per DAG run, so a burst of discoveries is processed incrementally across runs.
- **`FOR UPDATE SKIP LOCKED`** — safe multi-worker dequeuing without double processing.
- **Retry caps + backoff** — `attempts <= 5` per row, with `next_attempt_at = now() + 5 hours` on failure (terminal no-retry for `404`).
- **Append-only target** — the load stage only ever inserts into `bronze.raw_jobs`; it never updates or deletes, which is what makes the downstream history model possible.
- **MinIO as the handoff** — fetch and load are decoupled through object storage: fetch writes the JSON, load reads it back; the `s3_key` on `bronze.job_urls` links the two.

### Relationship to the rest of the pipeline

- Discover is the entry point; `ops.ingestion_queue` is then drained by fetch → load.
- Each completed load inserts a `bronze.raw_jobs` row, which dbt staging (`stg_*__jobs`) parses on the next `transform` run.
- The `enrich` DAG starts a *separate* queue (`ops.enrichment_queue`) only after dbt has materialized `silver.fact_job` (see [Enrichment queue and process](#enrichment-queue-and-process)).

---

## Enrichment queue and process

The enrichment layer takes the normalized `silver.fact_job` rows produced by dbt and runs them through three sequential stages — **translation**, **main-skill extraction**, and **embedding** — persisting progress in an operational queue so the work is idempotent, resumable, and safe across concurrent workers.

### Overview

Enrichment is driven by the `enrich` DAG (triggered by the `x-fact-job://ready` asset that `transform` emits). A single DAG run executes four tasks in order:

```
enqueue → translate → main_skill_extraction → embed
```

The process is **pull-based and queue-driven**: each stage selects a bounded batch of eligible `job_key`s, marks them in progress, does the work, and advances them to the next status. Partial progress is committed after each stage, so a crash mid-DAG never loses completed work.

### Two tables

**`ops.enrichment_queue`** — one row per job that has entered (or is waiting to enter) enrichment. It is the state machine.

| Column                     | Purpose                                                              |
| -------------------------- | -------------------------------------------------------------------- |
| `job_key`                  | unique grain key from `fact_job`                                     |
| `attempts`                 | retry counter for the current stage (dequeue gate: `attempts <= 12`) |
| `next_attempt_at`          | backoff gate; rows are only dequeued once this is in the past        |
| `need_translation`         | whether the raw text is non-English (per-site heuristic)             |
| `translated`               | boolean flag: translation stage done                                 |
| `main_skill_extracted`     | boolean flag: main-skill stage done                                  |
| `embedded`                 | boolean flag: embedding stage done                                   |
| `status`                   | current state in the state machine (see below)                       |
| `error`                    | last failure's traceback                                             |
| `created_at`, `translated_at`, `main_skill_extracted_at`, `embedded_at` | timestamps                                   |

**`ops.enrichment_results`** — one row per job holding the *outputs* of enrichment. This is what `silver.int_enriched_jobs` reads.

| Column                      | Purpose                                                  |
| --------------------------- | -------------------------------------------------------- |
| `job_key`                   | unique, matches `fact_job.job_key`                       |
| `title_en`, `description_en`| English translation (or original when already English)   |
| `main_skill_site_suggested` | main skill taken from the site's own metadata            |
| `main_skill_nlp_suggested`  | main skill from the spaCy NER model                      |
| `chroma_embedding_ids`      | Chroma document IDs for the embedded chunks              |
| `ready`                     | flips `true` once all outputs are populated              |

### State machine

`ops.enrichment_queue.status` progresses through:

```
                 enqueue_next_batch()
                         │
                         ▼
        ┌───────────────────────────────────┐
        │ waiting_for_translation           │   (need_translation = true)
        └───────────────┬───────────────────┘
                        │ translation_stage()
                        ▼
        translation_in_progress ──(failure)──▶ translation_failed
                        │                           │
                        │ (success)                 │ (5h backoff, retry)
                        ▼                           ▼
        ┌───────────────────────────────────┐   (re-enters queue)
        │ waiting_for_main_skill_extraction │
        └───────────────┬───────────────────┘
                        │ main_skill_extraction_stage()
                        ▼
   main_skill_extraction_in_progress ──(failure)──▶ main_skill_extraction_failed
                        │
                        │ (success)
                        ▼
        ┌───────────────────────────────────┐
        │ waiting_for_embedding             │
        └───────────────┬───────────────────┘
                        │ embedding_stage()
                        ▼
        embedding_in_progress ──(failure)──▶ embedding_failed
                        │
                        │ (success)
                        ▼
                     finished
```

If `need_translation = false` (already-English jobs), the row is enqueued directly at `waiting_for_main_skill_extraction`, skipping translation.

### Stage 1 — Enqueue (`enqueue_stage`)

`enrichment_queue.enqueue_next_batch()` finds jobs that exist in `fact_job` but have **no** row in either `enrichment_queue` or `enrichment_results`:

```sql
select jobs.job_key, sites.name, jobs.title, jobs.description
from silver.fact_job as jobs
left join ops.enrichment_queue as queue on queue.job_key = jobs.job_key
join bronze.raw_jobs as raw_jobs on raw_jobs.id = jobs.bronze_id
join ops.sites as sites on sites.id = raw_jobs.site_id
left join ops.enrichment_results as enrichment on enrichment.job_key = jobs.job_key
where enrichment.job_key is null
and queue.job_key is null
```

For each candidate it:

1. resolves the site-specific translator to determine `need_translation`,
2. inserts the `enrichment_queue` row with the correct initial status (`waiting_for_translation` or `waiting_for_main_skill_extraction`),
3. inserts an `enrichment_results` row **seeded with the original (untranslated) title/description** — so an already-English job still has values to fall back on.

### Stage 2 — Translation (`translation_stage`)

`dequeue_for_translation(limit=5)` pulls up to 5 rows where `need_translation = true`, `translated = false`, `attempts <= 12`, `next_attempt_at < now()`, and `status in ('waiting_for_translation', 'translation_failed')`, ordered oldest-first with `FOR UPDATE SKIP LOCKED` so concurrent workers don't double-pick.

The per-site translation strategy:

- **NoFluffJobs** — `need_translation` inspects the raw payload's `metadata.sectionLanguages` (`daily-tasks`, `description`, `requirements.description`); anything not `en` needs translation.
- **JustJoinIT** — `need_translation` runs `langdetect` over `payload.body`.

Both then read the title/description from `silver.fact_job` and translate via a Mistral LLM (`ministral-14b-2512`) returning structured output (`translated_text`, `source_language`). The result is written back to `enrichment_results.title_en`/`description_en`, and the queue row advances to `waiting_for_main_skill_extraction`.

### Stage 3 — Main-skill extraction (`main_skill_extraction_stage`)

`dequeue_for_main_skill_extraction(limit=25)` selects rows at `waiting_for_main_skill_extraction` / `main_skill_extraction_failed` with `main_skill_extracted = false`. Each site contributes a **site-suggested** skill and, for JustJoinIT, an **NLP-suggested** skill:

- **NoFluffJobs** — `site_suggested = payload.basics.technology`; no NLP fallback.
- **JustJoinIT** — `site_suggested = payload.category.key`; `nlp_suggested` runs the trained spaCy NER `SKILL` model over the English title, falling back to the job's first `dim_skill`.

The result is written to `enrichment_results.main_skill_site_suggested` / `main_skill_nlp_suggested`, and the row advances to `waiting_for_embedding`.

### Stage 4 — Embedding (`embedding_stage`)

`dequeue_for_embedding(limit=25)` selects rows at `waiting_for_embedding` / `embedding_failed`. For each, it builds the embedding content as `title_en || ' ' || description_en`, then:

- chunks it with `RecursiveCharacterTextSplitter` (`chunk_size=1000`, `chunk_overlap=50`),
- embeds via Mistral `mistral-embed`,
- stores the chunks in the Chroma `jobs` collection with `metadata = {job_key}`,
- writes the returned Chroma IDs to `enrichment_results.chroma_embedding_ids`,
- marks the queue row `finished`.

### The `ready` flag

`enrichment_results._mark_finished` is called after each output write, but only flips `ready = true` when **all** outputs are present:

```sql
update ops.enrichment_results
set ready = true
where job_key = %s
and title_en is not null
and description_en is not null
and chroma_embedding_ids is not null
and (main_skill_site_suggested is not null or main_skill_nlp_suggested is not null)
```

`ready` is the single contract between the enrichment layer and the warehouse: `silver.int_enriched_jobs` joins `fact_job` to `enrichment_results` with `where enrichment.ready = true`, so only fully enriched jobs reach downstream marts, CV matching, and the skill-gap analyzer.

### Concurrency, retries, and idempotency

- **Bounded batches** — each stage dequeues a fixed-size batch (translation `limit=5`, others `limit=25`), so a single DAG run processes at most `limit` jobs per stage; the queue is drained over successive runs.
- **`FOR UPDATE SKIP LOCKED`** — safe multi-worker dequeuing without double processing.
- **Retry caps + backoff** — `attempts <= 12` per row, with `next_attempt_at = now() + 5 hours` on failure; the DAG additionally sets task-level `retries=3` with 3–15 minute delays.
- **Resumability** — each stage commits its own progress (`translated_at`, `main_skill_extracted_at`, `embedded_at`, status), so a failure in one stage leaves earlier stages' work intact and only failed rows re-enter the queue.

---

## End-to-end pipeline

1. **Discover** (`discover` DAG) — for the top site×search-term rows by importance score, call the site scraper, save listing pages to MinIO, parse job URLs, create `bronze.job_urls`, and enqueue them.
2. **Fetch** (`fetch` DAG) — dequeue up to 25 URLs (`FOR UPDATE SKIP LOCKED`), download detail JSON, store in MinIO, record the S3 key.
3. **Load** (`load` DAG) — read the detail JSON from MinIO and insert a new `bronze.raw_jobs` row.
4. **Transform** (`transform` DAG) — dbt rebuilds silver/gold: parse payloads → dedupe/version → normalize salaries to EUR/monthly → split accepted/rejected → build dims/fact/bridge → aggregate marts, then runs tests.
5. **Enrich** (`enrich` DAG, triggered by the fact asset) — enqueue new `job_key`s; translate non-English text to English; extract the main skill (site metadata + spaCy NER); embed the English title+description into Chroma.
6. **Train skill model** (`train_skill_model` DAG) — retrain the spaCy NER `SKILL` recognizer from `dim_skill` + `int_enriched_jobs`, then publish a new versioned model to MinIO.
7. **Serve** — FastAPI reads `gold` marts (popular/top-paying skills) and `silver` (leaderboard, jobs); CV matching uses Chroma embeddings + the NER model + Levenshtein; skill-gap analysis uses an LLM with structured output.

### Discovery importance score

Per ADR [`choose-scraping-priority.md`](adr/choose-scraping-priority.md), the next site×term to scrape is chosen by:

```
importance_score = 0.6 * (priority / 10) + 0.4 * days_since_last_run
```

`priority` (0–100) is weighted at 60% and elapsed-time-since-last-run at 40%, balancing high-priority keywords against starvation of lower-priority ones.

---

## Packages (uv workspace)

The Python monorepo (`api/`) is a `uv` workspace with one package per bounded concern:

| Package                      | Purpose                                                                                   |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| `techmunkak-core`            | Config (pydantic-settings), DB connection pool (psycopg), S3/MinIO storage, schema migrator, TTL cache, logging, string/JSON helpers. |
| `techmunkak-ingest`          | Scrapers (`justjoinit`, `nofluffjobs`), discover/fetch/load stages, ingestion queue, tracking, currency refresh. |
| `techmunkak-enrich`          | Enqueue/translate/main-skill/embedding stages, enrichment queue & results, per-site translation + main-skill extractors. |
| `techmunkak-embeddings`      | Mistral embedder, Chroma vector store, recursive text chunking.                           |
| `techmunkak-skill-model`     | spaCy NER training (PhraseMatcher-seeded, overlap-rejecting) + inference + versioned S3 model loader. |
| `techmunkak-cv-match`        | PDF parsing (pypdf), embedding-based matching, NER + Levenshtein matching.                 |
| `techmunkak-skill-gap-analysis` | LLM structured-output skill-gap report between a CV and similar jobs.                 |
| `techmunkak-api`             | FastAPI application and endpoints.                                                        |

Console scripts (`[project.scripts]`): `api`, `migrate`, `discover`, `fetch`, `load`, `refresh_exchange_rates`, `embed`, `enrich`, `train` — these are what the `api/Makefile` targets (`make api`, `make migrate`, `make discover`, …) wrap.

---

## API surface

Exposed by `techmunkak.api.run` (FastAPI) and reverse-proxied by Caddy under `/api*`.

| Method | Path                        | Description                                                    |
| ------ | --------------------------- | -------------------------------------------------------------- |
| GET    | `/api/ping`                 | Health check                                                   |
| GET    | `/api/leaderboard`          | Median salary + count for a month, filterable by skill/country/seniority (cached 1h) |
| GET    | `/api/most-popular-main-skills`  | Popular main skills between two months (gold mart)        |
| GET    | `/api/most-popular-skills`       | Popular skills between two months (gold mart)             |
| GET    | `/api/top-paying-main-skills`    | Top-paying main skills between two months (gold mart)     |
| GET    | `/api/top-paying-skills`         | Top-paying skills between two months (gold mart)          |
| POST   | `/api/match-cv`             | Upload a PDF CV → returns matching jobs (embedding + NER union) |
| POST   | `/api/skill-gap-analysis`   | Upload a PDF CV + `target_role` → structured skill-gap report |

---

## Running & deploying

Local (app stack):

```sh
make up          # docker compose -f docker-compose.yml up
```

Local (Airflow):

```sh
make upairflow   # docker compose -f docker-compose.airflow.yml up
```

One-off dbt / package tasks (inside `api/`):

```sh
make migrate                 # apply schema migrations
make transform               # dbt build (deps/seed/run/test)
make discover|fetch|load     # individual ingestion stages
make embed                   # embeddings entrypoint
```

Production deploy is driven by `deploy/deploy.sh`: `rsync` the tree to the remote host, then `docker compose up -d --build` for both the app stack (`docker-compose.yml` + `docker-compose.prod.yml`) and the Airflow stack.

Configuration is centralized in `.env` (see `.env` for DB/S3/Chroma/LLM credentials, ports, and scheduler cadences).

---

## Architecture decision records

- [`adr/choose-scraping-priority.md`](adr/choose-scraping-priority.md) — how site/keyword scrape order is prioritized (importance score).
- [`adr/grain.md`](adr/grain.md) — the `job_key` grain (external ID + contract type) and why multi-country postings collapse into one job.
