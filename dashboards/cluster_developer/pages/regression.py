from dash import register_page
import dash.dcc as dcc
import dash.html as html

import dashboard_tools.dashboard_controls as dc
from stores.regression_stores import regression_stores

register_page(__name__, path="/regression")


header = dc.create_header("Regression Analysis Dashboard")

controls = html.Div(
    [
        html.Div(
            [
                dc.create_geolevel_dropdown("regression"),
                dc.create_variable_checklist(
                    "Regression Independent Variables",
                    "regression-input-variable-checklist",
                ),
                dc.create_year_dropdown("regression-display-year-dropdown"),
                dc.create_dropdown(
                    "Regression Dependent Variable", "regression-output-variable"
                ),
                dc.create_button("Run Regression", "run-regression"),
            ],
            style={
                "padding": "20px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "backgroundColor": "#ffffff",
                "flex": "1",
            },
        ),
        html.Div([html.Div(id="regression-summary")], style={"flex": "2"}),
    ],
    style={
        "display": "flex",
        "flexDirection": "row",
        "marginBottom": "20px",
        "maxWidth": "2000px",
        "margin": "0 auto",
    },
)

analysis = html.Div(
    [
        html.Div(
            [
                dcc.Graph(id="histogram_graph", style={"flex": "1", "margin": "10px"}),
                dcc.Graph(id="residual_graph", style={"flex": "1", "margin": "10px"}),
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
                    id="leverage_residuals_graph", style={"flex": "1", "margin": "10px"}
                ),
                dcc.Graph(
                    id="standarized_residuals_graph",
                    style={"flex": "1", "margin": "10px"},
                ),
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "maxWidth": "2000px",
                "margin": "0 auto",
            },
        ),
    ]
)
layout = html.Div([header, controls, analysis])
