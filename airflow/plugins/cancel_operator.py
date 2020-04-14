import os

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults


class CancelOp(BaseSensorOperator):
    """
    This sensor monitors the job folder for a stop_file. Evaluates to true when the file exists.

    This is currently the only option in Airflow to stop a running task via code.
    see: https://stackoverflow.com/questions/49039386/how-do-i-stop-an-airflow-dag
    """

    @apply_defaults
    def __init__(self, stop_file: str, *args, **kwargs):
        super().__init__(mode='poke', poke_interval=5, *args, **kwargs)
        self.stop_file = stop_file

    def poke(self, context):
        self.log.info('Poking for file')
        return os.path.isfile(self.stop_file)


def add_stop_file(stop_file: str, **kwargs) -> None:
    """Adds STOP file to job.
    Job finished successful, cancel sensor needs to finish with success. > Satisfy success criteria.
    This will trigger the cancel action (set all running tasks to failed). This has no effect as all tasks are finished.

    Arguments:
        stop_file {str} -- File path to STOP file (needs to be equal to the one used in the cancel sensor!)
    """
    if not os.path.isfile(stop_file):
        open(stop_file, 'a').close()


def flag_running_tasks_as_failed(dag: DAG, **kwargs) -> None:
    """Flags not finished tasks as failed to stop the dag.

    Arguments:
        dag {DAG} -- Dag to stop
    """
    tasks = dag.get_task_instances(state=['running', 'queued', 'up_for_reschedule', 'up_for_retry', 'scheduled'])
    for task in tasks:
        task.set_state('failed')


class AddStopFileOp(PythonOperator):
    @apply_defaults
    def __init__(self, stop_file: str, *args, **kwargs):
        super().__init__(python_callable=add_stop_file,
                         op_kwargs={'stop_file': stop_file},
                         provide_context=True, *args, **kwargs)


class StopDagOp(PythonOperator):
    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=flag_running_tasks_as_failed,
                         provide_context=True, *args, **kwargs)


class CancelPlugin(AirflowPlugin):
    name = "cancel_plugin"
    operators = [CancelOp, AddStopFileOp, StopDagOp]
