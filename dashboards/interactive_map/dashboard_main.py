import pandas as pd
import numpy as np

import dash.dcc as dcc
import dash.html as html
from dash.dependencies import Input, Output, State
import plotly.express as px


def build_dashboard(app, data_dict):
    # data for initial display
    geo_dict = data_dict["county"]["geojson"]
    plotdata_dict = data_dict["county"]["data"]

    data_stores = html.Div(
        [
            dcc.Store(id="all_data", data=data_dict),
            dcc.Store(id="geodata", data=geo_dict),
            dcc.Store(id="plotdata", data=plotdata_dict),
            dcc.Store(id="metadata-store", data={"geolevel": "county"}),
        ]
    )

    app.layout = html.Div(
        [
            html.H1("Select geography"),
            dcc.Dropdown(
                id="geolevel-dropdown",
                options=[
                    {"label": "Census Tract", "value": "census_tract"},
                    {"label": "County", "value": "county"},
                ],
                value="county",
            ),
            html.H1("Select variable"),
            dcc.Dropdown(id="display-variable-dropdown"),
            html.H1("Select year"),
            dcc.Dropdown(id="display-year-dropdown"),
            dcc.Graph(id="map_graph", style={"width": "100%", "height": "80vh"}),
            data_stores,
        ]
    )

    @app.callback(
        Output("display-variable-dropdown", "options"), Input("plotdata", "data")
    )
    def update_data_dropdown(plotdata):
        options = [
            {"label": col[:-5], "value": col}
            for col in pd.DataFrame(plotdata).columns
            if col.endswith("_data")
        ]
        return options

    @app.callback(Output("display-year-dropdown", "options"), Input("plotdata", "data"))
    def update_year_dropdown(plotdata):
        options = [
            {"label": year, "value": year}
            for year in sorted(pd.DataFrame(plotdata)["year"].unique())
        ]
        return options

    @app.callback(Output("metadata-store", "data"), Input("geolevel-dropdown", "value"))
    def update_metadata(geolevel):
        print(f"callback triggered with {geolevel} values")
        return {"geolevel": geolevel}

    @app.callback(
        Output("geodata", "data"),
        Output("plotdata", "data"),
        State("all_data", "data"),
        Input("metadata-store", "data"),
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
            range_color=(
                plotdata_df[display_var].min(),
                plotdata_df[display_var].max(),
            ),
            center={"lat": 36.6455249, "lon": -77.9564560},
            mapbox_style="carto-positron",
            zoom=3,
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

    return app
