import geopandas as gpd
import json
import pandas as pd
from pathlib import Path
import pickle

from core.utils import load_config

from collect_census_ts_data import get_ts_data

DASHBOARD_VARIABLES = ["NAME", "B01001_001E", "B01002_001E", "B19013_001E"]


def get_shapefiles(config):
    """The shapefile data will need to reorganized at some point."""

    # collect and process geographic shape file data
    counties_shape = gpd.read_file(config["shapefiles"]["counties"]["path"])
    counties_shape["geometry"] = counties_shape["geometry"].simplify(
        tolerance=0.01, preserve_topology=True
    )

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

    return counties_shape, census_tracts_shape


def get_regional_data(api_call_dict, regional_shape_df, geolevel="county"):
    join_columns = {
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
    counties_shape, census_tract_shape = get_shapefiles(config)

    ### Data Load ###

    api_call_dict = {
        "type_": "acs1",
        "variables": DASHBOARD_VARIABLES,
        "state": ["51"],
        "county": ["*"],
        "begin_year": 2021,
        "end_year": 2023,
    }

    county_data_dict = get_regional_data(api_call_dict, counties_shape)

    # census_tract data
    api_call_dict = {
        "type_": "acs5",
        "variables": DASHBOARD_VARIABLES,
        "state": ["51"],
        "tract": ["*"],
        "begin_year": 2021,
        "end_year": 2023,
    }

    census_tract_dict = get_regional_data(
        api_call_dict, census_tract_shape, geolevel="tract"
    )

    # aggregate data
    data_dict = {
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
