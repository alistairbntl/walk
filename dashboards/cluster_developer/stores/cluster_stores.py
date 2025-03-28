from dash import dcc

cluster_stores = [
    dcc.Store(id="cluster-geodata"),
    dcc.Store(id="cluster-plotdata"),
    dcc.Store(id="cluster-metadata-level", data={"geolevel": "county"}),
    dcc.Store(id="cluster-columns", data=[]),
    dcc.Store(id="cluster-results"),
]
