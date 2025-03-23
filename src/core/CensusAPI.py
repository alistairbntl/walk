import logging
from dataclasses import dataclass

from av_core.api_tools.API_requests import make_api_call

from urllib.parse import urlencode

CENSUS_DATA_API_BASE = "https://api.census.gov/data/"
API_KEY = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_census_api_call(api_dict):
    cac = CensusAPIConfig(**api_dict)
    headers = {"Content-Type": "application/json"}
    return make_api_call(cac.build_data_query_url(), headers)


@dataclass
class CensusAPIConfig:
    """
    data class built to run Census Bureau API calls of the form
    https://api.census.gov/data/yyyy/acs/acsx?get=NAME,B01001_001E&for=tract:*&in=state:06&in=county:*&key=API_KEY
    """

    year: int
    type_: str
    variables: list
    state: list
    dataset: str = "acs"
    tract: list = None
    county: list = None

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


if __name__ == "__main__":
    pass
