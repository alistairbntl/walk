from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict
import yaml

from core.utils import get_db_manager


class DataPipelineManager(ABC):
    def __init__(self):
        self.load_pipeline_config()
        self.upload_sql_table_name = None
        self.upload_fields = None
        self.input_sql_table_name = None
        self.input_fields = None

    def run_pipeline(self):
        data_dict = self.collect_data()
        data_dict = self.process_data(data_dict)
        self.upload_data(data_dict)

    def upload_data(self, data_dict):
        db_manager = get_db_manager()

        for region, df_ in data_dict.items():
            df_["geo_level"] = region
            db_manager.df_to_sql_table(
                df_[self.upload_fields],
                self.upload_sql_table_name,
                if_exists="append",
            )

    def load_pipeline_config(self):
        with open("/home/alistair/walk/src/data_loaders/data_pipeline.yaml") as file:
            config = yaml.safe_load(file)
        self.pipeline_configs = config

    @abstractmethod
    def collect_data(self) -> Dict[str, pd.DataFrame]:
        """This method must be overridden in a subclass"""
        pass

    @abstractmethod
    def process_data(self, data_dict) -> Dict[str, pd.DataFrame]:
        """This method must be overridden in a subclass"""
        pass
