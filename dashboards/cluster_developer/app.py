import dash
import webbrowser
from threading import Timer

from dashboard_tools.dashboard_data_loader import ClusterDashboardDataLoader
from dashboard_layout import build_dashboard


def open_browser():
    webbrowser.open_new("http://127.0.0.1:8051")


def main(port=8051):
    app = dash.Dash(__name__, use_pages=True)

    cluster_data_loader = ClusterDashboardDataLoader()
    data_dict = cluster_data_loader.create_regional_data_dict()

    Timer(1, open_browser).start()

    app = build_dashboard(app, data_dict)

    app.run_server(debug=False, port=port)


if __name__ == "__main__":
    main()
