CREATE TABLE census_bureau_variables_display (
    variable_id text,
    display_name text,
    dtype text,
    default_ts_transformation text
);

insert into census_bureau_variables_display
select
    'B19013_001E'
    , 'median_household_income'
    , 'int'
    , 'pct_chg';

insert into census_bureau_variables_display
select
    'B01001_001E'
    , 'total_population'
    , 'int'
    , 'pct_chg';

insert into census_bureau_variables_display
select
    'B01002_001E'
    , 'median_age'
    , 'float'
    , 'diff';

