"""Example Airflow DAG using @dag decorator for testing the AirflowFlowFinder."""

from datetime import datetime
from airflow.decorators import dag, task


@dag(
    dag_id="acme-project--main--example-flow--dev",
    description="Example DAG using @dag decorator for development environment",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["PROJECT=acme-project", "BRANCH=main", "ENV=dev", "COMMIT_HASH=abc123"],
)
def example_dag():
    """Example DAG using the @dag decorator following the project naming convention."""

    @task
    def extract_data():
        """Extract data from source."""
        return {"data": "extracted from source"}

    @task
    def transform_data(data: dict):
        """Transform the extracted data."""
        transformed = data["data"] + " -> transformed"
        return {"data": transformed}

    @task
    def load_data(data: dict):
        """Load the transformed data."""
        print(f"Loading data: {data['data']}")
        return "Data loaded successfully"

    # Define the task dependencies
    extracted = extract_data()
    transformed = transform_data(extracted)
    load_data(transformed)


# Instantiate the DAG
example_dag_instance = example_dag()
