import os
import glob
import logging

from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults
from eodatareaders.eo_data_reader import EODataProcessor

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

class eoDataReadersPlugin(AirflowPlugin):
    name = "eo_data_readers_plugin"
    operators = [eoDataReadersOp]
