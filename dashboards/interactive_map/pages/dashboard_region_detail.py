from dash import html, Input, Output, State

layout = html.Div(
    [
        html.H1("Detailed Regional View"),
        html.Div(id="geo-details"),
        html.A("Back to Map", href="/"),
    ]
)


def register_callbacks(app):
    @app.callback(
        Output("geo-details", "children"),
        Input("url", "search"),
        State("selected-geo", "data"),
    )
    def update_details_page(search, selected_geo):
        if not selected_geo:
            return "No geography selected"

        unique_geo_id = selected_geo.get("unique_geo_id")

        return html.Div([html.H2(f"Unique GEO ID: {unique_geo_id} selected!")])
