import pandas as pd
from typing import Dict

from collect_census_ts_data import get_ts_data
from data_loaders.data_pipeline_manager import DataPipelineManager
from geo_metadata import GEO_METADATA


class DataLoader(DataPipelineManager):
    begin_year = 2014
    end_year = 2023

    def __init__(self):
        pass

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


class DemographicDataLoader(DataLoader):
    input_fields = [
        "NAME",
        "B01001_001E",
        "B01002_001E",
        # mobility statistics
        "B07001_001E",
        "B07001_017E",
        "B07001_033E",
        "B07001_049E",
        "B07001_065E",
        "B07001_081E",
    ]
    upload_fields = [
        "geo_level",
        "unique_geo_id",
        "delimited_geo_id",
        "year",
        "name",
        "total_population_data",
        "median_age_data",
        "lived_in_same_house_one_year_ago_data",
        "moved_within_county_data",
        "moved_from_different_county_same_state_data",
        "moved_from_different_state_data",
        "moved_from_abroad_data",
        "total_population_migration_data",
    ]
    upload_sql_table_name = "raw_data_census_bureau_demographic_ts"

    def process_data(self, data_dict):
        return self._process_data(data_dict)


class WorkForceDataLoader(DataLoader):
    input_fields = [
        "NAME",
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
    upload_fields = [
        "geo_level",
        "unique_geo_id",
        "delimited_geo_id",
        "year",
        "total_population_25_plus_data",
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
        "population_25_plus_bachelors_degree_data",
        "population_25_plus_masters_degree_data",
        "population_25_plus_professional_degree_data",
        "population_25_plus_phd_data",
    ]
    upload_sql_table_name = "raw_data_census_bureau_workforce_ts"

    def process_data(self, data_dict):
        return self._process_data(data_dict)


class HousingMarketDataLoader(DataLoader):
    input_fields = [
        "NAME",
        "B25013_001E",
        "B25013_002E",
        "B25013_007E",
    ]
    upload_sql_table_name = "raw_data_census_bureau_housing_market_ts"
    upload_fields = [
        "geo_level",
        "unique_geo_id",
        "delimited_geo_id",
        "year",
        "total_occupied_housing_units_data",
        "owner_occupied_housing_units_data",
        "renter_occupied_housing_units_data",
    ]
    sql_table_name = "raw_data_census_bureau_housing_market_ts"

    def process_data(self, data_dict):
        return self._process_data(data_dict)
