import pandas as pd

from av_core.api_tools.API_requests import make_api_call

from core.utils import get_db_manager


def variables_to_df(variables: dict) -> pd.DataFrame:
    data = []
    for var_id, details in variables.items():
        data.append(
            {
                "variable_id": var_id,
                "description": details.get("label"),
                "group": details.get("group"),
                "concept": details.get("concept"),
                "predicate_type": details.get("predicateType"),
                "limit": details.get("limit"),
                "attributes": details.get("attributes"),
            }
        )

    return pd.DataFrame(data)


def process_variables(variables_df, year, data_set) -> pd.DataFrame:
    variables_df = variables_df.query("group != 'N/A'")

    variables_df["year"] = year
    variables_df["data_set"] = data_set

    return variables_df


def collect_and_upload_census_bureau_variable_info(year, data_set, db_manager):
    url = f"https://api.census.gov/data/{year}/acs/{data_set}/variables.json"
    headers = {"Accept": "application/json"}
    response = make_api_call(url, headers=headers)

    # if the api call fails, return
    if response is None:
        return

    variables = response["variables"]

    variables_df = variables_to_df(variables)
    variables_df = process_variables(variables_df, year, data_set)

    groups_df = variables_df[["year", "data_set", "group", "concept"]].drop_duplicates()

    db_manager.df_to_sql_table(
        groups_df[["group", "concept", "year", "data_set"]],
        "census_bureau_data_groups",
        if_exists="append",
    )

    db_manager.df_to_sql_table(
        variables_df[
            [
                "variable_id",
                "group",
                "description",
                "predicate_type",
                "limit",
                "attributes",
                "year",
                "data_set",
            ]
        ],
        "census_bureau_variables",
        if_exists="append",
    )


def main():
    years = range(2005, 2024)
    data_set = "acs5"
    print("...loading data to database...")
    db_manager = get_db_manager()

    for year in years:
        collect_and_upload_census_bureau_variable_info(year, data_set, db_manager)


if __name__ == "__main__":
    main()
