import pandas as pd

from av_core.visualize_tools.graph_builders import create_multi_line_chart

from dash import html, dcc, Input, Output, State


def build_plot_ts(location, level, all_data) -> pd.DataFrame:
    all_locations_df = pd.DataFrame(all_data[level["geolevel"]]["data"])
    location_mask = all_locations_df["unique_geo_id"] == location["unique_geo_id"]
    location_df = all_locations_df[location_mask]

    # this needs to be set up to handle no parent locations case
    parent_geo_id = "".join(location["delimited_geo_id"].split("-")[:-1])
    all_parent_locations_df = pd.DataFrame(all_data[level["geolevel_parent"]]["data"])
    parent_location_mask = all_parent_locations_df["unique_geo_id"] == parent_geo_id
    parent_location_df = all_parent_locations_df[parent_location_mask]

    concat_columns = (
        ["name", "year"]
        + [col for col in location_df.columns if "_data" in col]
        + ["unique_geo_id"]
    )

    return_df = pd.concat(
        [location_df[concat_columns], parent_location_df[concat_columns]],
        ignore_index=True,
    )

    return return_df.to_dict("records")


def generate_ts_plot(plotdata_df, plot_column, data_transform="level"):
    plotdata_df = plotdata_df.sort_values(["unique_geo_id", "year"])
    if data_transform == "diff":
        plotdata_df[plot_column] = plotdata_df.groupby("unique_geo_id")[
            plot_column
        ].diff()
    elif data_transform == "perc_chg":
        plotdata_df[plot_column] = (
            plotdata_df.groupby("unique_geo_id")[plot_column].pct_change() * 100
        )
    fig = create_multi_line_chart(plotdata_df, plot_column)

    return fig


demographic_charts = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    id="population-graph-dropdown",
                    options=[
                        {"label": "level", "value": "level"},
                        {"label": "diff", "value": "diff"},
                        {"label": "perc_chg", "value": "perc_chg"},
                    ],
                    value="level",
                    placeholder="select data transformation",
                ),
                dcc.Graph(id="population_graph"),
            ],
            className="chart-container",
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="median-age-graph-dropdown",
                    options=[
                        {"label": "level", "value": "level"},
                        {"label": "diff", "value": "diff"},
                        {"label": "perc_chg", "value": "perc_chg"},
                    ],
                    value="level",
                    placeholder="select data transformation",
                ),
                dcc.Graph(id="median_age_graph"),
            ],
            className="chart-container",
        ),
    ],
    className="row",
)

workforce_charts = html.Div(
    [
        html.Div(
            [
                dcc.Graph(id="education_less_hs_graph"),
            ],
            className="chart-container",
        ),
        html.Div(
            [
                dcc.Graph(id="education_college_degree_graph"),
            ],
            className="chart-container",
        ),
    ],
    className="row",
)

housing_charts = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    id="housing-units-dropdown",
                    options=[
                        {"label": "level", "value": "level"},
                        {"label": "diff", "value": "diff"},
                        {"label": "perc_chg", "value": "perc_chg"},
                    ],
                    value="level",
                    placeholder="select data transformation",
                ),
                dcc.Graph(id="housing_units_graph"),
            ],
            className="chart-container",
        ),
    ],
    className="row",
)

layout = html.Div(
    [
        html.Div(id="page_title"),
        html.H2("Demographics"),
        demographic_charts,
        html.H2("Workforce"),
        workforce_charts,
        html.H2("Housing Supply"),
        housing_charts,
        html.A("Back to Map", href="/"),
        dcc.Store(id="local-plot-data"),
    ]
)


def register_callbacks(app):
    @app.callback(
        Output("page_title", "children"),
        Input("metadata-location", "data"),
        State("plotdata", "data"),
    )
    def create_page_title(location, plotdata):
        plotdata_df = pd.DataFrame(plotdata)
        geodata_df = plotdata_df[
            plotdata_df["unique_geo_id"] == location["unique_geo_id"]
        ]
        name = geodata_df["name"].unique()[0]

        return html.H1(f"Detailed Regional View: {name}")

    @app.callback(
        Output("local-plot-data", "data"),
        Input("metadata-location", "data"),
        State("metadata-level", "data"),
        State("all_data", "data"),
    )
    def update_population_graph(location, level, all_data):
        return build_plot_ts(location, level, all_data)

    @app.callback(
        Output("population_graph", "figure"),
        Input("local-plot-data", "data"),
        Input("population-graph-dropdown", "value"),
    )
    def update_population_graph(local_plot_data, data_transform):
        plot_data_df = pd.DataFrame(local_plot_data)
        return generate_ts_plot(plot_data_df, "total_population_data", data_transform)

    @app.callback(
        Output("median_age_graph", "figure"),
        Input("local-plot-data", "data"),
        Input("median-age-graph-dropdown", "value"),
    )
    def update_details_page(local_plot_data, data_transform):
        plot_data_df = pd.DataFrame(local_plot_data)
        return generate_ts_plot(plot_data_df, "median_age_data", data_transform)

    @app.callback(
        Output("housing_units_graph", "figure"),
        Input("local-plot-data", "data"),
        Input("housing-units-dropdown", "value"),
    )
    def update_housing_units_graph(local_plot_data, data_transform):
        plot_data_df = pd.DataFrame(local_plot_data)
        return generate_ts_plot(
            plot_data_df, "total_occupied_housing_units_data", data_transform
        )

    @app.callback(
        Output("education_less_hs_graph", "figure"),
        Input("local-plot-data", "data"),
        Input("housing-units-dropdown", "value"),
    )
    def update_housing_units_graph(local_plot_data, data_transform):
        plot_data_df = pd.DataFrame(local_plot_data)
        return generate_ts_plot(plot_data_df, "percent_less_hs_data", data_transform)

    @app.callback(
        Output("education_college_degree_graph", "figure"),
        Input("local-plot-data", "data"),
        Input("housing-units-dropdown", "value"),
    )
    def update_housing_units_graph(local_plot_data, data_transform):
        plot_data_df = pd.DataFrame(local_plot_data)
        return generate_ts_plot(
            plot_data_df, "percent_college_degree_data", data_transform
        )
