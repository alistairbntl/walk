import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


def build_dashboard(app, data_dict):
    geo_dict = data_dict["county"]["geojson"]
    plotdata_dict = data_dict["county"]["data"]

    data_stores = html.Div(
        [
            dcc.Store(id="all-data", data=data_dict),
        ]
    )

    nav_bar = dbc.NavbarSimple(
        brand="Navigation",
        color="primary",
        dark=True,
        children=[
            dbc.NavItem(dcc.Link("Home", href="/", className="nav-link")),
            dbc.NavItem(dcc.Link("Cluster", href="/cluster", className="nav_link")),
            dbc.NavItem(
                dcc.Link("Regression", href="/regression", className="nav_link")
            ),
        ],
    )

    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content"),
            nav_bar,
            data_stores,
            dash.page_container,
        ]
    )

    return app
