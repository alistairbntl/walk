drop table census_bureau_demographic_ts;

CREATE TABLE IF NOT EXISTS census_bureau_demographic_ts (
geo_level TEXT,
unique_geo_id TEXT,
delimited_geo_id TEXT,
year INTEGER,
total_population_data FLOAT,
total_population_data_1_period_growth_rate FLOAT,
total_population_data_5_period_growth_rate FLOAT,
median_age_data FLOAT,
median_age_data_5_period_diff FLOAT,
population_density FLOAT
);

drop table census_bureau_workforce_ts;

CREATE TABLE IF NOT EXISTS census_bureau_workforce_ts (
geo_level TEXT,
unique_geo_id TEXT,
delimited_geo_id TEXT,
year INTEGER,
percent_less_hs_data FLOAT,
percent_college_degree_data FLOAT);

drop table census_bureau_housing_market_ts;

CREATE TABLE IF NOT EXISTS census_bureau_housing_market_ts (
geo_level TEXT,
unique_geo_id TEXT,
delimited_geo_id TEXT,
year INTEGER,
owner_occupied_housing_units_data FLOAT,
renter_occupied_housing_units_data FLOAT,
owner_occupied_housing_units_data_percent FLOAT,
renter_occupied_housing_units_data_percent FLOAT
);