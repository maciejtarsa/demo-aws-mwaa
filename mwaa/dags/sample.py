from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime

# Define the default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Instantiate the DAG
with DAG(
    dag_id='dummy_operator_dag',
    default_args=default_args,
    description='A simple DAG with a DummyOperator',
    schedule_interval='@daily',
    start_date=datetime(2024, 8, 1),
    catchup=False,
) as dag:
    
    # Define the dummy task
    dummy_task = DummyOperator(
        task_id='dummy_task',
    )

# Set the task dependencies (if any)
dummy_task
