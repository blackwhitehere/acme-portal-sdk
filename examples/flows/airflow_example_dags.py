"""Example Airflow DAGs for testing the AirflowFlowFinder."""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.decorators import dag, task

# Example 1: Traditional DAG instantiation
example_dag = DAG(
    dag_id="example_dag",
    description="A simple example DAG",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

# Example 2: DAG with project naming convention
project_dag = DAG(
    dag_id="acme-project--main--data-processing--dev",
    description="Data processing pipeline for development",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    tags=["PROJECT=acme-project", "BRANCH=main", "ENV=dev", "COMMIT_HASH=abc123"],
)


# Example 3: Using @dag decorator (Airflow 2.0+ style)
@dag(
    dag_id="decorated_example",
    description="Example using @dag decorator",
    schedule="@hourly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example", "decorated"],
)
def decorated_dag_example():
    """Example DAG using the @dag decorator."""

    @task
    def extract():
        return {"data": "extracted"}

    @task
    def transform(data):
        return {"data": data["data"] + " and transformed"}

    @task
    def load(data):
        print(f"Loading: {data}")

    extracted = extract()
    transformed = transform(extracted)
    load(transformed)


# Instantiate the decorated DAG
decorated_dag_instance = decorated_dag_example()

# Add some operators to the traditional DAGs for completeness
start_task = DummyOperator(
    task_id="start",
    dag=example_dag,
)

end_task = DummyOperator(
    task_id="end",
    dag=example_dag,
)

start_task >> end_task

process_task = DummyOperator(
    task_id="process_data",
    dag=project_dag,
)
