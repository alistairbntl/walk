"""
Manages data loading and processing for dsml models.

In addition to the input and output tables / fields,
dsml loaders typically include information about a cached
machine learning model which is used to process the input
data into the output format.
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

from data_loaders.data_pipeline_manager import DataPipelineManager
from dsml_model_tools.model_cache_manager import ModelCacheManager

from core.utils import get_db_manager


class ClusterAnalysis(DataPipelineManager):
    def __init__(self, dataloader_type):
        super().__init__()
        self.upload_fields = None
        self.upload_sql_table_name = None


class DemographicClusterAnalysis(ClusterAnalysis):
    def collect_data(self):
        with open(
            self.pipeline_configs["dsml_sql_scripts"]["demographic_clusters"], "r"
        ) as file:
            sql_str = file.read()

        db_manager = get_db_manager()
        return_df = db_manager.query_to_df(sql_str)

        data_dict = {
            geo_level: group.reset_index(drop=True)
            for geo_level, group in return_df.groupby("geo_level")
        }

        return data_dict

    def process_data(self):
        pass


class MedianHomePriceModel(DataPipelineManager):
    def __init__(self, model_specs):
        super().__init__()
        self.model_specs = model_specs
        self.upload_sql_table_name = self.pipeline_configs["model_output_tables"][
            "median_home_price_census_tract_model"
        ]
        self.upload_fields = self.pipeline_configs["model_output_fields"][
            "median_home_price_census_tract_model"
        ]

    def collect_data(self) -> dict:
        # load cached model
        model_cache_manager = ModelCacheManager(self.model_specs)
        ml_model = model_cache_manager.uncache_model()

        # load input data
        sql_file_path = self.model_specs["dataload_path"]
        with open(sql_file_path, "r") as file:
            sql_script = file.read()

        db_manager = get_db_manager()

        return_df = db_manager.query_to_df(sql_script)

        data_dict = {
            geo_level: group.reset_index(drop=True)
            for geo_level, group in return_df.groupby("geo_level")
        }

        return {"ml_model": ml_model, "data_dict": data_dict}

    def process_data(self, model_data_dict):
        model = model_data_dict["ml_model"]
        data_dict = model_data_dict["data_dict"]

        columns = [col for col in data_dict["county"].columns if "_data" in col]

        for col in columns:
            data_dict["census_tract"][f"normalized_{col}"] = (
                data_dict["census_tract"][col]
                - data_dict["state"].query("unique_geo_id=='51'")[col].iloc[0]
            )

        df_ = data_dict["census_tract"][self.model_specs["independent_variables"]]
        scalar = StandardScaler()
        df_ = pd.DataFrame(scalar.fit_transform(df_), columns=df_.columns)
        dependent_scalar = StandardScaler()
        dependent_scalar.fit_transform(
            data_dict["census_tract"][self.model_specs["dependent_variable"]]
        )

        df_ = sm.add_constant(df_)

        data_dict["census_tract"]["demeaned_predicted_home_price"] = (
            dependent_scalar.inverse_transform(
                model.ols_model.predict(df_).values.reshape(-1, 1)
            )
        )

        data_dict["census_tract"]["model_name"] = self.model_specs["name"]
        # arb - TODO - clean this up
        data_dict["census_tract"] = data_dict["census_tract"].rename(
            columns={
                "normalized_median_home_price_with_nulls_data": "demeaned_actual_home_price"
            }
        )
        return data_dict
