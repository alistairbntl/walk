from data_loaders.data_loader import DataLoader
from data_loaders.data_processors import (
    DemographicDataProcessor,
    WorkForceDataProcessor,
    HousingMarketDataProcessor,
)


def main():
    # demo_data_loader = DataLoader("demographics")
    # demo_data_loader.run_pipeline()

    # demo_data_loader = DataLoader("workforce")
    # demo_data_loader.run_pipeline()

    #    demo_data_loader = DataLoader("housing_market")
    #    demo_data_loader.run_pipeline()

    #    demo_data_processor = DemographicDataProcessor()
    #    demo_data_processor.run_pipeline()

    # workforce_data_processor = WorkForceDataProcessor()
    # workforce_data_processor.run_pipeline()

    housing_market_data_processor = HousingMarketDataProcessor()
    housing_market_data_processor.run_pipeline()


if __name__ == "__main__":
    main()
