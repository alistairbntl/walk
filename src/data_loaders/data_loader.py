from abc import ABC, abstractmethod
import pandas as pd

from core.pd_utils import create_percent_change_columns, create_diff_change_columns
from core.utils import load_config, get_db_manager

from collect_census_ts_data import get_ts_data
from geo_metadata import GEO_METADATA
from load_shapefiles import get_shapefiles


class DataLoader(ABC):
    census_variables = None
    upload_columns = None
    sql_table_name = None
    begin_year = 2014
    end_year = 2023

    def __init__(self):
        pass

    @abstractmethod
    def process_data(self, api_call_dict, geolevel="county"):
        """This method must be overridden in a subclass"""
        pass

    def _process_data(self, api_call_dict, geolevel):
        geo_metadata = GEO_METADATA[geolevel]

        _df = get_ts_data(api_call_dict)

        # set geo ids
        _df["geo_id"] = _df[geo_metadata["right_on"]].agg("".join, axis=1)
        _df["delimited_geo_id"] = _df[geo_metadata["right_on"]].agg("".join, axis=1)

        return _df

    def load_data(self):
        api_call_dict = {
            "type_": "acs1",
            "variables": self.census_variables,
            "state": ["*"],
            "begin_year": self.begin_year,
            "end_year": self.end_year,
        }

        state_data_df = self.process_data(api_call_dict, geolevel="state")

        api_call_dict = {
            "type_": "acs5",
            "variables": self.census_variables,
            "state": ["51"],
            "county": ["*"],
            "begin_year": self.begin_year,
            "end_year": self.end_year,
        }

        county_data_df = self.process_data(api_call_dict)

        # census_tract data
        api_call_dict = {
            "type_": "acs5",
            "variables": self.census_variables,
            "state": ["51"],
            "tract": ["*"],
            "begin_year": self.begin_year,
            "end_year": self.end_year,
        }

        census_tract_df = self.process_data(api_call_dict, geolevel="tract")

        return {
            "state": state_data_df,
            "county": county_data_df,
            "census_tract": census_tract_df,
        }

    def upload_df(self, data_dict):
        db_manager = get_db_manager()

        for region, df_ in data_dict.items():
            df_["geo_level"] = region
            db_manager.df_to_sql_table(
                df_[self.upload_columns],
                self.sql_table_name,
                if_exists="append",
            )


class DemographicDataLoader(DataLoader):
    census_variables = [
        "NAME",
        "B01001_001E",
        "B01002_001E",
    ]
    upload_columns = [
        "geo_level",
        "geo_id",
        "year",
        "total_population_data",
        "total_population_data_1_period_growth_rate",
        "total_population_data_5_period_growth_rate",
        "median_age_data",
        "median_age_data_5_period_diff",
        "population_density",
    ]
    sql_table_name = "census_bureau_demographic_ts"

    def process_data(self, api_call_dict, geolevel="county"):
        regional_data_df = self._process_data(api_call_dict, geolevel)

        geo_metadata = GEO_METADATA[geolevel]

        config = load_config()
        shape_dict = get_shapefiles(config)

        regional_data_df = regional_data_df.groupby(geo_metadata["groupby"]).apply(
            create_percent_change_columns,
            columns=["total_population_data"],
            periods_back=1,
        )

        regional_data_df = regional_data_df.groupby(geo_metadata["groupby"]).apply(
            create_percent_change_columns,
            columns=["total_population_data"],
            periods_back=5,
        )

        regional_data_df = regional_data_df.groupby(geo_metadata["groupby"]).apply(
            create_diff_change_columns, columns=["median_age_data"], periods_back=5
        )

        shape_df = shape_dict[geo_metadata["shape_name"]][["GEOID", "ALAND"]]

        regional_data_df = pd.merge(
            regional_data_df, shape_df, left_on="geo_id", right_on="GEOID"
        ).drop(columns="GEOID")
        # population density per sq mile
        regional_data_df["population_density"] = (
            regional_data_df["total_population_data"]
            / regional_data_df["ALAND"]
            * (2589988.11)
        )

        return regional_data_df


class WorkForceDataLoader(DataLoader):
    census_variables = [
        "B15003_001E",
        "B15003_002E",
        "B15003_003E",
        "B15003_004E",
        "B15003_005E",
        "B15003_006E",
        "B15003_007E",
        "B15003_008E",
        "B15003_009E",
        "B15003_010E",
        "B15003_011E",
        "B15003_012E",
        "B15003_013E",
        "B15003_014E",
        "B15003_015E",
        "B15003_016E",
        "B15003_022E",
        "B15003_023E",
        "B15003_024E",
        "B15003_025E",
    ]
    upload_columns = [
        "geo_level",
        "geo_id",
        "year",
        "percent_less_hs_data",
        "percent_college_degree_data",
    ]
    sql_table_name = "census_bureau_workforce_ts"

    def process_data(self, api_call_dict, geolevel="county"):
        regional_data_df = self._process_data(api_call_dict, geolevel)
        regional_data_df["percent_less_hs_data"] = (
            regional_data_df[
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
            / regional_data_df["total_population_25_plus_data"]
            * 100
        )

        regional_data_df["percent_college_degree_data"] = (
            regional_data_df[
                [
                    "population_25_plus_bachelors_degree_data",
                    "population_25_plus_masters_degree_data",
                    "population_25_plus_professional_degree_data",
                    "population_25_plus_phd_data",
                ]
            ].sum(axis=1)
            / regional_data_df["total_population_25_plus_data"]
        ) * 100

        return regional_data_df


class HousingMarketDataLoader(DataLoader):
    census_variables = [
        "B25013_001E",
        "B25013_002E",
        "B25013_007E",
    ]
    upload_columns = [
        "geo_level",
        "geo_id",
        "year",
        "owner_occupied_housing_units_data",
        "renter_occupied_housing_units_data",
        "owner_occupied_housing_units_data_percent",
        "renter_occupied_housing_units_data_percent",
    ]
    sql_table_name = "census_bureau_housing_market_ts"

    def process_data(self, api_call_dict, geolevel="county"):
        regional_data_df = self._process_data(api_call_dict, geolevel)

        regional_data_df["owner_occupied_housing_units_data_percent"] = (
            regional_data_df["owner_occupied_housing_units_data"]
            / regional_data_df["total_occupied_housing_units_data"]
        ) * 100

        regional_data_df["renter_occupied_housing_units_data_percent"] = (
            regional_data_df["renter_occupied_housing_units_data"]
            / regional_data_df["total_occupied_housing_units_data"]
        ) * 100

        return regional_data_df
