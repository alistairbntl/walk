"""
Provides helper functions for constructing time series of
Census Bureau data sets.
"""

import logging
import numpy as np
import pandas as pd

from av_core.api_tools.API_requests import make_api_call

from core.CensusAPI import CensusAPIConfig
from core.utils import get_db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POSSIBLE_GEO_COLUMNS = ["state", "county", "tract"]


def cast_column_datatypes(df_, api_data_dict, db_manager):
    """
    When data is originally pulled from the Census Bureau API, it often is pulled
    as a string datatype.

    This method collects the variables pulled and assigns the column the correct
    dtype according to the value prescribed in census_bureau_variables_display
    """
    # converts the variables to a sql friend format
    variables = api_data_dict["variables"]
    data_column_names = "({})".format(", ".join(f"'{item}'" for item in variables))

    column_name_query = f"""SELECT
                            variable_id,
                            dtype
                            FROM census_bureau_variables_display
                            WHERE variable_id in {data_column_names}
    """
    column_config = db_manager.query_to_df(column_name_query)

    # cast data columns to correct data type
    dtype_mapping = dict(zip(column_config["variable_id"], column_config["dtype"]))

    for col, dtype in dtype_mapping.items():
        if dtype == "int":
            df_[col] = df_[col].astype(float)
        if dtype == "float":
            df_[col] = df_[col].astype(float)
        if dtype == "string":
            df_[col] = df_[col].astype(str)

    return df_


def rename_df_columns(df_, api_data_dict, db_manager):
    """
    Renames dataframe columns from variable_id to human readable form.
    """
    variables = api_data_dict["variables"]
    data_column_names = "({})".format(", ".join(f"'{item}'" for item in variables))

    column_name_query = f"""SELECT
                            variable_id,
                            display_name,
                            dtype
                            FROM census_bureau_variables_display
                            WHERE variable_id in {data_column_names}
    """
    column_config = db_manager.query_to_df(column_name_query)

    # rename data columns
    column_rename_dict = pd.Series(
        column_config["display_name"].values + "_data",
        index=column_config["variable_id"],
    ).to_dict()
    # rename geo columns
    column_rename_dict["NAME"] = "name"
    column_rename_dict["state"] = "state_id"
    column_rename_dict["county"] = "county_id"
    column_rename_dict["tract"] = "tract_id"

    return df_.rename(columns=column_rename_dict)


def interpolate_missing_data(df_, api_call_dict):
    """
    Occasionally a year will be missing from the pulled data set.

    This method will replace missing values with a linear interpolation
    of the surronding data points.

    Future iterations will likely need to handle this different.
    """
    geo_columns = [col for col in POSSIBLE_GEO_COLUMNS if col in df_.columns]

    # interpolate missing values
    df_[api_call_dict["variables"]] = df_.groupby(geo_columns)[
        api_call_dict["variables"]
    ].apply(lambda group: group.interpolate(method="linear"))

    return df_


def build_ts_data_set(api_call_dict, begin_year=2005, end_year=2023):
    """
    Collects and organizes Census Bureau data for multiple years.
    """
    begin_year = api_call_dict.pop("begin_year", begin_year)
    end_year = api_call_dict.pop("end_year", end_year)

    dataframes = []
    missing_years = []

    for year in range(begin_year, end_year + 1):
        logger.info(f"...downloading data for year {year}...")

        api_call_dict["year"] = year

        cac = CensusAPIConfig(**api_call_dict)
        headers = {"Content-Type": "application/json"}
        data = make_api_call(cac.build_data_query_url(), headers)

        if data:
            df_ = pd.DataFrame(data[1:], columns=data[0])
            df_["year"] = year
            dataframes.append(df_)
        else:
            logger.info(f"...error processing data for year {year}...")
            missing_years.append(year)

    final_df = pd.concat(dataframes, ignore_index=True)

    final_df = add_missing_years(final_df, missing_years)

    return final_df


def add_missing_years(df_, missing_years):
    """
    Appends a row for missing years to each geography
    in the dataframe.
    """
    # add empty row for missing years
    geo_columns = [col for col in POSSIBLE_GEO_COLUMNS if col in df_.columns]
    unique_geo_combinations = df_[geo_columns].drop_duplicates()

    missing_rows = []
    for year in missing_years:
        for _, geo_combination in unique_geo_combinations.iterrows():
            row = geo_combination.to_dict()
            row["year"] = year
            for col in df_.columns:
                if col not in row:
                    row[col] = np.nan
            missing_rows.append(row)

    missing_df = pd.DataFrame(missing_rows)
    df_ = pd.concat([df_, missing_df], ignore_index=True)

    return df_.sort_values(by=geo_columns + ["year"]).reset_index(drop=True)


def get_ts_data(api_call_dict):
    db_manager = get_db_manager()

    logger.info("building data set...")
    df_ = build_ts_data_set(api_call_dict)

    logger.info("setting column dtype...")
    df_ = cast_column_datatypes(df_, api_call_dict, db_manager)

    logger.info("interpolate missing data points...")
    df_ = interpolate_missing_data(df_, api_call_dict)

    logger.info("cleaning output df...")
    df_ = rename_df_columns(df_, api_call_dict, db_manager)

    db_manager.close()

    return df_


if __name__ == "__main__":
    pass
