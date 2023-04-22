import numpy as np
import pytest
import pandas as pd
from src.features import ProcessDataFrame


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "Duration": {
                0: "8:00",
                1: "5:30",
                2: "9:00",
            },
            "Tags": {0: "Aced it", 1: "Aced it", 2: "Struggled"},
            "Time": {
                0: "25/03/2023 2:25 PM",
                1: "29/03/2023 12:15 PM",
                2: "13/04/2023 8:41 PM",
            },
            "Trainer": {
                0: ["40e597e9-749c-4703-b2ed-466f508c25a8"],
                1: ["5f909007-268c-43df-9a9d-65de1339e2f0"],
                2: [
                    "40e597e9-749c-4703-b2ed-466f508c25a8",
                    "5f909007-268c-43df-9a9d-65de1339e2f0",
                ],
            },
            "Trazadone": {
                0: "No",
                1: "Yes",
                2: "No",
            },
            "Tired?": {0: np.nan, 1: "Yes", 2: "No"},
            "Weather": {
                0: np.nan,
                1: "Sunny",
                2: "Rainy",
            },
            "Recording": {
                0: "Yes",
                1: "Yes",
                2: "Yes",
            },
        }
    )


def test_read_config():
    # Test that config is loaded successfully
    processor = ProcessDataFrame(pd.DataFrame())
    processor._read_config()
    assert isinstance(processor.config, dict)


# def test_get_date(sample_dataframe):
#     # Test that date is correctly extracted from datetime
#     processor = ProcessDataFrame(sample_dataframe)
#     processor._get_date()
#     expected = pd.Series(["2023-03-25", "2023-03-29", "2023-04-13"], name="Date")
#     pd.testing.assert_series_equal(processor.df["Date"], expected)

# def test_get_time(sample_dataframe):
#     # Test that time is correctly extracted from datetime
#     processor = ProcessDataFrame(sample_dataframe)
#     processor._get_time()
#     assert all(processor.df["Time"] == pd.to_datetime(["2022-01-01T10:00:00Z", "2022-01-02T14:30:00Z", "2022-01-03T18:45:00Z"]).tz_convert("Europe/London").time)


def test_get_duration_in_min(sample_dataframe):
    # Test that duration is correctly converted to minutes
    processor = ProcessDataFrame(sample_dataframe)
    processor._get_duration_in_min()
    expected = pd.Series([8, 5.5, 9], name="Duration (min)")
    pd.testing.assert_series_equal(processor.df["Duration (min)"], expected)


# def test_filter_columns(sample_dataframe):
#     # Test that only specified columns are kept in the dataframe
#     processor = ProcessDataFrame(sample_dataframe)
#     processor._filter_columns()
#     assert all(processor.df.columns == ["Duration", "Tags", "Time", "Trainer", ])

# def test_get_trainer_names(sample_dataframe):
#     # Test that trainer names are correctly replaced with values from config file
#     processor = ProcessDataFrame(sample_dataframe)
#     print(processor.df["Trainer"])
#     processor._get_trainer_names()
#     expected = pd.Series(["Seth Olsen", "Kristia K", "Seth Olsen, Kristia K"], name="Trainer")
#     pd.testing.assert_series_equal(processor.df["Trainer"], expected)

# def test_sort_df(sample_dataframe):
#     # Test that dataframe is sorted by datetime in descending order
#     processor = ProcessDataFrame(sample_dataframe)
#     processor._sort_df()
#     assert all(processor.df["Datetime"] == pd.to_datetime(["2022-01-03T18:45:00Z", "2022-01-02T14:30:00Z", "2022-01-01T10:00:00Z"]).tz_convert("Europe/London"))
