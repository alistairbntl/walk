from dataclasses import dataclass

# from config import get_db_connection
from urllib.parse import urlencode

CENSUS_DATA_API_BASE = "https://api.census.gov/data/"
API_KEY = "6c1399af793891246545517f96f88674a0282315"


@dataclass
class CensusAPIConfig:
    """
    data class built to run Census Bureau API calls of the form
    https://api.census.gov/data/yyyy/acs/acsx?get=NAME,B01001_001E&for=tract:*&in=state:06&in=county:*&key=API_KEY
    """

    year: int
    dataset: str
    type_: str
    variables: list
    tract: list
    state: list
    county: list

    def __post_init__(self):
        self.base_url = self.build_base_url()

    def build_base_url(self) -> str:
        return CENSUS_DATA_API_BASE + f"{self.year}/{self.dataset}"

    def build_data_query_url(self) -> str:
        url = f"{self.base_url}/{self.type_}?get="

        url += ",".join(self.variables)

        filters = {}
        if self.tract:
            filters["for"] = f"tract:{','.join(self.tract)}"
        elif self.county:
            filters["for"] = f"county:{','.join(self.county)}"
        elif self.state:
            filters["for"] = f"state:{','.join(self.state)}"
        else:
            filters["for"] = "us:*"

        if self.state and (self.county or self.tract):
            filters["in"] = f"state:{','.join(self.state)}"

        filters["key"] = API_KEY

        query_string = urlencode(filters, safe=":,*")

        return f"{url}&{query_string}"


def main():
    acs_2023 = CensusAPIConfig(
        year=2023,
        dataset="acs",
        type_="acs1",
        variables=["NAME", "B01001_001E", "B01002_001E"],
        tract=None,
        state=["51"],
        county=["*"],
    )


if __name__ == "__main__":
    main()
