import dash
import webbrowser
from threading import Timer

import dashboard_data
from dashboard_main import build_dashboard


def open_browser():
    webbrowser.open_new("http://127.0.0.1:8051")


def main(port=8051):
    app = dash.Dash(__name__)

    data_dict = dashboard_data.main(rebuild_data=False)

    Timer(1, open_browser).start()

    app = build_dashboard(app, data_dict)

    app.run_server(debug=False, port=port)


if __name__ == "__main__":
    main()
