from nameko.extensions import DependencyProvider
from random import choice
from string import ascii_lowercase, digits
from ..models import Task

class TasksWrapper:
    def __init__(self):
        self.tasks = []

    def parse_process_graph(self, job_id, process_graph):
        self.parse_tasks(job_id, process_graph)
        self.tasks = self.tasks[::-1]
        for idx, task in enumerate(self.tasks):
            task.seq_num = idx

        return self.tasks

    def parse_tasks(self, job_id, task_graph): #, next_task=None
        if "process_id" in task_graph:
            process_name = task_graph["process_id"]
            args = task_graph["args"]
            prev_task = args.pop("imagery") if "imagery" in args else None
        if "product_id" in task_graph:
            process_name = "extract-s2" #TODO: Implement extractors for all data
            args = {"product": task_graph["product_id"]}
            prev_task = None

        task = Task(job_id, process_name, len(self.tasks), args) #. next_task
        self.tasks.append(task)

        if prev_task:
            self.parse_tasks(job_id, prev_task) #, task

class TaskParser(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return TasksWrapper()