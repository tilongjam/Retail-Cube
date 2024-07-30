import datetime as dt
import json

import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm

from utils.data_handling import read_data_func, write_data_func
from utils.dateConversion import date_convert

#SERVER = r"INMUMPRATHAKKAR\SQLEXPRESS"
#DATABASE = "RetailCube"
#DRIVER = "ODBC Driver 17 for SQL Server"
#USERNAME = "Prati"
#PASSWORD = "Black%402609"
#DB_CONNECT = f"mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}"

SERVER = r"IN-5CG34534K6\SQLEXPRESS"
DATABASE = "RetailCube"
DRIVER = "ODBC Driver 17 for SQL Server"
DB_CONNECT = ('mssql+pyodbc://@' + SERVER + '/' + DATABASE + '?trusted_connection=yes&driver='+ DRIVER)

engine = create_engine(DB_CONNECT)
connection = engine.connect()


class shockContainer:
    def __init__(self, date, lag=1):
        self.date = date_convert(date).convert_date("datetime")
        self.date_string = date_convert(date).convert_date("string")
        self.lag = lag

    def collate_data(self):
        market_data_initial = read_data_func("MarketDataContainer", "*", [])
        market_data_initial = pd.DataFrame.from_records(
            market_data_initial["data"], columns=market_data_initial["columns"]
        )
        market_data_initial["date"] = pd.to_datetime(market_data_initial["date"])
        market_data = pd.DataFrame()
        base_market_data = pd.DataFrame(
            json.loads(
                market_data_initial[market_data_initial["date"] == self.date]
                .reset_index()
                .loc[0, "data"]
            )
        ).reset_index(drop=True)
        # maturity_dates = base_market_data[
        #     ["Market parameter", "Instrument group", "Instrument", "Strike", "Tenor", "Maturity Date"]
        # ]
        mdc_list = []
        for i in tqdm(range(len(market_data_initial))):
            date = market_data_initial.loc[i, "date"]

            if date != self.date:
                mdc_list.extend(
                    json.loads(
                        market_data_initial[market_data_initial["date"] == date].loc[
                            i, "data"
                        ]
                    )
                )

                # filtered = market_data_initial[market_data_initial["date"] == date].loc[i, "data"]
                # filtered = pd.DataFrame(json.loads(filtered)).reset_index(drop=True)
                # market_data = pd.concat(
                #     [
                #         market_data,
                #         pd.DataFrame(
                #             json.loads(market_data_initial[market_data_initial["date"] == date].loc[i, "data"])
                #         ).reset_index(drop=True),
                #     ]
                # )
        market_data = pd.DataFrame.from_records(mdc_list).drop(
            columns=["Maturity Date"]
        )
        # market_data["Maturity Date"] = market_data["Maturity Date"].fillna(base_market_data["Maturity Date"])

        base_market_data = base_market_data.set_index(
            ["Market parameter", "Instrument group", "Instrument", "Strike", "Tenor"]
        )
        return market_data, base_market_data

    def create_shock(self, instrument_group, base_value, shock_value, instrument):
        if instrument_group in ["Equity", "Spot"]:
            return base_value * (1 + shock_value)
        else:
            return base_value + shock_value

    def create_shock_container(self, start_date, end_date):
        try:
            start_date = dt.datetime.strptime(start_date, "%d/%m/%Y")
            end_date = dt.datetime.strptime(end_date, "%d/%m/%Y")
        except:
            start_date = start_date
            end_date = end_date
        market_data, base_market_data = self.collate_data()
        market_data_pivot = pd.pivot_table(
            market_data,
            index=[
                "Market parameter",
                "Instrument group",
                "Instrument",
                "Strike",
                "Tenor",
            ],
            values="Value",
            columns="Date",
        )
        returns = market_data_pivot[
            market_data_pivot.index.isin(["Equity", "Spot"], level=1)
        ]
        absolute = market_data_pivot[
            ~market_data_pivot.index.isin(["Equity", "Spot"], level=1)
        ]

        returns = returns.sort_index(axis="columns").pct_change(axis=1).dropna(axis=1)
        absolute = absolute.sort_index(axis="columns").diff(axis=1).dropna(axis=1)
        shockContainer = pd.concat([returns, absolute])

        self.default_cols = [
            "Date",
            "Market parameter",
            "Instrument group",
            "Instrument",
            "Strike",
            "Tenor",
            "Value",
            "Df",
            "Maturity Date",
        ]
        if start_date == None:
            self.date_cols = list(
                pd.Series(
                    [
                        dt.datetime.strptime(x, "%Y-%m-%d")
                        for x in shockContainer.columns
                        if x not in self.default_cols
                    ]
                )
                .sort_values()
                .tail(253)
            )
        else:
            self.date_cols = list(
                pd.Series(
                    [
                        dt.datetime.strptime(x, "%Y-%m-%d")
                        for x in shockContainer.columns
                        if x not in self.default_cols
                        and start_date
                        <= dt.datetime.strptime(x, "%Y-%m-%d")
                        <= end_date
                    ]
                ).sort_values()
            )

        shockContainer = base_market_data.join(
            shockContainer, how="inner"
        ).reset_index()
        for date in tqdm(self.date_cols):
            date = date.strftime("%Y-%m-%d")
            # try:
            shockContainer[date] = shockContainer.apply(
                lambda x: self.create_shock(
                    x["Instrument group"], x["Value"], x[date], x["Instrument"]
                ),
                axis=1,
            )

            # except Exception as e:
            #     pass
        # shockContainer.columns =
        # print(shockContainer)
        if start_date != None:
            # date_mask = shockContainer.iloc[:, 9:].apply(
            #     lambda row: (pd.to_datetime(row) >= start_date) & (pd.to_datetime(row) <= end_date), axis=1
            # )
            date_columns = [
                col
                for col in shockContainer.columns[9:]
                if start_date <= dt.datetime.strptime(col, "%Y-%m-%d") <= end_date
            ]
            print(date_columns)
            shockContainer = pd.concat(
                [shockContainer.iloc[:, :9], shockContainer[date_columns]], axis=1
            )
            # shockContainer = shockContainer[
            #     shockContainer.apply(
            #         lambda row: (date_convert(row).convert_date("datetime") >= start_date)
            #         & (date_convert(row).convert_date("datetime") <= end_date)
            #     ).any(axis=1)
            # ]
            # shockContainer = shockContainer[(shockContainer.columns >= start_date) & (shockContainer.columns <= end_date)]
        else:
            shockContainer = shockContainer
        print(shockContainer)
        shockContainer_json = json.dumps(
            shockContainer.reset_index(drop=True).to_dict("records")
        )
        # print("JSON Done")
        df = pd.DataFrame.from_dict(
            {"date": [self.date], "data": [shockContainer_json]}
        )
        # print(df)
        query = f"""
        INSERT INTO dbo.shockContainer (date, data) VALUES('{self.date}', '{shockContainer_json}')
        """
        # # # file = open(r"C:\Users\guduremanthi.ext\Documents\DValTest\json.txt", "w")
        # # # a = file.write(query)
        # # # file.close()

        # print("Started")
        write_data_func("shockContainer", df)
        # print("Done")
        return shockContainer
