DBT_ENV := set -a && . ./.env && set +a && export DBT_PROFILES_DIR=transform DBT_PROJECT_DIR=transform

migrate:
	uv run migrate

dbt-run:
	@$(DBT_ENV) && uv run dbt run

dbt-deps: 
	@$(DBT_ENV) && uv run dbt deps