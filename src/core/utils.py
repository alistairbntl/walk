from pathlib import Path
import yaml

from av_core.db_tools.sqlite_manager import SQLiteManager


def load_config(config_file="config.yaml"):
    base_dir = Path(__file__).resolve().parent.parent.parent
    config_path = base_dir / config_file

    with config_path.open("r") as file:
        return yaml.safe_load(file)


def get_db_manager():
    config = load_config()
    db_manager = SQLiteManager(config["database"]["path"])
    return db_manager
