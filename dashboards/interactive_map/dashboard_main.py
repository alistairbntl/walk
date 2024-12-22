from dash import dcc, html
from dash.dependencies import Input, Output

from pages import dashboard_choropleth, dashboard_region_detail


def build_dashboard(app, data_dict):
    geo_dict = data_dict["county"]["geojson"]
    plotdata_dict = data_dict["county"]["data"]

    data_stores = html.Div(
        [
            dcc.Store(id="all_data", data=data_dict),
            dcc.Store(id="geodata", data=geo_dict),
            dcc.Store(id="plotdata", data=plotdata_dict),
            dcc.Store(
                id="metadata-level",
                data={"geolevel": "state"},
            ),
            dcc.Store(id="metadata-location", data={}),
        ]
    )

    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content"),
            data_stores,
        ]
    )

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def render_page(pathname):
        if pathname == "/region_detail":
            return dashboard_region_detail.layout
        return dashboard_choropleth.layout

    @app.callback(Output("url", "pathname"), Input("metadata-location", "data"))
    def update_url_on_selection(metadata_location):
        if metadata_location:
            return "/region_detail"
        return "/"

    # register callbacks
    dashboard_choropleth.register_callbacks(app)
    dashboard_region_detail.register_callbacks(app)

    return app
