def create_lead_lag_columns(group_df, columns, periods_back):
    """
    Creates lead / lag columns
    """
    shifted_df = group_df.copy()
    shifted_df[[f"{col}_shift_{periods_back}" for col in columns]] = shifted_df[
        columns
    ].shift(periods_back)
    return shifted_df


def create_percent_change_columns(group_df, columns, periods_back):
    group_df[[f"{col}_{periods_back}_period_growth_rate" for col in columns]] = (
        group_df[columns] - group_df[columns].shift(periods_back)
    ) / group_df[columns].shift(periods_back)
    return group_df


def create_diff_change_columns(group_df, columns, periods_back):
    group_df[[f"{col}_{periods_back}_period_diff" for col in columns]] = group_df[
        columns
    ] - group_df[columns].shift(periods_back)
    return group_df


def normalize_column(column):
    return (column - column.min()) / (column.max() - column.min()) * 100


def percentile_rank(column, ascending=True):
    return column.rank(ascending=ascending, pct=True) * 100


def absolute_value_scaling(series):
    max_abs_value = series.abs().max()
    return (series / max_abs_value) * 50 + 50
