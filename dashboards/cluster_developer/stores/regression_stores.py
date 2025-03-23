from dash import dcc

regression_stores = [
    dcc.Store(id="metadata-level-regression", data={"geolevel": "county"}),
    dcc.Store(id="geodata_cluster", data=geo_dict),
]
