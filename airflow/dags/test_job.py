from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
#from eodatareaders.eo_data_reader import eoDataReader
from airflow.operators import eoDataReadersOp

filename = "/data_in/S2A_MSIL1C_20170620T100031_N0205_R122_T33UWP_20170620T100453.zip"
root_folder = "/data_out"

process_graph = [
    {'name': 'set_output_folder', 'folder_name': root_folder + '/output_ndvi_ndwi/', 'absolute_path': True},
    {'name': 'eo_function', 'bands': [4, 8], 'group_bands': True, 'f_input': {'f_name' : 'ndvi'}},
    {'name': 'quick_preview', 'bands': 'ndvi'}
]

process_graph2 = [
    {'name': 'set_output_folder', 'folder_name': root_folder + '/output_ndvi_ndwi/', 'absolute_path': True},
    {'name': 'eo_function', 'bands': [3, 8], 'group_bands': True, 'f_input': {'f_name' : 'ndwi'}},
    {'name': 'quick_preview', 'bands': 'ndwi'}
]

default_args = {
    'owner': 'luca-user',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}


job_id = 'jb-12345'
job_description = 'Simple job.'
dag = DAG(dag_id=job_id,
          description=job_description,
          schedule_interval=timedelta(days=100),
          catchup=False,
          default_args=default_args)

dummy_task = DummyOperator(task_id='dummy_task', dag=dag)

operator_task_1 = eoDataReadersOp(task_id='step_1',
                                  dag=dag,
                                  input_filepaths=filename,
                                  input_params=process_graph)
operator_task_2 = eoDataReadersOp(task_id='step_2',
                                  dag=dag,
                                  input_filepaths=filename,
                                  input_params=process_graph2)

operator_task_1.set_upstream([dummy_task])
operator_task_2.set_upstream([dummy_task, operator_task_1])
