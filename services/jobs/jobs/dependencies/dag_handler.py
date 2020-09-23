import os
from typing import Dict, List

from dynaconf import settings
from nameko.extensions import DependencyProvider


class DagIdExtensions:
    """Domain holding the dag íd naming conventions."""

    preparation = "prep"
    parallel = "parallel"
    filename_prefix = "dag"
    file_extension = "py"

    def to_dict(self) -> Dict[str, str]:
        return {
            "preparation": self.preparation,
            "parallel": self.parallel,
        }


class DagHandler:
    """Handles the mapping between job_id and dags."""

    job_id_extensions = DagIdExtensions()

    def get_non_parallel_dag_id(self, job_id: str) -> str:
        """Return dag id for sync job.

        Currently also sync jobs are parallelized which does not make sense. Once this is changed this method can be
        used to return the sync job dag_id.
        """
        return self.get_preparation_dag_id(job_id)

    def get_preparation_dag_id(self, job_id: str) -> str:
        """Return dag_id of preparation dag."""
        return f"{job_id}_{self.job_id_extensions.preparation}"

    def get_parallel_dag_id(self, job_id: str) -> str:
        """Return dag_id of parallel dag."""
        return f"{job_id}_{self.job_id_extensions.parallel}"

    def get_dag_filename(self, dag_id: str) -> str:
        """Return the dag filename with extension."""
        return f"{self.job_id_extensions.filename_prefix}_{dag_id}.{self.job_id_extensions.file_extension}"

    def get_all_dag_ids(self, job_id: str) -> List[str]:
        """Return a list of all dag_ids connected to a job_id.

        Currently to dag_ids are returned the on of the preparation and of the parallel dag.
        """
        return [self.get_preparation_dag_id(job_id), self.get_parallel_dag_id(job_id)]

    def get_dag_path_from_id(self, dag_id: str) -> str:
        """Return the complete path on the file system from a dag_id."""
        return self.get_dag_path(self.get_dag_filename(dag_id=dag_id))

    def get_dag_path(self, dag_filename: str) -> str:
        """Get the complete path on the file system of from a dag_filename.

        Args:
            dag_filename: The filename of the dag (with extension)

        Returns:
            Absolute location of the dag on the file system
        """
        return os.path.join(settings.AIRFLOW_DAGS, dag_filename)

    def get_all_dag_paths(self, job_id: str) -> List[str]:
        """Get a list of ALL dag-files on the file system from a job_id."""
        dag_paths = []
        dag_ids = self.get_all_dag_ids(job_id)
        for dag_id in dag_ids:
            dag_filename = self.get_dag_filename(dag_id)
            dag_paths.append(self.get_dag_path(dag_filename))
        return dag_paths

    def remove_all_dags(self, job_id: str) -> None:
        """Remove all dags connected to the job_id.

        Currently this deletes all dags returned by the get_all_dag_ids method.
        """
        for dag_path in self.get_all_dag_paths(job_id):
            if os.path.isfile(dag_path):
                os.remove(dag_path)


class DagHandlerProvider(DependencyProvider):

    def get_dependency(self, worker_ctx: object) -> DagHandler:
        return DagHandler()
