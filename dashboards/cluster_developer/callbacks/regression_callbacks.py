from dash import callback
import dash.html as html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


from av_core.regression_tools.regression_tools import OLSRegressionGenerator

import dashboard_tools.callback_functions as cbf
from dashboard_tools.dashboard_utils import serialize_model, deserialize_model

GEOLEVEL_RELATIONSHIP = {
    "state": {"parent": None, "child": "county"},
    "county": {"parent": "state", "child": "census_tract"},
    "census_tract": {"parent": "county", "child": None},
}

cbf.get_data_variables_callback("regression-input-variable-checklist")
cbf.create_display_year_dropdown(
    "regression-display-year-dropdown", "plotdata-regression"
)
cbf.get_data_variables_callback("regression-output-variable")


@callback(
    Output("metadata-level", "data", allow_duplicate=True),
    Input("regression-geolevel-dropdown", "value"),
    prevent_initial_call=True,
)
def update_metadata_regression(geolevel):
    print(f"callback triggered with {geolevel} values")
    return {
        "geolevel": geolevel,
        "geolevel_parent": GEOLEVEL_RELATIONSHIP[geolevel]["parent"],
        "geolevel_child": GEOLEVEL_RELATIONSHIP[geolevel]["child"],
    }


@callback(
    Output("geodata", "data", allow_duplicate=True),
    Output("plotdata", "data", allow_duplicate=True),
    State("all_data", "data"),
    Input("metadata-level", "data"),
    prevent_initial_call=True,
)
def update_plotdata_regression(all_data, metadata):
    geolevel = metadata["geolevel"]

    geolevel_data_dict = all_data.get(geolevel, {})
    geo_dict = geolevel_data_dict.get("geojson", {})
    data_dict = geolevel_data_dict.get("data", {})

    return geo_dict, data_dict


@callback(
    Output("regressionmodel", "data"),
    Input("run-regression", "n_clicks"),
    State("plotdata", "data"),
    State("regression-input-variable-checklist", "value"),
    State("regression-output-variable", "value"),
    State("regression-display-year-dropdown", "value"),
)
def run_regression(n_clicks, plotdata, input_columns, output_column, display_year):
    if n_clicks == 0:
        return []

    plotdata_df = pd.DataFrame(plotdata)
    plotdata_df = plotdata_df[plotdata_df["year"] == display_year]
    columns = input_columns + [output_column]
    regression_generator = OLSRegressionGenerator(plotdata_df[columns], output_column)
    regression_generator.fit()

    return serialize_model(regression_generator.ols_model)


@callback(Output("regression-summary", "children"), Input("regressionmodel", "data"))
def display_regression_summary(model_data):
    if model_data is None:
        return "No model trained yet."

    model = deserialize_model(model_data)

    summary_html_tables = model.summary().tables

    return html.Div(
        [
            html.Iframe(
                srcDoc=summary_html_tables[0].as_html(),
                style={"width": "100%", "height": "260px", "border": "none"},
            ),
            html.Iframe(
                srcDoc=summary_html_tables[1].as_html(),
                style={"width": "100%", "height": "165px", "border": "none"},
            ),
            html.Iframe(
                srcDoc=summary_html_tables[2].as_html(),
                style={"width": "100%", "height": "125px", "border": "none"},
            ),
        ]
    )


@callback(Output("residual_graph", "figure"), Input("regressionmodel", "data"))
def display_residual_summary(model_data):
    if model_data is None:
        return "No model trained yet."

    model = deserialize_model(model_data)
    residuals = model.resid
    predicted = model.fittedvalues

    fig = px.scatter(
        x=predicted,
        y=residuals,
        labels={"x": "Predicted Values", "y": "Residuals"},
        title="Residuals vs Predicted",
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red")

    return fig


@callback(Output("histogram_graph", "figure"), Input("regressionmodel", "data"))
def display_historgram_summary(model_data):
    if model_data is None:
        return "No model trained yet."

    model = deserialize_model(model_data)
    residuals = model.resid

    fig = px.histogram(
        residuals,
        nbins=20,
        labels={"x": "Residuals", "y": "Frequency"},
        title="Histogram of Residuals",
    )
    fig.add_vline(x=0, line_dash="dash", line_color="red")

    return fig


@callback(
    Output("standarized_residuals_graph", "figure"), Input("regressionmodel", "data")
)
def display_standardized_residuals(model_data):
    if model_data is None:
        return "No model trained yet."

    model = deserialize_model(model_data)
    residuals = model.resid
    predicted = model.fittedvalues

    std_residuals = residuals / np.std(residuals)

    fig = px.scatter(
        x=predicted,
        y=std_residuals,
        labels={"x": "Predicted Values", "y": "Standardized Residuals"},
        title="Standarized Residuals vs Predicted",
    )
    fig.add_hline(y=2, line_dash="dash", line_color="red")
    fig.add_hline(y=-2, line_dash="dash", line_color="red")

    return fig


@callback(
    Output("leverage_residuals_graph", "figure"), Input("regressionmodel", "data")
)
def display_influence_residuals(model_data):
    if model_data is None:
        return "No model trained yet."

    model = deserialize_model(model_data)
    influence = model.get_influence()
    leverage = influence.hat_matrix_diag
    cooks_d = influence.cooks_distance[0]

    fig = px.scatter(
        x=leverage,
        y=cooks_d,
        labels={"x": "Predicted Values", "y": "Standardized Residuals"},
        title="Leverage vs Residuals (Cook's Distance)",
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red")

    return fig
