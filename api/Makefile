DBT_ENV := set -a && . ./.env && set +a && export DBT_PROFILES_DIR=transform DBT_PROJECT_DIR=transform

add:
	@if [ -z "$(pkg)" ]; then \
		echo "Usage: make add pkg=<package_name> dep=<dependency_name>"; \
		exit 1; \
	fi

	@if [ -z "$(dep)" ]; then \
		echo "Usage: make add pkg=<package_name> dep=<dependency_name>"; \
		exit 1; \
	fi
	uv add --package techmunkak-$(pkg) $(dep)

migrate:
	uv run migrate

ingest:
	uv run ingest

transform:
	@$(DBT_ENV) && uv run dbt build

embed:
	uv run embed

refresh-exchange-rates:
	uv run refresh_exchange_rates

dbt-build:
	@$(DBT_ENV) && uv run dbt build

dbt-deps: 
	@$(DBT_ENV) && uv run dbt deps