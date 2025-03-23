SELECT 
rw.unique_geo_id, 
rw.geo_level,
rw.year,
rw.name,
pd.population_density_data,
rw.median_age_data, 
pd.percent_did_not_move_in_last_year_data,
pd.percent_moved_in_last_year_data,
pd.percent_moved_within_county_in_last_year_data,
pd.percent_moved_from_different_county_same_state_in_last_year_data,
pd.percent_moved_from_different_state_in_last_year_data,
pd.percent_moved_from_abroad_in_last_year_data,
pd.families_per_person_data,
pd.percent_families_married_data,
pd.percent_families_married_with_own_children_data,
wf.percent_less_hs_data,
wf.percent_college_degree_data,
hm.median_home_price_with_nulls_data
FROM raw_data_census_bureau_demographic_ts rw 
    JOIN processed_data_census_bureau_demographic_ts pd
        ON pd.unique_geo_id = rw.unique_geo_id
        AND pd.year = rw.year
    JOIN processed_data_census_bureau_workforce_ts wf
        ON wf.unique_geo_id = rw.unique_geo_id
        AND wf.year = rw.year
    JOIN processed_data_census_bureau_housing_market_ts hm
        ON hm.unique_geo_id = rw.unique_geo_id
        AND hm.year = rw.year
WHERE rw.year = 2023;