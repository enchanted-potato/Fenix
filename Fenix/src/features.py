import ast
import datetime
import numpy as np
import pandas as pd
from src.config import Config


class ProcessDataFrame:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.date = "Datetime"
        self.config = "config.yaml"

    def process_dataframe(self):
        self._read_config()
        self._get_date()
        self._get_time()
        self._get_duration_in_min()
        self._get_trainer_names()
        self._sort_df()
        return self.df

    def _read_config(self):
        config = Config()
        self.config = config.get_final_config()

    def _get_date(self):
        self.df["Date"] = (
            pd.to_datetime(self.df[self.date], utc=True)
            .dt.tz_convert("Europe/London")
            .dt.date
        )
        self.df["Day"] = (
            pd.to_datetime(self.df["Datetime"], utc=True)
            .dt.strftime("%d %b %y")
            .astype(str)
        )
        self.df["Day"] = ["-".join(d[:2]) for d in self.df["Day"].str.split(" ")]

    def _get_time(self):
        self.df["Time"] = (
            pd.to_datetime(self.df[self.date], utc=True)
            .dt.tz_convert("Europe/London")
            .dt.time
        )

    def _get_duration_in_min(self):
        self.df["Duration (min)"] = self.df["Duration"].apply(lambda x: x.split(":"))
        self.df["Duration (min)"] = [
            int(time[0]) + int(time[1]) / 60 for time in self.df["Duration (min)"]
        ]
        self.df["Duration (min)"] = self.df["Duration (min)"].round(2)

    def _convert_date(self):
        # self.df[self.date] = pd.to_datetime(self.df[self.date], format="%d-%m-%Y %H:%M:%S")
        self.df = self.df.set_index(self.date)

    def _get_trainer_names(self):
        if isinstance(self.df["Trainer"].iloc[0], str):
            self.df.loc[:, "Trainer"] = self.df["Trainer"].apply(
                lambda x: ast.literal_eval(x)
            )
        self.df["Trainer"] = self.df["Trainer"].map(
            lambda lst: [self.config["trainers"].get(item, item) for item in lst]
        )
        self.df["Trainer"] = self.df["Trainer"].astype(str)
        self.df["Trainer"] = self.df["Trainer"].apply(self._split_list)

    def _sort_df(self):
        self.df.sort_values(["Datetime"], ascending=False, inplace=True)

    def filter_columns(self, display_columns):
        self.df.drop(
            columns=[col for col in self.df.columns if col not in display_columns],
            inplace=True,
        )

    def sort_columns(self, display_columns):
        self.df = self.df[display_columns]

    @staticmethod
    def _split_list(list_str):
        if pd.isnull(list_str):
            return np.nan
        else:
            list_str = list_str.replace("['", "")
            list_str = list_str.replace("']", "")
            list_str = list_str.replace("'", "")
            return list_str
