import pandas as pd

import dash.dcc as dcc
import dash.html as html
from dash.dependencies import Input, Output, State
import plotly.express as px

GEOLEVEL_RELATIONSHIP = {
    "state": {"parent": None, "child": "county"},
    "county": {"parent": "state", "child": "census_tract"},
    "census_tract": {"parent": "county", "child": None},
}

layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1(
                    "Census Data Visualization",
                    style={"textAlign": "center", "marginBottom": "20px"},
                )
            ],
            style={"padding": "10px", "backgroundColor": "#f8f9fa"},
        ),
        # Controls Section
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Select geography"),
                        dcc.Dropdown(
                            id="geolevel-dropdown",
                            options=[
                                {"label": "Census Tract", "value": "census_tract"},
                                {"label": "County", "value": "county"},
                                {"label": "State", "value": "state"},
                            ],
                            value="county",
                        ),
                    ],
                    style={"marginBottom": "10px"},
                ),
                html.Div(
                    [
                        html.Label("Select variable"),
                        dcc.Dropdown(id="display-variable-dropdown"),
                    ],
                    style={"marginBottom": "10px"},
                ),
                html.Div(
                    [
                        html.Label("Select year"),
                        dcc.Dropdown(id="display-year-dropdown"),
                    ],
                ),
            ],
            style={
                "padding": "20px",
                "width": "25%",
                "float": "left",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "backgroundColor": "#ffffff",
            },
        ),
        html.Div(
            [
                dcc.Graph(id="map_graph", style={"width": "100%", "height": "80vh"}),
            ],
            style={"width": "70%", "float": "right", "padding": "20px"},
        ),
    ],
    style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#f5f5f5"},
)


def register_callbacks(app):
    @app.callback(
        Output("display-variable-dropdown", "options"),
        Output("display-variable-dropdown", "value"),
        Input("plotdata", "data"),
    )
    def update_data_dropdown(plotdata):
        data_columns = [
            col for col in pd.DataFrame(plotdata).columns if col.endswith("_data")
        ]

        options = [{"label": col[:-5], "value": col} for col in data_columns]
        default_value = data_columns[0]

        return options, default_value

    @app.callback(
        Output("display-year-dropdown", "options"),
        Output("display-year-dropdown", "value"),
        Input("plotdata", "data"),
    )
    def update_year_dropdown(plotdata):
        year_options = [
            year for year in sorted(pd.DataFrame(plotdata)["year"].unique())
        ]

        options = [{"label": year, "value": year} for year in year_options]
        default_value = year_options[0]

        return options, default_value

    @app.callback(
        Output("metadata-level", "data"),
        Input("geolevel-dropdown", "value"),
    )
    def update_metadata(geolevel):
        print(f"callback triggered with {geolevel} values")
        return {
            "geolevel": geolevel,
            "geolevel_parent": GEOLEVEL_RELATIONSHIP[geolevel]["parent"],
            "geolevel_child": GEOLEVEL_RELATIONSHIP[geolevel]["child"],
        }

    @app.callback(
        Output("geodata", "data"),
        Output("plotdata", "data"),
        State("all_data", "data"),
        Input("metadata-level", "data"),
    )
    def update_plotdata(all_data, metadata):
        geolevel = metadata["geolevel"]

        geolevel_data_dict = all_data.get(geolevel, {})
        geo_dict = geolevel_data_dict.get("geojson", {})
        data_dict = geolevel_data_dict.get("data", {})
        return geo_dict, data_dict

    @app.callback(
        Output("map_graph", "figure"),
        State("geodata", "data"),
        Input("plotdata", "data"),
        Input("display-variable-dropdown", "value"),
        Input("display-year-dropdown", "value"),
    )
    def update_map(geodata, plotdata, display_var, display_year):
        plotdata_df = pd.DataFrame(plotdata)
        plotdata_df = plotdata_df[plotdata_df["year"] == display_year]

        print("rendering map")
        fig = px.choropleth_mapbox(
            plotdata_df,
            geojson=geodata,
            featureidkey="properties.name",
            locations="name",
            color=display_var,
            color_continuous_scale="Turbo",
            custom_data=["unique_geo_id", "delimited_geo_id"],
            range_color=(
                plotdata_df[display_var].min(),
                plotdata_df[display_var].max(),
            ),
            center={"lat": 36.6455249, "lon": -77.9564560},
            mapbox_style="carto-positron",
            zoom=6,
            opacity=0.2,
        )

        #        mapbox_access_token = "pk.eyJ1IjoiYWJlbnRsZXk5MDUiLCJhIjoiY2x6ZWsyZ3FhMHphNzJscHE4YXVnYm1wZSJ9.WMQOh4wkglYc1ypQUAaIrg"

        # fig.update_layout(
        #     mapbox_style="mapbox://styles/mapbox/streets-v11",  # High-resolution Mapbox style
        #     mapbox_accesstoken=mapbox_access_token,
        #     mapbox_zoom=15,  # Increase zoom level
        #     mapbox_center={"lat": 36.6455249, "lon": -77.9564560},
        #     margin={"r": 0, "t": 0, "l": 0, "b": 0},
        # )

        return fig

    @app.callback(
        Output("metadata-location", "data"),
        Input("map_graph", "clickData"),
        State("metadata-level", "data"),
    )
    def store_selected_subgeo(click_data, metadata_level):
        if click_data:
            unique_geo_id = click_data["points"][0]["customdata"][
                0
            ]  # pull the unique_geo_id
            delimited_geo_id = click_data["points"][0]["customdata"][
                1
            ]  # pull the unique_geo_id
            return {
                "unique_geo_id": unique_geo_id,
                "delimited_geo_id": delimited_geo_id,
            }

        return None
