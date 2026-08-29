FROM apache/airflow:3.3.1

USER airflow
COPY --chown=airflow:root ./api  /opt/techmunkak

RUN pip install --no-cache-dir -e /opt/techmunkak/packages/core && \
    pip install --no-cache-dir -e /opt/techmunkak/packages/ingest && \
    pip install --no-cache-dir -e /opt/techmunkak/packages/embed && \
    pip install --no-cache-dir -e /opt/techmunkak/packages/nlp && \
    pip install --no-cache-dir "en_core_web_sm==3.8.0" && \
    pip install --no-cache-dir "dbt-core==1.12.3" "dbt-postgres==1.11.0"