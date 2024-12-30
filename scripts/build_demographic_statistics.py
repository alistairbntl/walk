import pandas as pd

from core.pd_utils import create_percent_change_columns, create_diff_change_columns
from core.utils import load_config, get_db_manager

from collect_census_ts_data import get_ts_data
from geo_metadata import GEO_METADATA
from load_shapefiles import get_shapefiles

DASHBOARD_VARIABLES = [
    "NAME",
    "B01001_001E",
    "B01002_001E",
]


def get_demographic_data(api_call_dict, shape_dict, geolevel="county"):
    geo_metadata = GEO_METADATA[geolevel]

    regional_data_df = get_ts_data(api_call_dict)

    # set geo ids
    regional_data_df["geo_id"] = regional_data_df[geo_metadata["right_on"]].agg(
        "".join, axis=1
    )
    regional_data_df["delimited_geo_id"] = regional_data_df[
        geo_metadata["right_on"]
    ].agg("".join, axis=1)

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


def load_data(begin_year, end_year):
    config = load_config()
    shape_dict = get_shapefiles(config)

    api_call_dict = {
        "type_": "acs1",
        "variables": DASHBOARD_VARIABLES,
        "state": ["*"],
        "begin_year": begin_year,
        "end_year": end_year,
    }

    state_data_df = get_demographic_data(api_call_dict, shape_dict, geolevel="state")

    api_call_dict = {
        "type_": "acs5",
        "variables": DASHBOARD_VARIABLES,
        "state": ["51"],
        "county": ["*"],
        "begin_year": begin_year,
        "end_year": end_year,
    }

    county_data_df = get_demographic_data(api_call_dict, shape_dict)

    # census_tract data
    api_call_dict = {
        "type_": "acs5",
        "variables": DASHBOARD_VARIABLES,
        "state": ["51"],
        "tract": ["*"],
        "begin_year": begin_year,
        "end_year": end_year,
    }

    census_tract_df = get_demographic_data(api_call_dict, shape_dict, geolevel="tract")

    return {
        "state": state_data_df,
        "county": county_data_df,
        "census_tract": census_tract_df,
    }


def main(begin_year, end_year):
    data_dict = load_data(begin_year, end_year)

    db_manager = get_db_manager()

    for region, df_ in data_dict.items():
        df_["geo_level"] = region
        db_manager.df_to_sql_table(
            df_[
                [
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
            ],
            "census_bureau_demographic_ts",
            if_exists="append",
        )


if __name__ == "__main__":
    main(2014, 2023)
