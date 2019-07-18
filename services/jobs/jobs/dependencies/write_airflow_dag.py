import os
from shutil import copyfile
from openeo_pg_parser_python.translate_process_graph import translate_graph
from .map_processes import map_process


def WriteAirflowDag(job_id, user_name, process_graph_json, user_email=None, job_description=None):
    """
    Parse a process graph from the input json file, convert it to eoDataReaders syntax and
    creates an Apache Airflow DAG.
    """

    if not job_description:
        job_description = "No description provided."

        
    graph = translate_graph(process_graph_json)

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

    # Add default
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

    dagfile.write(
'''
dag = DAG(dag_id="{dag_id}",
          description="{dag_description}",
          catchup=False,
          default_args=default_args)
'''.format(dag_id=job_id, dag_description=job_description)
    )

    for node_id in graph.nodes:
        params, input_type, filepaths = map_process(graph.nodes[node_id].graph,
                                   graph.nodes[node_id].name,
                                   graph.nodes[node_id].id)
        # if parallel (from json process schema), second loop create airflow task
        #
        print(params, input_type, filepaths)
        print('\n')
        quotes = '' # empty
        if not filepaths:
            if graph.nodes[node_id].dependencies:
                filepaths = os.environ["JOB_DATA"] + os.path.sep + graph.nodes[node_id].dependencies[-1].id + os.path.sep # this is to be changed!
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

    for node_id in graph.nodes:
        if graph.nodes[node_id].dependencies:
            node_dependencies = []
            for dependency in graph.nodes[node_id].dependencies:
                node_dependencies.append(dependency.id)
            dagfile.write(
'''
{id}.set_upstream([{dependencies}])
'''.format(id=node_id, dependencies=",".join(map(str, node_dependencies)))
            )

    # Close file
    dagfile.close()

    # Move file to DAGs folder (must copy/delete because of volumes mounted on different )
    copyfile(dag_filename, "/usr/src/dags/" + dag_filename)
    os.remove(dag_filename)
