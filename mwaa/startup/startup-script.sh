#!/bin/sh

set -e
export DBT_VENV_PATH="${AIRFLOW_HOME}/dbt_venv"
export PIP_USER=false
python3 -m venv "${DBT_VENV_PATH}"
${DBT_VENV_PATH}/bin/pip install --no-index --find-links=/usr/local/airflow/plugins dbt-snowflake

export PIP_USER=true
