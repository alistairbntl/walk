from dash import callback, Input, Output, State
import dash.html as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


from av_core.regression_tools.regression_tools import OLSRegressionGenerator

import dashboard_tools.callback_functions as cbf
from dashboard_tools.dashboard_utils import serialize_model, deserialize_model

METADATA = "regression-metadata-level"
PLOTDATA = "regression-plotdata"
GEODATA = "regression-geodata"
MODEL = "regression-model"


cbf.get_data_variables_callback("regression-input-variable-checklist")
cbf.create_display_year_dropdown("regression-display-year-dropdown", PLOTDATA)
cbf.get_data_variables_callback("regression-output-variable")


@callback(
    Output(METADATA, "data"),
    Input("regression-geolevel-dropdown", "value"),
)
def update_metadata_regression(geolevel):
    GEOLEVEL_RELATIONSHIP = {
        "state": {"parent": None, "child": "county"},
        "county": {"parent": "state", "child": "census_tract"},
        "census_tract": {"parent": "county", "child": None},
    }
    return {
        "geolevel": geolevel,
        "geolevel_parent": GEOLEVEL_RELATIONSHIP[geolevel]["parent"],
        "geolevel_child": GEOLEVEL_RELATIONSHIP[geolevel]["child"],
    }


@callback(
    Output(GEODATA, "data"),
    Output(PLOTDATA, "data"),
    State("all_data", "data"),
    Input(METADATA, "data"),
)
def update_plotdata_regression(all_data, metadata):
    geolevel = metadata["geolevel"]

    geolevel_data_dict = all_data.get(geolevel, {})
    geo_dict = geolevel_data_dict.get("geojson", {})
    data_dict = geolevel_data_dict.get("data", {})

    return geo_dict, data_dict


@callback(
    Output(MODEL, "data"),
    Input("run-regression", "n_clicks"),
    State(PLOTDATA, "data"),
    State("regression-input-variable-checklist", "value"),
    State("regression-output-variable", "value"),
    State("regression-display-year-dropdown", "value"),
)
def run_regression(n_clicks, plotdata, input_columns, output_column, display_year):
    if n_clicks == 0:
        return []

    df = pd.DataFrame(plotdata)
    df = df[df["year"] == display_year]
    regression_generator = OLSRegressionGenerator(
        df[input_columns + [output_column]], output_column
    )
    regression_generator.fit()

    return serialize_model(regression_generator.ols_model)


@callback(Output("regression-summary", "children"), Input(MODEL, "data"))
def display_regression_summary(model_data):
    if model_data is None:
        return "No model trained yet."

    model = deserialize_model(model_data)

    tables = model.summary().tables
    heights = ["260px", "165px", "125px"]
    return html.Div(
        [
            html.Iframe(
                srcDoc=table.as_html(),
                style={"width": "100%", "height": height, "border": "none"},
            )
            for table, height in zip(tables, heights)
        ]
    )


@callback(Output("residual_graph", "figure"), Input(MODEL, "data"))
def display_residual_summary(model_data):
    if model_data is None:
        return go.Figure()

    model = deserialize_model(model_data)

    return px.scatter(
        x=model.fittedvalues,
        y=model.resid,
        labels={"x": "Predicted Values", "y": "Residuals"},
        title="Residuals vs Predicted",
    ).add_hline(y=0, line_dash="dash", line_color="red")


@callback(Output("histogram_graph", "figure"), Input(MODEL, "data"))
def display_historgram_summary(model_data):
    if model_data is None:
        return go.Figure()

    model = deserialize_model(model_data)

    return px.histogram(
        model.resid,
        nbins=20,
        labels={"x": "Residuals", "y": "Frequency"},
        title="Histogram of Residuals",
    ).add_vline(x=0, line_dash="dash", line_color="red")


@callback(Output("standarized_residuals_graph", "figure"), Input(MODEL, "data"))
def display_standardized_residuals(model_data):
    if model_data is None:
        return go.Figure()

    model = deserialize_model(model_data)

    std_residuals = model.resid / np.std(model.resid)

    fig = (
        px.scatter(
            x=model.fittedvalues,
            y=std_residuals,
            labels={"x": "Predicted Values", "y": "Standardized Residuals"},
            title="Standarized Residuals vs Predicted",
        )
        .add_hline(y=2, line_dash="dash", line_color="red")
        .add_hline(y=-2, line_dash="dash", line_color="red")
    )

    return fig


@callback(Output("leverage_residuals_graph", "figure"), Input(MODEL, "data"))
def display_influence_residuals(model_data):
    if model_data is None:
        return go.Figure()

    model = deserialize_model(model_data)
    influence = model.get_influence()
    leverage = influence.hat_matrix_diag
    cooks_d = influence.cooks_distance[0]

    return px.scatter(
        x=leverage,
        y=cooks_d,
        labels={"x": "Predicted Values", "y": "Standardized Residuals"},
        title="Leverage vs Residuals (Cook's Distance)",
    ).add_hline(y=0, line_dash="dash", line_color="red")
