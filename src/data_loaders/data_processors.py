"""
Main class for capturing and storing ACS API data.
"""

import numpy as np
import pandas as pd
from typing import Dict

from core.pd_utils import create_percent_change_columns, create_diff_change_columns
from core.utils import load_config, get_db_manager

from data_loaders.data_pipeline_manager import DataPipelineManager
from geo_metadata import GEO_METADATA
from load_shapefiles import get_shapefiles


class DataProcessor(DataPipelineManager):
    def __init__(self, dataloader_type):
        super().__init__()
        self.input_fields = self.pipeline_configs["raw_fields"][dataloader_type]
        self.input_sql_table_name = self.pipeline_configs["raw_tables"][dataloader_type]
        self.upload_fields = self.pipeline_configs["processed_fields"][dataloader_type]
        self.upload_sql_table_name = self.pipeline_configs["processed_tables"][
            dataloader_type
        ]

    def collect_data(self) -> Dict[str, pd.DataFrame]:
        raw_data_sql = f"""SELECT * FROM {self.input_sql_table_name}"""

        db_manager = get_db_manager()
        return_df = db_manager.query_to_df(raw_data_sql)

        data_dict = {
            geo_level: group.reset_index(drop=True)
            for geo_level, group in return_df.groupby("geo_level")
        }

        return data_dict

    def _create_regional_id_cols(self, _df, geo_metadata):
        _df[geo_metadata["groupby"]] = _df["delimited_geo_id"].str.split(
            "-", expand=True
        )
        return _df


class DemographicDataProcessor(DataProcessor):
    def __init__(self):
        super().__init__("demographics")

    def process_data(self, data_dict):
        for geolevel, _df in data_dict.items():
            geo_metadata = GEO_METADATA[geolevel]
            _df = self._create_regional_id_cols(_df, geo_metadata)
            _df = self._compute_population_density(_df, geo_metadata)
            _df = self._compute_rates_of_change(_df, geo_metadata)
            _df = self._compute_migration_rates(_df)
            _df = self._compute_family_metrics(_df)
            data_dict[geolevel] = _df
        return data_dict

    def _compute_rates_of_change(self, data_df, geo_metadata):
        data_df = data_df.groupby(geo_metadata["groupby"]).apply(
            create_percent_change_columns,
            columns=["total_population_data"],
            periods_back=1,
        )

        data_df = data_df.groupby(geo_metadata["groupby"]).apply(
            create_percent_change_columns,
            columns=["total_population_data"],
            periods_back=5,
        )

        data_df = data_df.groupby(geo_metadata["groupby"]).apply(
            create_diff_change_columns, columns=["median_age_data"], periods_back=5
        )
        return data_df

    def _compute_population_density(self, data_df, geo_metadata):
        config = load_config()
        shape_dict = get_shapefiles(config)

        shape_df = shape_dict[geo_metadata["shape_name"]][["GEOID", "ALAND"]]

        data_df = pd.merge(
            data_df, shape_df, left_on="unique_geo_id", right_on="GEOID"
        ).drop(columns="GEOID")
        # population density per sq mile
        data_df["population_density_data"] = (
            data_df["total_population_data"] / data_df["ALAND"] * (2589988.11)
        )

        return data_df

    def _compute_migration_rates(self, data_df):
        """
        Computes population percentages who moved in the past
        year, including breakdowns of moving origin.
        """
        data_df["percent_did_not_move_in_last_year_data"] = (
            data_df[
                [
                    "lived_in_same_house_one_year_ago_data",
                ]
            ].sum(axis=1)
            / data_df["total_population_migration_data"]
            * 100
        )

        data_df["percent_moved_in_last_year_data"] = (
            100 - data_df["percent_did_not_move_in_last_year_data"]
        )

        data_df["percent_moved_within_county_in_last_year_data"] = (
            data_df[["moved_within_county_data"]].sum(axis=1)
            / data_df["total_population_migration_data"]
            * 100
        )

        data_df["percent_moved_from_different_county_same_state_in_last_year_data"] = (
            data_df[["moved_from_different_county_same_state_data"]].sum(axis=1)
            / data_df["total_population_migration_data"]
            * 100
        )

        data_df["percent_moved_from_different_state_in_last_year_data"] = (
            data_df[["moved_from_different_state_data"]].sum(axis=1)
            / data_df["total_population_migration_data"]
            * 100
        )

        data_df["percent_moved_from_abroad_in_last_year_data"] = (
            data_df[["moved_from_abroad_data"]].sum(axis=1)
            / data_df["total_population_migration_data"]
            * 100
        )

        return data_df

    def _compute_family_metrics(self, data_df):
        data_df["families_per_person_data"] = (
            data_df["total_families_data"] / data_df["total_population_data"]
        )

        data_df["percent_families_married_data"] = (
            data_df["married_couple_families_data"] / data_df["total_families_data"]
        )

        data_df["percent_families_married_with_own_children_data"] = (
            data_df["married_couple_families_with_own_children_data"]
            / data_df["total_families_data"]
        )

        return data_df


class WorkForceDataProcessor(DataProcessor):
    def __init__(self):
        super().__init__("workforce")

    def process_data(self, data_dict):
        for geolevel, _df in data_dict.items():
            _df = self._compute_education_bins(_df)
            data_dict[geolevel] = _df
        return data_dict

    def _compute_education_bins(
        self, df_: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        df_["percent_less_hs_data"] = (
            df_[
                [
                    "population_25_plus_no_schooling_data",
                    "population_25_plus_nursery_school_data",
                    "population_25_plus_kindergarten_data",
                    "population_25_plus_1st_grade_data",
                    "population_25_plus_2nd_grade_data",
                    "population_25_plus_3rd_grade_data",
                    "population_25_plus_4th_grade_data",
                    "population_25_plus_5th_grade_data",
                    "population_25_plus_6th_grade_data",
                    "population_25_plus_7th_grade_data",
                    "population_25_plus_8th_grade_data",
                    "population_25_plus_9th_grade_data",
                    "population_25_plus_10th_grade_data",
                    "population_25_plus_11th_grade_data",
                    "population_25_plus_12th_grade_no_diploma_data",
                ]
            ].sum(axis=1)
            / df_["total_population_25_plus_data"]
            * 100
        )

        df_["percent_college_degree_data"] = (
            df_[
                [
                    "population_25_plus_bachelors_degree_data",
                    "population_25_plus_masters_degree_data",
                    "population_25_plus_professional_degree_data",
                    "population_25_plus_phd_data",
                ]
            ].sum(axis=1)
            / df_["total_population_25_plus_data"]
        ) * 100

        return df_


class HousingMarketDataProcessor(DataProcessor):
    def __init__(self):
        super().__init__("housing_market")

    def process_data(self, data_dict):
        for geolevel, _df in data_dict.items():
            geo_metadata = GEO_METADATA[geolevel]
            _df = self._create_regional_id_cols(_df, geo_metadata)
            _df = self._set_null_values(_df)
            _df = self._compute_owner_and_renter_occupied_percents(_df)
            _df = self._compute_rates_of_change(_df, geo_metadata)
            data_dict[geolevel] = _df
        return data_dict

    def _compute_owner_and_renter_occupied_percents(self, _df):
        _df["owner_occupied_housing_units_data_percent"] = (
            _df["owner_occupied_housing_units_data"]
            / _df["total_occupied_housing_units_data"]
        ) * 100

        _df["renter_occupied_housing_units_data_percent"] = (
            _df["renter_occupied_housing_units_data"]
            / _df["total_occupied_housing_units_data"]
        ) * 100

        return _df

    def _compute_rates_of_change(self, data_df, geo_metadata):
        data_df = data_df.groupby(geo_metadata["groupby"]).apply(
            create_percent_change_columns,
            columns=["median_home_price_data"],
            periods_back=1,
        )

        data_df = data_df.groupby(geo_metadata["groupby"]).apply(
            create_percent_change_columns,
            columns=["median_home_price_data"],
            periods_back=5,
        )

        return data_df

    def _set_null_values(self, data_df):
        data_df["median_home_price_with_nulls_data"] = data_df[
            "median_home_price_data"
        ].replace(-666666666, np.nan)
        return data_df
