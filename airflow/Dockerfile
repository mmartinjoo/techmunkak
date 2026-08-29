FROM apache/airflow:3.3.1

USER airflow
COPY --chown=airflow:root ./api  /opt/techmunkak

RUN pip install --no-cache-dir -e /opt/techmunkak/packages/core && \
    pip install --no-cache-dir -e /opt/techmunkak/packages/ingest && \
    pip install --no-cache-dir -e /opt/techmunkak/packages/embed && \
    pip install --no-cache-dir "dbt-core==1.12.3" "dbt-postgres==1.11.0"