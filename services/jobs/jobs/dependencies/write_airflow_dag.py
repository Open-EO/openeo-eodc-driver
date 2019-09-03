import os
from shutil import copyfile
from .openeo_to_eodatareaders import openeo_to_eodatareaders


def WriteAirflowDag(job_id, user_name, process_graph_json, job_data, user_email=None, job_description=None):
    """
    Creates an Apache Airflow DAG with eoDataReaders syntax from a parsed openEO process graph.
    """
    
    # Convert from openEO to eoDataReaders syntax
    nodes, graph = openeo_to_eodatareaders(process_graph_json, job_data)

    if not job_description:
        job_description = "No description provided."

    dag_filename = 'dag_' + job_id + '.py'
    dagfile = open(dag_filename, 'w+')

    # Add imports
    dagfile.write(
'''
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
#from eodatareaders.eo_data_reader import eoDataReader
from airflow.operators import eoDataReadersOp
'''
    )
    dagfile.write('\n')

    # Add default args
    dagfile.write(
'''
default_args = {{
    'owner': "{username}",
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': "{usermail}",
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'schedule_interval': None,
    'catchup': False,
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}}
'''.format(username=user_name, usermail=user_email)
    )

    # Add DAG instance
    dagfile.write(
'''
dag = DAG(dag_id="{dag_id}",
          description="{dag_description}",
          catchup=False,
          default_args=default_args)
'''.format(dag_id=job_id, dag_description=job_description)
    )
    
    # Add nodes
    for node in nodes:
        node_id = node[0]
        params = node[1]
        filepaths = node[2]
        node_dependencies = node[3]
        print(params, filepaths)
        print('\n')
        quotes = '' # empty
        if not filepaths:
            if node_dependencies:
                filepaths = []
                for dep in node_dependencies:
                    filepaths.append(job_data + os.path.sep + dep + os.path.sep)
            # if graph.nodes[node_id].dependencies:
            #     filepaths = job_data + os.path.sep + graph.nodes[node_id].dependencies[-1].id + os.path.sep # this is to be changed!
            quotes = '"' # "
        dagfile.write(
'''
{id} = eoDataReadersOp(task_id="{task_id}",
                                dag=dag,
                                input_filepaths={quote}{filepaths}{quote},
                                input_params={process_graph}
                                )
'''.format(id=node_id, task_id=node_id, filepaths=filepaths, quote=quotes, process_graph=params)
        )
#         if node_dependencies:                
#             dagfile.write(
# '''
# {id}.set_upstream([{dependencies}])
# '''.format(id=node_id, dependencies=",".join(map(str, node_dependencies)))
#                 )
    
    # Add node dependencies
    for node in nodes:
        node_id = node[0]
        params = node[1]
        filepaths = node[2]
        node_dependencies = node[3]
        if node_dependencies:
            dagfile.write(
'''
{id}.set_upstream([{dependencies}])
'''.format(id=node_id, dependencies=",".join(map(str, node_dependencies)))
                )

    # Close file
    dagfile.close()

    # Move file to DAGs folder (must copy/delete because of volumes mounted on different )
    copyfile(dag_filename, os.environ.get('AIRFLOW_DAGS') + "/" + dag_filename)
    os.remove(dag_filename)
