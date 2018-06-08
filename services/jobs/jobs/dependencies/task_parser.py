from nameko.extensions import DependencyProvider
from random import choice
from string import ascii_lowercase, digits
from ..models import Task

# TODO: Exception Handling -> Bad Input?

class TasksWrapper:
    # TODO: Aliases for product names?
    _filter_mapper = {
        "s2a_prd_msil1c": "filter-s2"
    }

    def __init__(self):
        self.tasks = []
        self.filters = {}

    def parse_process_graph(self, job_id, process_graph, processes):
        self.processes = processes
        self.parse_tasks(job_id, process_graph)
        self.tasks = self.tasks[::-1]
        self.tasks.append(Task(job_id, "convert", len(self.tasks), {"job_id": job_id}))
        for idx, task in enumerate(self.tasks):
            task.seq_num = idx

        return self.tasks

    def extract_filter_args(self, filter_graph):
        if "process_id" in filter_graph:
            args = filter_graph["args"]
            imagery = args.pop("imagery")
            self.filters[filter_graph["process_id"]] = args
            self.extract_filter_args(imagery)
        elif "product_id" in filter_graph:
            self.filters["product"] = filter_graph["product_id"]

    def parse_tasks(self, job_id, task_graph):
        process_id = task_graph["process_id"]

        for process in self.processes:
            if process['process_id'] == process_id:
                process_spec = process
                break

        if process_spec["process_type"] == "operation":
            args = task_graph["args"]
            imagery = args.pop("imagery")
            self.tasks.append(
                Task(job_id, process_id, len(self.tasks), args))
            self.parse_tasks(job_id, imagery)
        elif process_spec["process_type"] == "filter":
            self.extract_filter_args(task_graph)
            process_id = self._filter_mapper[self.filters["product"]]
            self.tasks.append(
                Task(job_id, process_id, len(self.tasks), self.filters))


class TaskParser(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return TasksWrapper()
