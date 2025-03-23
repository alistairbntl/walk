import pandas as pd

import dash.dcc as dcc
import dash.html as html
from dash import register_page, callback
from dash.dependencies import Input, Output, State
import plotly.express as px

from av_core.clustering_tools.cluster_tools import ClusterAnalyzer, ClusterGenerator
from av_core.visualize_tools.graph_builders import create_radar_plot

from core.pd_utils import absolute_value_scaling
import dashboard_tools.callback_functions as cbf
import dashboard_tools.dashboard_controls as dc

register_page(__name__, path="/cluster")

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
                    "Cluster Analysis Dashboard",
                    style={"textAlign": "center", "marginBottom": "20px"},
                )
            ],
            style={"padding": "10px", "backgroundColor": "#f8f9fa"},
        ),
        html.Div(
            [
                # Controls Section
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Select geography"),
                                dcc.Dropdown(
                                    id="geolevel-dropdown",
                                    options=[
                                        {
                                            "label": "Census Tract",
                                            "value": "census_tract",
                                        },
                                        {"label": "County", "value": "county"},
                                    ],
                                    value="county",
                                ),
                            ],
                            style={"marginBottom": "10px"},
                        ),
                        html.Div(
                            [
                                html.Label("Select cluster variables"),
                                dcc.Checklist(
                                    id="cluster-variable-checklist",
                                    style={"fontSize": "18px"},
                                    inputStyle={
                                        "marginRight": "10px",
                                        "alignSelf": "center",
                                    },
                                    labelStyle={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "10px",
                                    },
                                    value=["normalized_population_density_data"],
                                ),
                            ],
                            style={"marginBottom": "10px"},
                        ),
                        html.Div(
                            [
                                html.Label("Select year"),
                                dcc.Dropdown(id="display-year-dropdown"),
                            ],
                            style={"marginBottom": "10px"},
                        ),
                        dc.create_button(
                            "Analyze Number of Clusters", "analyze-num-clusters-button"
                        ),
                        html.Div(
                            [
                                html.Label("Enter number of clusters"),
                                dcc.Dropdown(
                                    id="num-clusters",
                                    options=[
                                        {"label": str(num), "value": num}
                                        for num in range(2, 25)
                                    ],
                                    value=2,
                                ),
                            ],
                            style={"margin": "10px"},
                        ),
                    ],
                    style={
                        "padding": "20px",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                        "backgroundColor": "#ffffff",
                        "flex": "1",
                    },
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="map-graph", style={"width": "100%", "height": "80vh"}
                        )
                    ],
                    style={"padding": "20px", "flex": "2"},
                ),
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "marginBottom": "20px",
                "maxWidth": "2000px",
                "margin": "0 auto",
            },
        ),
        html.Div(
            [
                dcc.Graph(id="dendrogram-graph", style={"flex": "1", "margin": "10px"}),
                dcc.Graph(id="elbow-graph", style={"flex": "1", "margin": "10px"}),
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "maxWidth": "2000px",
                "margin": "0 auto",
            },
        ),
        html.Div(
            [
                dcc.Graph(id="silhouette-graph", style={"flex": "1", "margin": "10px"}),
                dcc.Graph(id="pairplot-graph", style={"flex": "1", "margin": "10px"}),
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "maxWidth": "2000px",
                "margin": "0 auto",
            },
        ),
        html.Div(
            [
                dcc.Graph(id="radar-graph", style={"flex": "1", "margin": "10px"}),
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "maxWidth": "2000px",
                "margin": "0 auto",
            },
        ),
    ],
    style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#f5f5f5"},
)

cbf.get_data_variables_callback("cluster-variable-checklist")
cbf.create_display_year_dropdown("display-year-dropdown", "plotdata-cluster")


@callback(Output("metadata-level-cluster", "data"), Input("geolevel-dropdown", "value"))
def update_metadata(geolevel):
    print(f"callback triggered with {geolevel} values")
    return {
        "geolevel": geolevel,
        "geolevel_parent": GEOLEVEL_RELATIONSHIP[geolevel]["parent"],
        "geolevel_child": GEOLEVEL_RELATIONSHIP[geolevel]["child"],
    }


@callback(
    Output("geodata-cluster", "data", allow_duplicate=True),
    Output("plotdata-cluster", "data", allow_duplicate=True),
    State("all-data", "data"),
    Input("metadata-level-cluster", "data"),
    prevent_initial_call=True,
)
def update_plotdata(all_data, metadata):
    geolevel = metadata["geolevel"]

    geolevel_data_dict = all_data.get(geolevel, {})
    geo_dict = geolevel_data_dict.get("geojson", {})
    data_dict = geolevel_data_dict.get("data", {})

    return geo_dict, data_dict


@callback(
    Output("map-graph", "figure"),
    State("geodata-cluster", "data"),
    Input("clusterdata", "data"),
)
def update_map(geodata, plotdata):
    plotdata_df = pd.DataFrame(plotdata)

    print("rendering map")
    fig = px.choropleth_mapbox(
        plotdata_df,
        geojson=geodata,
        featureidkey="properties.name",
        locations="name",
        color="cluster_labels",
        color_continuous_scale="Turbo",
        range_color=(
            plotdata_df["cluster_labels"].min(),
            plotdata_df["cluster_labels"].max(),
        ),
        center={"lat": 36.6455249, "lon": -77.9564560},
        mapbox_style="carto-positron",
        zoom=6,
        opacity=0.2,
    )

    return fig


@callback(
    Output("cluster-columns", "data"),
    Input("analyze-num-clusters-button", "n_clicks"),
    State("cluster-variable-checklist", "value"),
)
def get_cluster_columns(n_clicks, selected_columns):
    if n_clicks > 0:
        return selected_columns
    return []


@callback(
    Output("elbow-graph", "figure"),
    Input("plotdata-cluster", "data"),
    Input("cluster_columns", "data"),
    Input("display-year-dropdown", "value"),
)
def plot_elbow_graph(plotdata, cluster_columns, display_year):
    plotdata_df = pd.DataFrame(plotdata)
    plotdata_df = plotdata_df[plotdata_df["year"] == display_year]

    cluster_analyzer = ClusterAnalyzer(plotdata_df[cluster_columns])

    return cluster_analyzer.plotly_elbow_graph()


@callback(
    Output("dendrogram-graph", "figure"),
    Input("plotdata-cluster", "data"),
    Input("cluster_columns", "data"),
    Input("display-year-dropdown", "value"),
)
def plot_dendrogram_graph(plotdata, cluster_columns, display_year):
    plotdata_df = pd.DataFrame(plotdata)
    plotdata_df = plotdata_df[plotdata_df["year"] == display_year]

    cluster_analyzer = ClusterAnalyzer(plotdata_df[cluster_columns])

    return cluster_analyzer.plotly_dendrogram_graph()


@callback(
    Output("clusterdata", "data"),
    Input("num-clusters", "value"),
    State("plotdata-cluster", "data"),
    State("cluster_columns", "data"),
    State("display-year-dropdown", "value"),
)
def generate_clusters(num_clusters, plotdata, cluster_columns, display_year):
    plotdata_df = pd.DataFrame(plotdata)
    plotdata_df = plotdata_df[plotdata_df["year"] == display_year]
    cluster_generator = ClusterGenerator(
        plotdata_df[cluster_columns], n_clusters=num_clusters
    )

    cluster_generator.fit()
    cluster_labels = cluster_generator.get_cluster_labels()

    cluster_df = plotdata_df[["unique_geo_id", "geo_level", "year", "name"]].copy()
    cluster_df["cluster_labels"] = cluster_labels

    clusterdata = cluster_df.to_dict("records")

    return clusterdata


@callback(
    Output("silhouette-graph", "figure"),
    Input("num-clusters", "value"),
    State("plotdata-cluster", "data"),
    State("cluster_columns", "data"),
    State("display-year-dropdown", "value"),
)
def silhouette_graph(num_clusters, plotdata, cluster_columns, display_year):
    plotdata_df = pd.DataFrame(plotdata)
    plotdata_df = plotdata_df[plotdata_df["year"] == display_year]
    cluster_generator = ClusterGenerator(
        plotdata_df[cluster_columns], n_clusters=num_clusters
    )

    cluster_generator.fit()

    return cluster_generator.plotly_silhouette_graph()


@callback(
    Output("pairplot-graph", "figure"),
    Input("num-clusters", "value"),
    State("plotdata-cluster", "data"),
    State("cluster-columns", "data"),
    State("display-year-dropdown", "value"),
)
def pairplot_graph(num_clusters, plotdata, cluster_columns, display_year):
    plotdata_df = pd.DataFrame(plotdata)
    plotdata_df = plotdata_df[plotdata_df["year"] == display_year]
    cluster_generator = ClusterGenerator(
        plotdata_df[cluster_columns], n_clusters=num_clusters
    )

    cluster_generator.fit()

    return cluster_generator.plotly_pairplot()


@callback(
    Output("radar-graph", "figure"),
    Input("cluster-columns", "data"),
    Input("plotdata-cluster", "data"),
    Input("display-year-dropdown", "value"),
)
def radar_graph(cluster_columns, plotdata, display_year):
    plotdata_df = pd.DataFrame(plotdata)
    plotdata_df = plotdata_df[plotdata_df["year"] == display_year]

    plotdata_df[cluster_columns] = plotdata_df[cluster_columns].apply(
        absolute_value_scaling
    )

    plotdata_df = plotdata_df.query("unique_geo_id=='51001'")

    return create_radar_plot(plotdata_df, cluster_columns)
