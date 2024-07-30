import datetime as dt
import decimal
import json
import os
import time

import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pandas as pd
import QuantLib as ql
from django.shortcuts import HttpResponse, render


from utils import dateConversion
from utils.table_to_html import table_to_html


def parse_float(value):
    if isinstance(value, decimal.Decimal):
        return np.float64(str(value))
    return value


# Create your views here.
def index(request):
    context = {}
    # sc = shockContainer(pd.to_datetime("30-06-2022", dayfirst=True), 1).create_shock_container()
    # print(sc)
    return render(request, "Valuations/index.html", context)


def Comparison(request):
    context = {}
    # sc = shockContainer(pd.to_datetime("30-06-2022", dayfirst=True), 1).create_shock_container()
    # print(sc)
    return render(request, "Valuations/Comparison.html", context)


def forex(request):
    context = {}
    # print(portfolio_valuation)
    forex = portfolio_valuation[portfolio_valuation["asset_class"] == "Forex"]
    # print(forex)
    return render(request, "Valuations/forex.html", context)


def equity(request):
    context = {}
    return render(request, "Valuations/equity.html", context)


def interest_rate(request):
    context = {}
    return render(request, "Valuations/interest_rate.html", context)


def fixed_income(request):
    context = {}
    return render(request, "Valuations/fixed_income.html", context)


def valuations_funcs(request):
    if request.method == "POST":
        request_data = request.POST
        data = json.loads(request_data["data"])
        context = {
            "func": request_data["func"],
        }
        func = request_data["func"]
        # print(request_data)
        date = data["date"]
        date_datetime = dt.datetime.strptime(date, "%d/%m/%Y")
        date_string = date_datetime.strftime("%Y/%m/%d")
        if func == "populate_portfolio_select":
            table = read_data_func(
                "portfolio_details",
                "*",
                [f"date='{date_string}'"],
            )
            table = pd.DataFrame.from_records(
                table["data"], columns=table["columns"]
            ).reset_index(drop=True)
            # table = pd.DataFrame.from_records(json.loads(table.loc[0, "data"], parse_float=parse_float))
            # print(table)
            unique_portfolios = table["portfolio"].unique()
            string = ""
            for curve in unique_portfolios:
                string += f"<option value='{curve}'>{curve}</option>"
            context["options"] = string
        elif func == "value_portfolio":
            portfolio = data["portfolio"]
            date = data["date"]
            date_datetime = dt.datetime.strptime(date, "%d/%m/%Y")
            date_30 = date_datetime - dt.timedelta(days=30)

            date_1 = date_datetime - dt.timedelta(
                days=1
            )  # Chnges remaing on only taking the business day and like if it is a holiday take the previous date
            result = read_data_func(
                "portfolio_valuations_test",
                conditions=[f"date='{date_datetime.strftime('%Y/%m/%d')}'"],
            )
            result_30 = read_data_func(
                "portfolio_valuations_test",
                conditions=[f"date='{date_30.strftime('%Y/%m/%d')}'"],
            )
            result_1 = read_data_func(
                "portfolio_valuations_test",
                conditions=[f"date='{date_1.strftime('%Y/%m/%d')}'"],
            )

            existing_val = pd.DataFrame.from_records(
                result["data"], columns=result["columns"]
            )
            existing_val_30 = pd.DataFrame.from_records(
                result_30["data"], columns=result["columns"]
            )
            existing_val_1 = pd.DataFrame.from_records(
                result_1["data"], columns=result["columns"]
            )

            existing_val = existing_val.loc[
                existing_val["portfolio"] == data["portfolio"]
            ]
            existing_val_30 = existing_val_30.loc[
                existing_val_30["portfolio"] == data["portfolio"]
            ]
            existing_val_1 = existing_val_1.loc[
                existing_val_1["portfolio"] == data["portfolio"]
            ]

            global portfolio_valuation
            print("Started")
            s = time.time()
            if len(existing_val) and len(existing_val_30) and len(existing_val_1) > 0:
                existing_val = existing_val[
                    existing_val["last_modified"] == max(existing_val["last_modified"])
                ].reset_index(drop=True)
                portfolio_valuation = pd.DataFrame.from_records(
                    json.loads(existing_val.loc[0, "portfolio_valuation"])
                )
                portfolio_valuation_30 = pd.DataFrame.from_records(
                    json.loads(existing_val_30.loc[0, "portfolio_valuation"])
                )
                portfolio_valuation_1 = pd.DataFrame.from_records(
                    json.loads(existing_val_1.loc[0, "portfolio_valuation"])
                )

                # portfolio_valuation["Day change - absolute"] = np.array(portfolio_valuation_1["valuation"]) - np.array(
                #     portfolio_valuation["valuation"]
                # )

                portfolio_valuation["Day change"] = (
                    (
                        np.array(portfolio_valuation_1["valuation"])
                        - np.array(portfolio_valuation["valuation"])
                    )
                    / np.array(portfolio_valuation["valuation"])
                ) * 100

                # portfolio_valuation["Monthly change - absolute"] = np.array(
                #     portfolio_valuation_30["valuation"]
                # ) - np.array(portfolio_valuation["valuation"])

                portfolio_valuation["Monthly change"] = (
                    (
                        np.array(portfolio_valuation_30["valuation"])
                        - np.array(portfolio_valuation["valuation"])
                    )
                    / np.array(portfolio_valuation["valuation"])
                ) * 100
                print(portfolio_valuation)

            else:
                # portfolio_valuation = pf.value_portfolio(read_from_db=True, write_to_db=False)
                date_ql = ql.DateParser.parseFormatted(date, "%d/%m/%Y")
                date_datetime = dateConversion.date_convert(date_ql).convert_date(
                    "datetime"
                )
                date_datetime_30 = date_datetime - dt.timedelta(days=30)
                date_ql_30 = dateConversion.date_convert(date_datetime_30).convert_date(
                    "ql"
                )
                date_datetime_1 = date_datetime - dt.timedelta(days=1)
                date_ql_1 = dateConversion.date_convert(date_datetime_1).convert_date(
                    "ql"
                )

                pf = Portfolio(date_ql, portfolio)
                portfolio_valuation = pf.value_portfolio(read_from_db=False)
                pf_30 = Portfolio(date_ql_30, portfolio)
                portfolio_valuation_30 = pf_30.value_portfolio(read_from_db=False)
                pf_1 = Portfolio(date_ql_1, portfolio)
                portfolio_valuation_1 = pf_1.value_portfolio(read_from_db=False)

                # portfolio_valuation["Day change - absolute"] = np.array(portfolio_valuation_1["valuation"]) - np.array(
                #     portfolio_valuation["valuation"]
                # )
                portfolio_valuation["Day change"] = (
                    (
                        np.array(portfolio_valuation_1["valuation"])
                        - np.array(portfolio_valuation["valuation"])
                    )
                    / np.array(portfolio_valuation["valuation"])
                ) * 100

                # portfolio_valuation["Monthly change - absolute"] = np.array(
                #     portfolio_valuation_30["valuation"]
                # ) - np.array(portfolio_valuation["valuation"])

                portfolio_valuation["Monthly change"] = (
                    (
                        np.array(portfolio_valuation_30["valuation"])
                        - np.array(portfolio_valuation["valuation"])
                    )
                    / np.array(portfolio_valuation["valuation"])
                ) * 100
            e = time.time()

            break_down_level = float(request_data["breakdown_level"])
            # print("Ended")
            print(f"Time elapsed: {(e-s)}")
            # pf.compute_portfolio_sensitvities()
            print(portfolio_valuation)
            forex = portfolio_valuation.loc[
                portfolio_valuation["asset_class"] == "Forex"
            ].reset_index(drop=True)

            interest_rate = portfolio_valuation.loc[
                portfolio_valuation["asset_class"] == "Interest Rate"
            ].reset_index(drop=True)
            fixed_income = portfolio_valuation.loc[
                portfolio_valuation["asset_class"] == "Fixed Income"
            ].reset_index(drop=True)
            data_dict = {}

            for data in ["forex", "interest_rate", "fixed_income"]:
                data_dict[data] = eval(data)

            # by_instrument = portfolio_valuation.groupby("instrument").sum().reset_index()[["instrument", "valuation"]]

            # try:
            #     by_instrument = by_instrument.drop(columns="id")
            # except Exception as e:
            #     print(e)

            # by_instrument.columns = ["Instrument", "Value"]

            return_dict = {"table": {}, "plots": {}}
            if break_down_level == 0:
                for key in data_dict.keys():
                    by_instrument = (
                        data_dict[key]
                        .groupby("instrument")
                        .sum()
                        .reset_index()[
                            [
                                "instrument",
                                "valuation",
                                "Day change",
                                "Monthly change",
                            ]
                        ]
                    )
                    by_instrument.columns = [
                        "Instrument",
                        "Value",
                        "Day change",
                        "Monthly change",
                    ]
                    by_product = (
                        data_dict[key]
                        .groupby("product_type")[
                            "valuation",
                            "Day change",
                            "Monthly change",
                        ]
                        .apply(lambda c: c.abs().sum())
                        .reset_index()[
                            [
                                "product_type",
                                "valuation",
                                "Day change",
                                "Monthly change",
                            ]
                        ]
                    ).reset_index(drop=True)
                    by_product.columns = [
                        "Product Type",
                        "Value",
                        "Day change",
                        "Monthly change",
                    ]

                    return_dict["table"][key] = table_to_html(
                        by_instrument,
                        [
                            "Instrument",
                            "Value",
                            "Day change",
                            "Monthly change",
                        ],
                    )

                    return_dict["plots"][key] = {
                        "x": list(by_product["Product Type"].values),
                        "y": list(by_product["Value"].values),
                    }
            # table = table_to_html(by_instrument, ["Instrument", "Value"])
            # date = ql.Date(30, 6, 2022)
            # by_product = portfolio_valuation.groupby("product_type").sum().reset_index()[["product_type", "valuation"]]

            # try:
            #     by_product = by_product.drop(columns="id")
            # except Exception as e:
            #     print(e)

            # by_product.columns = ["Product Type", "Value"]

            # x = list(by_product["Product Type"].values)
            # y = list(by_product["Value"].values)
            # plot = vsf.vol_surface_as_on_date()

            context["func"] = request_data["func"]
            context["content"] = return_dict
            return HttpResponse(json.dumps(context))

        elif func == "impact_assessment_fi":

            def provisioning_func(row):
                # Computing New Market Value
                print(row)
                if row["New ASF"] in ["HTM", "JVS"]:
                    new_market_value = row["Book Value"]
                else:
                    if row["Product Type"] == "VCF":
                        new_market_value = (
                            row["Book Value"] * row["Market Price"]
                        ) / 100
                    else:
                        new_market_value = row["Market Price"] * row["Face Value"] / 100

                new_mtm = new_market_value - row["Book Value"]

                # Provisioning
                if row["NPIREST"] == "NN":
                    if row["Product Type"] in ["RCIL", "A'&'S"]:
                        provision = row["Book Value"]
                    else:
                        provision = new_mtm

                else:
                    provision = row["Provision Net of LICRA"]

                return abs(provision), abs(new_market_value), abs(new_mtm)

            data = pd.read_excel(
                r"C:\Users\prathakkar.ext\Desktop\Dval\impactAssessment.xlsx"
            )
            for i in range(len(data)):
                provision, new_mv, new_mtm = provisioning_func(data.loc[i, :])
                data.loc[i, "Provision"] = provision
                data.loc[i, "New Market Value"] = new_mv
                data.loc[i, "New MTM"] = new_mtm
            required_data = data.groupby("Product").agg(
                {"Provision": "sum", "New MTM": "sum", "New Market Value": "sum"}
            )
            content = table_to_html(required_data)
            context = {"content": content}
            return HttpResponse(json.dumps(context))

        elif func == "value_portfolio_comp":
            portfolio = data["portfolio"]
            date = data["date"]
            comp_date = data["date_comp"]
            date_datetime = dt.datetime.strptime(date, "%d/%m/%Y")
            date_datetime_comp = dt.datetime.strptime(comp_date, "%d/%m/%Y")

            result = read_data_func(
                "portfolio_valuations_test",
                conditions=[f"date='{date_datetime.strftime('%Y/%m/%d')}'"],
            )

            result_comp = read_data_func(
                "portfolio_valuations_test",
                conditions=[f"date='{date_datetime_comp.strftime('%Y/%m/%d')}'"],
            )

            existing_val = pd.DataFrame.from_records(
                result["data"], columns=result["columns"]
            )
            existing_val_comp = pd.DataFrame.from_records(
                result_comp["data"], columns=result["columns"]
            )

            existing_val = existing_val.loc[
                existing_val["portfolio"] == data["portfolio"]
            ]
            existing_val_comp = existing_val_comp.loc[
                existing_val_comp["portfolio"] == data["portfolio"]
            ]

            print("Started")
            s = time.time()
            if len(existing_val) and len(existing_val_comp) > 0:
                existing_val = existing_val[
                    existing_val["last_modified"] == max(existing_val["last_modified"])
                ].reset_index(drop=True)
                portfolio_valuation = pd.DataFrame.from_records(
                    json.loads(existing_val.loc[0, "portfolio_valuation"])
                )
                portfolio_valuation_comp = pd.DataFrame.from_records(
                    json.loads(existing_val_comp.loc[0, "portfolio_valuation"])
                )

                # portfolio_valuation["Day change - absolute"] = np.array(portfolio_valuation_1["valuation"]) - np.array(
                #     portfolio_valuation["valuation"]
                # )

                portfolio_valuation["Comparision Date"] = portfolio_valuation_comp[
                    "valuation"
                ]
                portfolio_valuation["Change"] = (
                    (
                        np.array(portfolio_valuation_comp["valuation"])
                        - np.array(portfolio_valuation["valuation"])
                    )
                    / np.array(portfolio_valuation["valuation"])
                ) * 100
                # portfolio_valuation.columns = [
                #     "As on the Valuation Date",
                #     "As on the Comparision Date",
                #     "Relative Change",
                # ]
                print(portfolio_valuation)

            else:
                # portfolio_valuation = pf.value_portfolio(read_from_db=True, write_to_db=False)
                date_ql = ql.DateParser.parseFormatted(date, "%d/%m/%Y")
                date_datetime = dateConversion.date_convert(date_ql).convert_date(
                    "datetime"
                )
                date_ql_comp = dateConversion.date_convert(
                    date_datetime_comp
                ).convert_date("ql")

                pf = Portfolio(date_ql, portfolio)
                portfolio_valuation = pf.value_portfolio(read_from_db=False)
                pf_comp = Portfolio(date_ql_comp, portfolio)
                portfolio_valuation_comp = pf_comp.value_portfolio(read_from_db=False)

                # portfolio_valuation["Day change - absolute"] = np.array(portfolio_valuation_1["valuation"]) - np.array(
                #     portfolio_valuation["valuation"]
                # )
                portfolio_valuation["Comparision Date"] = portfolio_valuation_comp[
                    "valuation"
                ]
                portfolio_valuation["Change"] = (
                    (
                        np.array(portfolio_valuation_comp["valuation"])
                        - np.array(portfolio_valuation["valuation"])
                    )
                    / np.array(portfolio_valuation["valuation"])
                ) * 100
                # portfolio_valuation.columns = [
                #     "As on the Valuation Date",
                #     "As on the Comparision Date",
                #     "Relative Change",
                # ]
                print("MY PORTFOLIO", portfolio_valuation)
            e = time.time()

            break_down_level = float(request_data["breakdown_level"])
            print("Ended")
            print(f"Time elapsed: {(e-s)}")
            # pf.compute_portfolio_sensitvities()
            print(portfolio_valuation)
            forex = portfolio_valuation.loc[
                portfolio_valuation["asset_class"] == "Forex"
            ].reset_index(drop=True)

            interest_rate = portfolio_valuation.loc[
                portfolio_valuation["asset_class"] == "Interest Rate"
            ].reset_index(drop=True)
            fixed_income = portfolio_valuation.loc[
                portfolio_valuation["asset_class"] == "Fixed Income"
            ].reset_index(drop=True)
            data_dict = {}

            for data in ["forex", "interest_rate", "fixed_income"]:
                data_dict[data] = eval(data)

            # by_instrument = portfolio_valuation.groupby("instrument").sum().reset_index()[["instrument", "valuation"]]

            # try:
            #     by_instrument = by_instrument.drop(columns="id")
            # except Exception as e:
            #     print(e)

            # by_instrument.columns = ["Instrument", "Value"]

            return_dict = {"table": {}, "plots": {}}
            if break_down_level == 0:
                for key in data_dict.keys():
                    by_instrument = (
                        data_dict[key]
                        .groupby("instrument")
                        .sum()
                        .reset_index()[
                            ["instrument", "valuation", "Comparision Date", "Change"]
                        ]
                    )
                    by_instrument.columns = [
                        "Instrument",
                        "Value as on Valuation Date",
                        "Value as on Comparision Date",
                        "Relative Change",
                    ]
                    by_product = (
                        data_dict[key]
                        .groupby("product_type")[
                            "valuation",
                            "Comparision Date" "Change",
                        ]
                        .apply(lambda c: c.abs().sum())
                        .reset_index()[
                            ["product_type", "valuation", "Comparision Date", "Change"]
                        ]
                    ).reset_index(drop=True)
                    by_product.columns = [
                        "Product Type",
                        "Value as on Valuation Date",
                        "Value as on Comparision Date",
                        "Relative Change",
                    ]

                    return_dict["table"][key] = table_to_html(
                        by_instrument,
                        [
                            "Instrument",
                            "Value as on Valuation Date",
                            "Value as on Comparision Date",
                            "Relative Change",
                        ],
                    )

                    return_dict["plots"][key] = {
                        "x": list(by_product["Product Type"].values),
                        "y": list(by_product["Relative Change"].values),
                    }
            # table = table_to_html(by_instrument, ["Instrument", "Value"])
            # date = ql.Date(30, 6, 2022)
            # by_product = portfolio_valuation.groupby("product_type").sum().reset_index()[["product_type", "valuation"]]

            # try:
            #     by_product = by_product.drop(columns="id")
            # except Exception as e:
            #     print(e)

            # by_product.columns = ["Product Type", "Value"]

            # x = list(by_product["Product Type"].values)
            # y = list(by_product["Value"].values)
            # plot = vsf.vol_surface_as_on_date()

            context["func"] = request_data["func"]
            context["content"] = return_dict
            return HttpResponse(json.dumps(context))

        elif func == "valuations_breakdown":
            asset_class = data["asset_class"]
            break_down_level = data["breakdown_level"]
            print(portfolio_valuation)
            if "portfolio_valuation" not in globals():
                portfolio_valuation = pf.value_portfolio(read_from_db=False)
            if asset_class == "Forex":
                forex = portfolio_valuation.loc[
                    portfolio_valuation["asset_class"] == "Forex"
                ].reset_index(drop=True)
                if break_down_level == "Instrument":
                    by_instrument = (
                        forex.groupby("instrument")
                        .sum()
                        .reset_index()[
                            [
                                "instrument",
                                "valuation",
                                "Day change",
                                "Monthly change",
                            ]
                        ]
                    )
                    by_instrument.columns = [
                        "Instrument",
                        "Value",
                        "Day change",
                        "Monthly change",
                    ]
                    table = table_to_html(by_instrument, list(by_instrument.columns))
                elif break_down_level == "Trade":
                    trade = forex[
                        [
                            "contract_number",
                            "trade_number",
                            "asset_class",
                            "instrument",
                            "product_type",
                            "valuation",
                            "Day change",
                            "Monthly change",
                        ]
                    ].copy()
                    trade.columns = [
                        "Contract Number",
                        "Trade Number",
                        "Asset Class",
                        "Instrument",
                        "Product Type",
                        "Value",
                        "Day change",
                        "Monthly change",
                    ]
                    table = table_to_html(trade, trade.columns)
                context["content"] = table

            if asset_class == "Interest Rate":
                interest_rate = portfolio_valuation.loc[
                    portfolio_valuation["asset_class"] == "Interest Rate"
                ].reset_index(drop=True)
                if break_down_level == "Instrument":
                    by_instrument = (
                        interest_rate.groupby("instrument")
                        .sum()
                        .reset_index()[
                            [
                                "instrument",
                                "valuation",
                                "Day change",
                                "Monthly change",
                            ]
                        ]
                    )
                    by_instrument.columns = [
                        "Instrument",
                        "Value",
                        "Day change",
                        "Monthly change",
                    ]
                    table = table_to_html(by_instrument, list(by_instrument.columns))
                elif break_down_level == "Trade":
                    trade = interest_rate[
                        [
                            "contract_number",
                            "trade_number",
                            "asset_class",
                            "instrument",
                            "product_type",
                            "valuation",
                            "Day change",
                            "Monthly change",
                        ]
                    ].copy()
                    trade.columns = [
                        "Contract Number",
                        "Trade Number",
                        "Asset Class",
                        "Instrument",
                        "Product Type",
                        "Value",
                        "Day change",
                        "Monthly change",
                    ]
                    table = table_to_html(trade, trade.columns)
                context["content"] = table

            if asset_class == "Fixed Income":
                fixed_income = portfolio_valuation.loc[
                    portfolio_valuation["asset_class"] == "Fixed Income"
                ].reset_index(drop=True)
                if break_down_level == "Instrument":
                    by_instrument = (
                        fixed_income.groupby("instrument")
                        .sum()
                        .reset_index()[
                            [
                                "instrument",
                                "valuation",
                                "Day change",
                                "Monthly change",
                            ]
                        ]
                    )
                    by_instrument.columns = [
                        "Instrument",
                        "Value",
                        "Day change",
                        "Monthly change",
                    ]
                    table = table_to_html(by_instrument, list(by_instrument.columns))
                elif break_down_level == "Trade":
                    trade = fixed_income[
                        [
                            "contract_number",
                            "trade_number",
                            "asset_class",
                            "instrument",
                            "product_type",
                            "valuation",
                            "Day change",
                            "Monthly change",
                        ]
                    ].copy()
                    trade.columns = [
                        "Contract Number",
                        "Trade Number",
                        "Asset Class",
                        "Instrument",
                        "Product Type",
                        "Value",
                        "Day change",
                        "Monthly change",
                    ]
                    table = table_to_html(trade, trade.columns)
                context["content"] = table
        elif func == "valuations_top5":
            asset_class = data["asset_class"]
            if "portfolio_valuation" not in globals():
                portfolio_valuation = pf.value_portfolio(read_from_db=False)
            # if "portfolio_valuation" not in globals():
            #     portfolio_valuation = pf.value_portfolio(read_from_db=False)
            if asset_class == "Forex":
                forex = portfolio_valuation.loc[
                    portfolio_valuation["asset_class"] == "Forex"
                ].reset_index(drop=True)
                forex_sorted = forex.sort_values(
                    by="valuation", ascending=True
                ).reset_index()
                forex_sorted = forex_sorted.head(5)
                forex_sorted = forex_sorted.loc[
                    :,
                    [
                        "contract_number",
                        "trade_number",
                        "asset_class",
                        "instrument",
                        "product_type",
                        "valuation",
                        "Day change",
                        "Monthly change",
                    ],
                ]
                forex_sorted1 = forex_sorted[
                    [
                        "contract_number",
                        "trade_number",
                        "asset_class",
                        "instrument",
                        "product_type",
                        "valuation",
                        "Day change",
                        "Monthly change",
                    ]
                ].copy()
                forex_sorted1.columns = [
                    "Contract Number",
                    "Trade Number",
                    "Asset Class",
                    "Instrument",
                    "Product Type",
                    "Value",
                    "Day change - absolute",
                    "Day change - relative",
                    "Monthly change - absolute",
                    "Monthly change - relative",
                ]
                table = table_to_html(forex_sorted1, forex_sorted1.columns)
                context["content"] = table

            elif asset_class == "Interest Rate":
                interest_rate = portfolio_valuation.loc[
                    portfolio_valuation["asset_class"] == "Interest Rate"
                ].reset_index(drop=True)
                interest_rate_sorted = interest_rate.sort_values(
                    by="valuation", ascending=True
                ).reset_index()
                interest_rate_sorted = interest_rate_sorted.head(5)
                interest_rate_sorted = interest_rate_sorted.loc[
                    :,
                    [
                        "contract_number",
                        "trade_number",
                        "asset_class",
                        "instrument",
                        "product_type",
                        "valuation",
                        "Day change",
                        "Monthly change",
                    ],
                ]
                interest_rate_sorted1 = interest_rate_sorted[
                    [
                        "contract_number",
                        "trade_number",
                        "asset_class",
                        "instrument",
                        "product_type",
                        "valuation",
                        "Day change",
                        "Monthly change",
                    ]
                ].copy()
                interest_rate_sorted1.columns = [
                    "Contract Number",
                    "Trade Number",
                    "Asset Class",
                    "Instrument",
                    "Product Type",
                    "Value",
                    "Day change - absolute",
                    "Day change - relative",
                    "Monthly change - absolute",
                    "Monthly change - relative",
                ]
                table = table_to_html(
                    interest_rate_sorted1, interest_rate_sorted1.columns
                )
                context["content"] = table
            elif asset_class == "Fixed Income":
                fixed_income = portfolio_valuation.loc[
                    portfolio_valuation["asset_class"] == "Fixed Income"
                ].reset_index(drop=True)
                fixed_income_sorted = fixed_income.sort_values(
                    by="valuation", ascending=True
                ).reset_index()
                fixed_income_sorted = fixed_income_sorted.head(5)
                fixed_income_sorted = fixed_income_sorted.loc[
                    :,
                    [
                        "contract_number",
                        "trade_number",
                        "asset_class",
                        "instrument",
                        "product_type",
                        "valuation",
                        "Day change",
                        "Monthly change",
                    ],
                ]
                fixed_income_sorted1 = fixed_income_sorted[
                    [
                        "contract_number",
                        "trade_number",
                        "asset_class",
                        "instrument",
                        "product_type",
                        "valuation",
                        "Day change",
                        "Monthly change",
                    ]
                ].copy()
                fixed_income_sorted1.columns = [
                    "Contract Number",
                    "Trade Number",
                    "Asset Class",
                    "Instrument",
                    "Product Type",
                    "Value",
                    "Day change",
                    "Monthly change",
                ]
                table = table_to_html(
                    fixed_income_sorted1, fixed_income_sorted1.columns
                )
                context["content"] = table
        elif func == "view_insights":
            if "portfolio_valuation" not in globals():
                portfolio_valuation = pf.value_portfolio(read_from_db=False)
            final_para = ""
            final_para += f"<div class='row'><div class='col-md-12 grid-margin stretch-card'><div class='card'><div class='card-body'><p style='font-size : 14px'> The total number of assets in the entire portfolio is {len(portfolio_valuation)}. The differnet products in the portfolio consists of "
            products = portfolio_valuation["product_type"].unique()
            if len(products) > 2:
                for i in range(0, len(products) - 2):
                    if i == len(products) - 1:
                        final_para += f"{products[i]}."
                    else:
                        final_para += f"{products[i]}, "
                final_para += f"and {products[len(products)-1]}."
            elif len(products) == 2:
                for i in range(0, len(products) - 1):
                    final_para += f"{products[i]}"
                final_para += f" and {products[len(products)-1]}."
            else:
                final_para += f"{products[len(products)-1]}."

            final_para += "</p></div></div></div></div>"
            final_para += "<div class='row' style='margin-bottom: 10px;'><div class='col-md-5 grid-margin stretch-card'><div class='card'><div class='card-body'><canvas id='AllInsights-chart'></canvas></div></div></div>"
            # final_para = "<div class=col-3></div>"
            val = sum(portfolio_valuation["valuation"])

            # final_para = ""
            # final_para += f"<p>The total number of deals in the entire portfolio is {len(portfolio_valuation)}</p>"
            # final_para += (
            #     f"<p>The different products in this portfolio are {portfolio_valuation['product_type'].unique()}</p>"
            # )
            three_class = portfolio_valuation.groupby("asset_class").sum().reset_index()
            three_class = three_class.sort_values(
                by="valuation", ascending=False
            ).reset_index()
            three_class = three_class.loc[:, ["asset_class", "valuation"]]
            dict_class = {
                "labels": list(three_class["asset_class"]),
                "values": list(three_class["valuation"]),
            }

            final_para += "<div class='col-md-7 grid-margin stretch-card'><div class='card'><div class='card-body'>"
            final_para += f"<p style='font-size : 14px'>The portfolio class have the following exposure:-"
            for i in range(0, len(three_class)):
                final_para += f"<li style='font-size : 14px'> The {three_class['asset_class'][i]} portfolio has a exposure of {round((three_class['valuation'][i]/val)*100 ,2)}%.</li>"
            final_para += "</p></div></div></div></div>"

            final_para += "<div></div><div class='row' style='margin-bottom: 20px;'><div class='col-md-5 grid-margin stretch-card'><div class='card'><div class='card-body'><canvas id='AllInsights_bar-chart'></canvas></div></div></div>"
            exposure = portfolio_valuation.groupby("product_type").sum().reset_index()
            exposure = exposure.sort_values(
                by="valuation", ascending=False
            ).reset_index()
            exposure = exposure.loc[:, ["product_type", "valuation"]]
            dict_class_bar = {
                "labels": list(exposure["product_type"]),
                "values": list(exposure["valuation"]),
            }
            final_para += "<div class='col-md-7 grid-margin stretch-card'><div class='card'><div class='card-body'>"
            final_para += "<p style='font-size : 14px'>The product types have the following exposure:-"
            for i in range(0, len(exposure)):
                final_para += f"<li style='font-size : 14px'>{exposure['product_type'][i]} has a exposure of {round((exposure['valuation'][i]/val)*100 ,2)}%.</li>"
            final_para += "</p></div></div></div></div>"

            context["content"] = final_para
            context["data"] = dict_class
            context["data_bar"] = dict_class_bar

        elif func == "clickable_func":
            if "portfolio_valuation" not in globals():
                portfolio_valuation = pf.value_portfolio(read_from_db=False)

            final_table = portfolio_valuation.loc[
                portfolio_valuation["product_type"] == data["product"]
            ].reset_index(drop=True)
            final_table_sorted = final_table.copy()
            table = table_to_html(final_table_sorted, final_table_sorted.columns)
            context["content"] = table
            print(table)

    return HttpResponse(json.dumps(context))
