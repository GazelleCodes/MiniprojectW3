
from datetime import datetime, timedelta
import csv
import logging
import os

from airflow import DAG
from airflow.operators.python import PythonOperator # type: ignore
from airflow.operators.email import EmailOperator # type: ignore

DATA_FOLDER = "/opt/airflow/data"
DB_PATH = "/opt/airflow/data/warehouse.duckdb"

# Default settings for all tasks
default_args = {
    "owner": "quickcart",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email": ["your_email@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
}


# Task 1: Extract CSV files
def extract_csv(**context):
    logging.info("Starting CSV extraction")

    files = [
        os.path.join(DATA_FOLDER, name)
        for name in os.listdir(DATA_FOLDER)
        if name.lower().endswith(".csv")
    ]

    if not files:
        raise FileNotFoundError("No CSV files found")

    context["ti"].xcom_push(key="csv_files", value=files)
    logging.info("Found %d CSV files", len(files))


# Task 2: Validate CSV files
def validate_csv(**context):
    files = context["ti"].xcom_pull(
        task_ids="extract_csv",
        key="csv_files",
    )

    for file_path in files:
        logging.info("Validating %s", file_path)

        with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            header = next(reader, None)

            if not header or not any(column.strip() for column in header):
                raise ValueError(f"{file_path} has no header")

            if len(header) != len(set(header)):
                raise ValueError(
                    f"{file_path} contains duplicate column names"
                )

            for row_number, row in enumerate(reader, start=2):
                if len(row) != len(header):
                    raise ValueError(
                        f"Invalid row {row_number} in {file_path}"
                    )

        logging.info("Validation passed: %s", file_path)


# Task 3: Load CSV data into staging tables
def load_staging(**context):
    import duckdb # type: ignore

    files = context["ti"].xcom_pull(
        task_ids="extract_csv",
        key="csv_files",
    )

    os.makedirs(DATA_FOLDER, exist_ok=True)
    con = duckdb.connect(DB_PATH)

    try:
        for file_path in files:
            table_name = os.path.splitext(
                os.path.basename(file_path)
            )[0].lower()

            if not table_name.replace("_", "").isalnum():
                raise ValueError(f"Invalid table name: {table_name}")

            # Replace the staging table on each run with current CSV data
            safe_path = file_path.replace("'", "''")
            con.execute(
                f"""
                CREATE OR REPLACE TABLE staging_{table_name} AS
                SELECT *
                FROM read_csv_auto('{safe_path}', header = true)
                """
            )

            logging.info(
                "Loaded %s into staging_%s",
                file_path,
                table_name,
            )
    finally:
        con.close()


# Task 4: Transform data
def transform_data():
    logging.info("Starting QuickCart transformation")

    # Placeholder transformation step:
    # Replace this with dbt build if your project uses dbt.
    import duckdb # type: ignore

    con = duckdb.connect(DB_PATH)

    try:
        tables = con.execute("SHOW TABLES").fetchall()
        logging.info("Available tables: %s", tables)
        logging.info("Transformation step completed")
    finally:
        con.close()


with DAG(
    dag_id="quickcart_daily_pipeline",
    default_args=default_args,
    description="Daily QuickCart CSV ingestion pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    tags=["quickcart", "etl"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_csv",
        python_callable=extract_csv,
    )

    validate_task = PythonOperator(
        task_id="validate_csv",
        python_callable=validate_csv,
    )

    load_task = PythonOperator(
        task_id="load_staging",
        python_callable=load_staging,
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    failure_email = EmailOperator(
        task_id="send_failure_email",
        to="your_email@example.com",
        subject="QuickCart pipeline failed",
        html_content=(
            "<h3>QuickCart pipeline failed</h3>"
            "<p>Please check the Airflow task logs.</p>"
        ),
        trigger_rule="one_failed",
    )

    # Main task sequence
    extract_task >> validate_task >> load_task >> transform_task

    # Run the alert task if any pipeline task fails
    [
        extract_task,
        validate_task,
        load_task,
        transform_task,
    ] >> failure_email
