DBT_ENV := set -a && . ./.env && set +a && export DBT_PROFILES_DIR=transform DBT_PROJECT_DIR=transform

migrate:
	uv run migrate

ingest:
	uv run ingest

refresh-exchang-rates:
	uv run refresh_exchange_rates

dbt-build:
	@$(DBT_ENV) && uv run dbt build

dbt-deps: 
	@$(DBT_ENV) && uv run dbt deps