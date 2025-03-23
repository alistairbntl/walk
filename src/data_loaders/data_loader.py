"""
The DataLoader class provides specific functionality to download,
process and upload data from the Census Bureaus ACS API.
"""

import pandas as pd
from typing import Dict

from collect_census_ts_data import get_ts_data
from data_loaders.data_pipeline_manager import DataPipelineManager
from geo_metadata import GEO_METADATA


class DataLoader(DataPipelineManager):
    begin_year = 2014
    end_year = 2023

    def __init__(self, dataloader_type):
        super().__init__()
        self.input_fields = self.pipeline_configs["acs_fields"][dataloader_type]
        self.upload_fields = self.pipeline_configs["raw_fields"][dataloader_type]
        self.upload_sql_table_name = self.pipeline_configs["raw_tables"][
            dataloader_type
        ]

    def _process_data(
        self, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        for geolevel, _df in data_dict.items():
            geo_metadata = GEO_METADATA[geolevel]
            _df["unique_geo_id"] = _df[geo_metadata["right_on"]].agg("".join, axis=1)
            _df["delimited_geo_id"] = _df[geo_metadata["right_on"]].agg(
                "-".join, axis=1
            )

        return data_dict

    def process_data(
        self, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        return self._process_data(data_dict)

    def collect_data(self):
        api_call_dict = {
            "type_": "acs1",
            "variables": self.input_fields,
            "state": ["*"],
            "begin_year": self.begin_year,
            "end_year": self.end_year,
        }

        state_data_df = get_ts_data(api_call_dict)

        api_call_dict = {
            "type_": "acs5",
            "variables": self.input_fields,
            "state": ["51"],
            "county": ["*"],
            "begin_year": self.begin_year,
            "end_year": self.end_year,
        }

        county_data_df = get_ts_data(api_call_dict)

        # census_tract data
        api_call_dict = {
            "type_": "acs5",
            "variables": self.input_fields,
            "state": ["51"],
            "tract": ["*"],
            "begin_year": self.begin_year,
            "end_year": self.end_year,
        }

        census_tract_df = get_ts_data(api_call_dict)

        return {
            "state": state_data_df,
            "county": county_data_df,
            "census_tract": census_tract_df,
        }
