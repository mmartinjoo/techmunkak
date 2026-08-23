up:
	docker compose -f docker-compose.yml up --remove-orphans

upairflow:
	docker compose -f docker-compose.airflow.yml up