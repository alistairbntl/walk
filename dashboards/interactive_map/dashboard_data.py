import json
import pandas as pd
from pathlib import Path
import pickle

from core.utils import load_config, get_db_manager

from load_shapefiles import get_shapefiles

DASHBOARD_VARIABLES = {}


def get_regional_data(regional_shape_df, geolevel="county"):
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

    # run sql queries to load_data
    regional_data_df = get_data(geolevel)

    # filter shape file to only include counties with data
    regional_df = pd.merge(
        regional_shape_df,
        regional_data_df,
        left_on="GEOID",
        right_on="unique_geo_id",
    )

    regional_geojson = json.loads(regional_df[geo_columns["geojson_cols"]].to_json())

    regional_data = regional_data_df.to_dict("records")

    return {"data": regional_data, "geojson": regional_geojson}


def get_data(geolevel):
    sql_file_path = "load_data.sql"
    with open(sql_file_path, "r") as file:
        sql_script = file.read()

    db_manager = get_db_manager()

    return_df = db_manager.query_to_df(sql_script)

    return return_df.query(f"geo_level=='{geolevel}'").reset_index()


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

    state_data_dict = get_regional_data(shapes_dict["states_shape"], geolevel="state")

    county_data_dict = get_regional_data(
        shapes_dict["counties_shape"], geolevel="county"
    )

    census_tract_dict = get_regional_data(
        shapes_dict["census_tracts_shape"], geolevel="tract"
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
