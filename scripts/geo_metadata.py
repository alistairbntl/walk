GEO_METADATA = {
    "state": {
        "left_on": ["STATEFP"],
        "right_on": ["state_id"],
        "groupby": ["state_id"],
        "geojson_cols": ["STATEFP", "name", "geometry"],
        "shape_name": "state_shape",
    },
    "county": {
        "left_on": ["STATEFP", "COUNTYFP"],
        "right_on": ["state_id", "county_id"],
        "groupby": ["state_id", "county_id"],
        "geojson_cols": ["STATEFP", "COUNTYFP", "name", "geometry"],
        "shape_name": "county_shape",
    },
    "census_tract": {
        "left_on": ["STATEFP", "COUNTYFP", "TRACTCE"],
        "right_on": ["state_id", "county_id", "tract_id"],
        "groupby": ["state_id", "county_id", "tract_id"],
        "geojson_cols": ["STATEFP", "COUNTYFP", "TRACTCE", "name", "geometry"],
        "shape_name": "census_tract_shape",
    },
}
