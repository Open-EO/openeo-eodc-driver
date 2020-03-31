import os

from airflow.plugins_manager import AirflowPlugin
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.decorators import apply_defaults
from airflow.models import TaskInstance, DAG


class CancelOp(BaseSensorOperator):
    @apply_defaults
    def __init__(self, stop_file: str, *args, **kwargs):
        super().__init__(mode='reschedule', *args, **kwargs)
        self.stop_file = stop_file

    def poke(self, context):
        return os.path.isfile(self.stop_file)


def flag_task_as_skipped(task, **kwargs):
    ti = TaskInstance(task, kwargs["execution_date"])
    ti.set_state('skipped')


def flag_running_tasks_as_skipped(dag: DAG, **kwargs):
    for state in ['running', 'queued', 'up_for_reschedule', 'up_for_retry']:
        tasks = dag.get_task_instances(state=state)
        for task in tasks:
            task.set_state('failed')


class TaskSkipOp(PythonOperator):
    @apply_defaults
    def __init__(self, task, *args, **kwargs):
        super().__init__(python_callable=flag_task_as_skipped,
                         op_kwargs={'task': task},
                         provide_context=True, *args, **kwargs)


class RunningTaskSkipOp(PythonOperator):
    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(python_callable=flag_running_tasks_as_skipped,
                         provide_context=True, *args, **kwargs)


class CancelPlugin(AirflowPlugin):
    name = "cancel_plugin"
    operators = [CancelOp, TaskSkipOp, RunningTaskSkipOp]
