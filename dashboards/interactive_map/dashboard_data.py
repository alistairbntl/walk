import geopandas as gpd
import json
import pandas as pd
from pathlib import Path
import pickle

from core.utils import load_config

from collect_census_ts_data import get_ts_data

DASHBOARD_VARIABLES = [
    "NAME",
    "B01001_001E",
    "B01002_001E",
    "B19013_001E",
    "B25013_001E",
    "B25013_002E",
    "B25013_007E",
    # education data
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


def get_shapefiles(config) -> dict:
    """The shapefile data will need to reorganized at some point."""

    # collect and process geographic shape file data

    # states
    states_shape = gpd.read_file(config["shapefiles"]["states"]["path"])
    states_shape["geometry"] = states_shape["geometry"].simplify(
        tolerance=0.01, preserve_topology=True
    )

    # counties
    counties_shape = gpd.read_file(config["shapefiles"]["counties"]["path"])
    counties_shape["geometry"] = counties_shape["geometry"].simplify(
        tolerance=0.01, preserve_topology=True
    )

    # census_tracts
    census_tracts_shape = gpd.read_file(
        config["shapefiles"]["virginia_census_tract"]["path"]
    )

    # identify census tracts in richmond surronding counties
    # limit to richmond because census tract shape data is very detailed
    richmond_counties = counties_shape[
        counties_shape["NAME"].isin(
            ["Richmond", "Henrico", "Chesterfield", "Hanover", "Goochland"]
        )
        & (counties_shape["STATEFP"] == "51")
        & (counties_shape["NAMELSAD"] != "Richmond County")
    ]
    census_tracts_shape = census_tracts_shape[
        census_tracts_shape["COUNTYFP"].isin(richmond_counties["COUNTYFP"].to_list())
    ].reset_index()

    return {
        "counties_shape": counties_shape,
        "census_tracts_shape": census_tracts_shape,
        "states_shape": states_shape,
    }


def compute_education_ratios(regional_data_df):
    """
    computes various percentages based on educational status
    """
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


def get_regional_data(api_call_dict, regional_shape_df, geolevel="county"):
    join_columns = {
        "state": {
            "left_on": ["STATEFP"],
            "right_on": ["state_id"],
            "geojson_cols": ["STATEFP", "name", "geometry"],
        },
        "county": {
            "left_on": ["STATEFP", "COUNTYFP"],
            "right_on": ["state_id", "county_id"],
            "geojson_cols": ["STATEFP", "COUNTYFP", "name", "geometry"],
        },
        "tract": {
            "left_on": ["STATEFP", "COUNTYFP", "TRACTCE"],
            "right_on": ["state_id", "county_id", "tract_id"],
            "geojson_cols": ["STATEFP", "COUNTYFP", "TRACTCE", "name", "geometry"],
        },
    }

    geo_columns = join_columns[geolevel]

    # make an API call to collect the county display data
    regional_data_df = get_ts_data(api_call_dict)

    regional_data_df = compute_education_ratios(regional_data_df)

    # concate the geo identifier columns to reate a unique geo id.
    # note, the order matters.  the column order should be defined
    # from biggests to smallest
    regional_data_df["unique_geo_id"] = regional_data_df[
        join_columns[geolevel]["right_on"]
    ].agg("".join, axis=1)
    regional_data_df["delimited_geo_id"] = regional_data_df[
        join_columns[geolevel]["right_on"]
    ].agg("-".join, axis=1)

    # filter shape file to only include counties with data
    regional_df = pd.merge(
        regional_shape_df,
        regional_data_df,
        left_on=geo_columns["left_on"],
        right_on=geo_columns["right_on"],
    )

    regional_geojson = json.loads(regional_df[geo_columns["geojson_cols"]].to_json())

    regional_data = regional_data_df.to_dict("records")

    return {"data": regional_data, "geojson": regional_geojson}


def main(rebuild_data=True, cache_results=True):
    ### Initialization Step ###
    config = load_config()

    ### try to return cached data before rebuilding ###
    if (
        Path(config["datacaches"]["interactive_map_data"]["path"]).expanduser().exists()
        and not rebuild_data
    ):
        with open(
            Path(config["datacaches"]["interactive_map_data"]["path"]).expanduser(),
            "rb",
        ) as f:
            data_dict = pickle.load(f)
        return data_dict

    ### Collect Shapefile Data ###
    shapes_dict = get_shapefiles(config)

    ### Data Load ###
    begin_year = 2021
    end_year = 2023

    api_call_dict = {
        "type_": "acs1",
        "variables": DASHBOARD_VARIABLES,
        "state": ["*"],
        "begin_year": begin_year,
        "end_year": end_year,
    }

    state_data_dict = get_regional_data(
        api_call_dict, shapes_dict["states_shape"], geolevel="state"
    )

    api_call_dict = {
        "type_": "acs5",
        "variables": DASHBOARD_VARIABLES,
        "state": ["51"],
        "county": ["*"],
        "begin_year": begin_year,
        "end_year": end_year,
    }

    county_data_dict = get_regional_data(api_call_dict, shapes_dict["counties_shape"])

    # census_tract data
    api_call_dict = {
        "type_": "acs5",
        "variables": DASHBOARD_VARIABLES,
        "state": ["51"],
        "tract": ["*"],
        "begin_year": begin_year,
        "end_year": end_year,
    }

    census_tract_dict = get_regional_data(
        api_call_dict, shapes_dict["census_tracts_shape"], geolevel="tract"
    )

    # aggregate data
    data_dict = {
        "state": state_data_dict,
        "county": county_data_dict,
        "census_tract": census_tract_dict,
    }

    # cache dashboard data for future retrival
    if cache_results:
        with open(
            Path(config["datacaches"]["interactive_map_data"]["path"]).expanduser(),
            "wb",
        ) as f:
            pickle.dump(data_dict, f)

    return data_dict


if __name__ == "__main__":
    main()
