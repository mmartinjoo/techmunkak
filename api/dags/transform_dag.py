import pendulum
from airflow.sdk import dag
from airflow.providers.standard.operators.bash import BashOperator

DBT_PROJECT_DIR="/opt/techmunkak/transform"

@dag(
    dag_id="transform",
    start_date=pendulum.datetime(2026, 8, 29, tz="UTC"),
    catchup=False,
    schedule="0 2 * * *",
)
def transform():
    t_deps = BashOperator(
        task_id="dbt_deps",
        bash_command="dbt deps",
        cwd=DBT_PROJECT_DIR,
        env={"DBT_PROFILES_DIR": DBT_PROJECT_DIR},
        append_env=True,
    )
    
    t_seed= BashOperator(
            task_id="dbt_seed",
            bash_command="dbt seed",
            cwd=DBT_PROJECT_DIR,
            env={"DBT_PROFILES_DIR": DBT_PROJECT_DIR},
            append_env=True,
        )
    t_run= BashOperator(
        task_id="dbt_run",
        bash_command="dbt run",
        cwd=DBT_PROJECT_DIR,
        env={"DBT_PROFILES_DIR": DBT_PROJECT_DIR},
        append_env=True,
    )
    t_test = BashOperator(
        task_id="dbt_test",
        bash_command="dbt test",
        cwd=DBT_PROJECT_DIR,
        env={"DBT_PROFILES_DIR": DBT_PROJECT_DIR},
        append_env=True,
    )
    
    t_deps >> t_seed >> t_run >> t_test
    
transform()