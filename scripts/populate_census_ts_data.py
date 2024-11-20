import pandas as pd

from av_core.api_tools.API_requests import make_api_call
from av_core.db_tools.sqlite_manager import SQLiteManager

from core.CensusAPI import CensusAPIConfig
from core.utils import load_config


def clean_api_df(df_, db_manager):
    data_description_df = db_manager.query_to_df("SELECT * FROM census_table_ids")

    column_rename_dict = pd.Series(
        data_description_df["data_description"].values + "_data",
        index=data_description_df["table_id"],
    ).to_dict()
    column_dtype_dict = pd.Series(
        data_description_df["dtype"].values,
        index=data_description_df["data_description"] + "_data",
    ).to_dict()
    df_ = df_.rename(columns=column_rename_dict)
    df_ = df_.astype(column_dtype_dict)

    return df_


def build_ts_data_set(begin_year=2005, end_year=2023):
    dataframes = []
    for year in range(begin_year, end_year + 1):
        print(f"...downloading data for year {year}...")
        cac = CensusAPIConfig(
            year=year,
            dataset="acs",
            type_="acs1",
            variables=["B01001_001E", "B01002_001E", "B19013_001E"],
            tract=None,
            state=["51"],
            county=[],
        )

        headers = {"Content-Type": "application/json"}
        try:
            data = make_api_call(cac.build_data_query_url(), headers=headers)
            df_ = pd.DataFrame(data[1:], columns=data[0])
            df_["year"] = year

            dataframes.append(df_)

        except:
            print(f"...error processing data for year {year}...")
            continue

    final_df = pd.concat(dataframes, ignore_index=True)

    return final_df


def main():
    config = load_config()
    db_manager = SQLiteManager(config["database"]["path"])

    print("building data set...")
    df_ = build_ts_data_set()

    print("cleaning output df...")
    df_ = clean_api_df(df_, db_manager)

    print("exporting data to sql...")
    db_manager.df_to_sql_table(df_, "census_ts_data", if_exists="append")

    db_manager.close()


if __name__ == "__main__":
    main()
