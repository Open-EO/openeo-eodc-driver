import os
import glob
import logging

from airflow.models import BaseOperator
from airflow.operators.python_operator import PythonOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from eodatareaders.eo_data_reader import EODataProcessor
from eodc_openeo_bindings.job_writer.dag_writer import AirflowDagWriter

log = logging.getLogger(__name__)

class eoDataReadersOp(BaseOperator):

    @apply_defaults
    def __init__(self, input_filepaths, input_dc_filepaths, input_params, *args, **kwargs):
        self.input_filepaths = input_filepaths
        self.input_dc_filepaths = input_dc_filepaths
        self.input_params = input_params
        super(eoDataReadersOp, self).__init__(*args, **kwargs)

    def execute(self, context):
        _ = EODataProcessor(filepaths=self.input_filepaths, user_params=self.input_params, dc_filepaths=self.input_dc_filepaths)


# def parallelise_dag(job_id, user_name, process_graph_json, job_data, process_def):
#     """
# 
#     """
# 
#     writer = AirflowDagWriter()
#     domain = writer.get_domain(job_id=job_id,
#                                user_name=user_name,
#                                proces_graph_json=process_graph_json,
#                                job_data=job_data,
#                                process_dfs=process_defs)
#     writer.rewrite_and_move_job(domain)
# 
# 
# class ParalleliseDagOp(PythonOperator):
#     @apply_defaults
#     def __init__(self, job_id, user_name, process_graph_json, job_data, process_def, *args, **kwargs):
#         super().__init__(python_callable=parallelise_dag,
#                          op_kwargs={
#                             'job_id': job_id,
#                             'user_name': user_name,
#                             'process_graph_json': process_graph_json,
#                             'job_data': job_data,
#                             'process_def': process_def
#                             }
#                         )


class eoDataReadersPlugin(AirflowPlugin):
    name = "eo_data_readers_plugin"
    operators = [eoDataReadersOp]
