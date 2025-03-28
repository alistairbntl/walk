from dash import dcc, html, register_page

import dashboard_tools.dashboard_controls as dc

from stores.cluster_stores import cluster_stores
import callbacks.cluster_callbacks

register_page(__name__, path="/cluster")


layout = html.Div(
    [
        *cluster_stores,
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
        # Controls and map
        html.Div(
            [
                # Controls Section
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Select geography"),
                                dcc.Dropdown(
                                    id="cluster-geolevel-dropdown",
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
                                dcc.Dropdown(id="cluster-display-year-dropdown"),
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
                                    id="cluster-num-clusters",
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
                            id="cluster-map-graph",
                            style={"width": "100%", "height": "80vh"},
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
                dcc.Graph(
                    id="cluster-dendrogram-graph", style={"flex": "1", "margin": "10px"}
                ),
                dcc.Graph(
                    id="cluster-elbow-graph", style={"flex": "1", "margin": "10px"}
                ),
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
                dcc.Graph(
                    id="cluster-silhouette-graph", style={"flex": "1", "margin": "10px"}
                ),
                dcc.Graph(
                    id="cluster-pairplot-graph", style={"flex": "1", "margin": "10px"}
                ),
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
                dcc.Graph(
                    id="cluster-radar-graph", style={"flex": "1", "margin": "10px"}
                ),
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
