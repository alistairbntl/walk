import pytest
from core.CensusAPI import CensusAPIConfig

shared_test_data = [
    {
        "year": 2022,
        "dataset": "acs",
        "type_": "acs5",
        "variables": ["NAME", "B01001_001E"],
        "tract": None,
        "state": ["51"],
        "county": ["*"],
        "expected_url": "https://api.census.gov/data/2022/acs/acs5?get=NAME,B01001_001E&for=county:*&in=state:51&key=6c1399af793891246545517f96f88674a0282315",
    },
    {
        "year": 2022,
        "dataset": "acs",
        "type_": "acs5",
        "variables": ["NAME", "B01001_001E"],
        "tract": None,
        "state": ["51"],
        "county": None,
        "expected_url": "https://api.census.gov/data/2022/acs/acs5?get=NAME,B01001_001E&for=state:51&key=6c1399af793891246545517f96f88674a0282315",
    },
]


def get_test_data(fields):
    return [tuple(item[field] for field in fields) for item in shared_test_data]


class TestCensusAPIConfig:
    """
    Tests for the CensusAPIConfig class.
    """

    @pytest.mark.parametrize(
        "year, dataset, type_, variables, tract, state, county",
        get_test_data(
            ["year", "dataset", "type_", "variables", "tract", "state", "county"]
        ),
    )
    def test_construct_CensusAPIConfig(
        self, year, dataset, type_, variables, tract, state, county
    ):
        query = CensusAPIConfig(
            year=year,
            dataset=dataset,
            type_=type_,
            variables=variables,
            tract=tract,
            state=state,
            county=county,
        )
        assert query.year == year
        assert query.dataset == dataset
        assert query.type_ == type_
        assert query.variables == variables
        assert query.tract == tract
        assert query.state == state
        assert query.county == county

    @pytest.mark.parametrize(
        "year, dataset, type_, variables, tract, state, county, expected_url",
        get_test_data(
            [
                "year",
                "dataset",
                "type_",
                "variables",
                "tract",
                "state",
                "county",
                "expected_url",
            ]
        ),
    )
    def test_build_data_query_url(
        self, year, dataset, type_, variables, tract, state, county, expected_url
    ):
        query = CensusAPIConfig(
            year=year,
            dataset=dataset,
            type_=type_,
            variables=variables,
            tract=tract,
            state=state,
            county=county,
        )
        assert query.build_data_query_url() == expected_url
