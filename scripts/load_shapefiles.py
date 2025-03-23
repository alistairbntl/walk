import geopandas as gpd


def get_shapefiles(config) -> dict:
    """The shapefile data will need to reorganized at some point."""

    # collect and process geographic shape file data

    # states
    states_shape = gpd.read_file(config["shapefiles"]["states"]["path"])
    states_shape["geometry"] = states_shape["geometry"].simplify(
        tolerance=0.01, preserve_topology=True
    )

    # counties
    counties_shape = gpd.read_file(config["shapefiles"]["counties"]["path"])
    counties_shape["geometry"] = counties_shape["geometry"].simplify(
        tolerance=0.01, preserve_topology=True
    )

    # census_tracts
    census_tracts_shape = gpd.read_file(
        config["shapefiles"]["virginia_census_tract"]["path"]
    )
    census_tracts_shape["geometry"] = census_tracts_shape["geometry"].simplify(
        tolerance=0.001, preserve_topology=True
    )

    return {
        "county_shape": counties_shape,
        "census_tract_shape": census_tracts_shape,
        "state_shape": states_shape,
    }
