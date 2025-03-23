from dash import dcc

regression_stores = [
    dcc.Store(id="regression-metadata-level", data={"geolevel": "county"}),
    dcc.Store(id="regression-plotdata"),
    dcc.Store(id="regression-geodata"),
    dcc.Store(id="regression-model"),
]
