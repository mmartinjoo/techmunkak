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

api:
	uv run api

migrate:
	uv run migrate

discover:
	uv run discover

fetch:
	uv run fetch

load:
	uv run load

transform:
	@$(DBT_ENV) && uv run dbt build

embed:
	uv run embed

refresh-exchange-rates:
	uv run refresh_exchange_rates

dbt-seed:
	@$(DBT_ENV) && uv run dbt seed