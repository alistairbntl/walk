from data_loaders.data_loader import (
    DemographicDataLoader,
    WorkForceDataLoader,
    HousingMarketDataLoader,
)


def main():
    demo_data_loader = DemographicDataLoader()
    data_dict = demo_data_loader.load_data()
    demo_data_loader.upload_df(data_dict)

    demo_data_loader = WorkForceDataLoader()
    data_dict = demo_data_loader.load_data()
    demo_data_loader.upload_df(data_dict)

    demo_data_loader = HousingMarketDataLoader()
    data_dict = demo_data_loader.load_data()
    demo_data_loader.upload_df(data_dict)


if __name__ == "__main__":
    main()
