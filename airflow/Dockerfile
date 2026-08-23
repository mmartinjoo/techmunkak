FROM apache/airflow:3.3.1

USER airflow
COPY --chown=airflow:root ./api/packages/core  /opt/techmunkak/packages/core
COPY --chown=airflow:root ./api/packages/ingest /opt/techmunkak/packages/ingest

RUN pip install --no-cache-dir -e /opt/techmunkak/packages/core && \
    pip install --no-cache-dir -e /opt/techmunkak/packages/ingest