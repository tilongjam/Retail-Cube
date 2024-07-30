import datetime as dt
import json
import os
import sys

# from tqdm import tqdm
import time
import warnings

# import dask
import pandas as pd
from joblib import Parallel, delayed

from RetailCube.Core import marketData
from utils import data_handling, dateConversion
from Valuations.pricingFunctions import (
    BondwithForeignCurrencyPricer,
    BondwithOptionPricer,
    CCSPricer,
    CDPricer,
    CommercialPaperPricer,
    CorporateBondPricer,
    CurrencyForwardsPricer,
    CurrencyFuturesPricer,
    FXSpotPricer,
    FXswapPricer,
    IRSPricer,
    NDFPricer,
    PerpetualBondPricer,
    StripsPricer,
    SwapPricer,
    Swaptions,
    ZCBPricer,
    fxOptionPricer,
    gSecPricer,
)

# from dask import delayed
# from dask.distributed import Client


# client = Client(n_workers=8)


class Portfolio:
    def __init__(self, date, portfolio_name, mdc=None):
        self.date = date  # QuantLibDate
        self.date_string = dateConversion.date_convert(self.date).convert_date("string")

        self.date_datetime = dateConversion.date_convert(self.date).convert_date(
            "datetime"
        )
        print(self.date_datetime)
        self.date_30 = self.date_datetime - dt.timedelta(
            days=30
        )  # This needs to be changed
        # If there is a holdiay the take the pervious date or after date

        self.date_30_ql = dateConversion.date_convert(self.date_30).convert_date("ql")
        self.date_datetime = self.date_datetime.date()
        self.date_30 = self.date_30.date()

        self.portfolio_name = portfolio_name
        # self.deals = data_handling.read_data_func(
        #     "portfolio_details",
        #     "*",
        #     [f"date='{self.date_string}'", f"portfolio='{self.portfolio_name}'"],
        # )
        self.deals = data_handling.read_data_func(
            "portfolio_details",
            "*",
            [f"portfolio='{self.portfolio_name}'"],
        )
        self.deals = pd.DataFrame.from_records(
            self.deals["data"], columns=self.deals["columns"]
        )
        print("Deals Length: ", len(self.deals))
        if mdc:
            print("MDC Present")
            self.mdc = mdc
        else:
            print("Creating MDC")
            s = time.time()
            sys.stdout = open(os.devnull, "w")
            self.mdc = marketData.MarketData(self.date)
            self.shocked_mdc = marketData.MarketData(self.date)
            self.mdc.createAll()
            self.shocked_mdc.createAll()
            sys.stdout = sys.__stdout__
            self.mdc.create_interpolated_curves()
            self.mdc.create_shocks()
            self.shocked_mdc.create_interpolated_curves()
            self.shocked_mdc.create_shocks()
            e = time.time()
            print("Time taken to create MDC: ", e - s)

            # print("Creating MDC")
            # s = time.time()
            # sys.stdout = open(os.devnull, "w")
            # self.mdc_30 = marketData.MarketData(self.date_30_ql)
            # self.shocked_mdc_30 = marketData.MarketData(self.date_30_ql)
            # self.mdc_30.createAll()
            # self.shocked_mdc_30.createAll()
            # sys.stdout = sys.__stdout__
            # self.mdc_30.create_interpolated_curves()
            # self.mdc_30.create_shocks()
            # self.shocked_mdc_30.create_interpolated_curves()
            # self.shocked_mdc_30.create_shocks()
            # e = time.time()
            # print("Time taken to create MDC: ", e - s)

        self.shocked_mdc.interpolated_rates = self.shocked_mdc.interpolated_rates_shocks
        self.shocked_mdc.interpolated_dfs = self.shocked_mdc.interpolated_dfs_shocks
        self.shocked_mdc.interpolated_dfs_dict = (
            self.shocked_mdc.interpolated_dfs_dict_shocks
        )
        self.shocked_mdc.forward_rate = self.shocked_mdc.forward_rate_shocked
        self.curve_mapper = data_handling.read_data_func(
            "curve_mapper", "*", ["instrument='Swaps'"]
        )
        self.curve_mapper_option = data_handling.read_data_func(
            "curve_mapper", "*", ["instrument='FX Options'"]
        )
        self.reset_curve_mapper = data_handling.read_data_func("reset_curve_mapping")
        self.final_valuations = pd.DataFrame(
            columns=[
                "date",
                "portfolio",
                "asset_class",
                "product_type",
                "contract_number",
                "trade_number",
                "valuation",
                # "last_modified",
            ]
        )
        self.sensitivities = pd.DataFrame(
            columns=[
                "date",
                "portfolio",
                "asset_class",
                "product_type",
                "instrument",
                "contract_number",
                "trade_number",
                "numerical_delta",
                "numerical_gamma",
                "numerical_vega",
                "numerical_rho",
                "numerical_phi",
                "theoretical_delta",
                "theoretical_gamma",
                "theoretical_vega",
                "theoretical_rho",
                "theoretical_phi",
                "pv01",
                "duration",
                "convexity",
                "last_modified",
            ]
        )
        self.sensitivity_shocks = data_handling.read_data_func(
            "sensitivity_shocks", "*", []
        )
        self.sensitivity_shocks = pd.DataFrame.from_records(
            self.sensitivity_shocks["data"], columns=self.sensitivity_shocks["columns"]
        )
        # Creating Shocked MDCs
        self.mdc_dict = {}
        for asset_class in self.sensitivity_shocks["asset_class"].unique():
            self.mdc_dict[asset_class] = dict()
        for i in range(len(self.sensitivity_shocks)):
            asset_class = self.sensitivity_shocks.loc[i, "asset_class"]
            risk_factor = self.sensitivity_shocks.loc[i, "risk_factor"]
            shock_value = self.sensitivity_shocks.loc[i, "shock_value"]
            shock_type = self.sensitivity_shocks.loc[i, "shock_type"]
            shock_unit = self.sensitivity_shocks.loc[i, "shock_unit"]
            if asset_class == "FX Options":
                if risk_factor == "Spot Delta":
                    for scenario in ["Spot Up", "Spot Down"]:
                        sys.stdout = open(os.devnull, "w")
                        shocked_mdc = marketData.MarketData(self.date)
                        shocked_mdc.createAll()

                        # No need to create all.
                        sys.stdout = sys.__stdout__
                        if scenario == "Spot Down":
                            shock_value = -1 * shock_value
                        for curr in shocked_mdc.spotList:
                            shocked_mdc.create_shock(
                                "FX Spot",
                                curr,
                                shock_value,
                                shock_unit,
                                shock_type,
                            )
                        self.mdc_dict[asset_class][scenario] = shocked_mdc

                elif risk_factor == "Spot Gamma":
                    for scenario in ["Spot Up Up", "Spot Down Down", "Spot Up Down"]:
                        shocked_mdc = marketData.MarketData(self.date)
                        shocked_mdc.createAll()
                        for curr in shocked_mdc.spotList:
                            if scenario == "Spot Up Up":
                                shocked_mdc.create_shock(
                                    "FX Spot",
                                    curr,
                                    shock_value,
                                    shock_unit,
                                    shock_type,
                                )
                                shocked_mdc.create_shock(
                                    "FX Spot",
                                    curr,
                                    shock_value,
                                    shock_unit,
                                    shock_type,
                                )
                            elif scenario == "Spot Down Down":
                                shocked_mdc.create_shock(
                                    "FX Spot",
                                    curr,
                                    -1 * shock_value,
                                    shock_unit,
                                    shock_type,
                                )
                                shocked_mdc.create_shock(
                                    "FX Spot",
                                    curr,
                                    -1 * shock_value,
                                    shock_unit,
                                    shock_type,
                                )
                            elif scenario == "Spot Up Down":
                                shocked_mdc.create_shock(
                                    "FX Spot",
                                    curr,
                                    shock_value,
                                    shock_unit,
                                    shock_type,
                                )
                                shocked_mdc.create_shock(
                                    "FX Spot",
                                    curr,
                                    -1 * shock_value,
                                    shock_unit,
                                    shock_type,
                                )
                        self.mdc_dict[asset_class][scenario] = shocked_mdc

                elif risk_factor == "Volatility":
                    for scenario in ["Vol Up", "Vol Down"]:
                        shocked_mdc = marketData.MarketData(self.date)
                        shocked_mdc.createAll()
                        if scenario == "Vol Down":
                            shock_value = -1 * shock_value
                        for vol_surface in shocked_mdc.volList:
                            shocked_mdc.create_shock(
                                "FX Volatilities",
                                vol_surface,
                                shock_value,
                                shock_unit,
                                shock_type,
                            )
                        self.mdc_dict[asset_class][scenario] = shocked_mdc

    def value_deal(self, val_date, mdc, deal_details: dict):
        asset_class = deal_details["asset_class"]
        product_type = deal_details["product_type"]
        contract_number = deal_details["contract_number"]
        trade_number = deal_details["trade_number"]
        trade_details = deal_details["trade_details"]
        value_dict = {}
        s = time.time()

        def value_fx_option(
            val_date, trade_details, contract_number, trade_number, curve_mapper_option
        ):
            option = fxOptionPricer.fxOption(
                val_date,
                trade_details,
                contract_number,
                trade_number,
                curve_mapper_option,
            )
            final_value = option.value_with(mdc)
            instrument = option.curr_pair
            return final_value, instrument

        def value_fx_swap(val_date, trade_details, contract_number, trade_number):
            swap = FXswapPricer.FxSwap(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = swap.value_with(mdc)
            instrument = swap.trade_details["product_type"]
            return final_value, instrument

        def value_ndf(val_date, trade_details, contract_number, trade_number):
            ndf = NDFPricer.NDFPricer(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = ndf.value_with(mdc)
            instrument = ndf.trade_details["product_type"]
            return final_value, instrument

        def value_currency_forward(
            val_date, trade_details, contract_number, trade_number
        ):
            forwards = CurrencyForwardsPricer.CurrencyForwardPricer(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = forwards.value_with(mdc)
            instrument = forwards.trade_details["product_type"]
            return final_value, instrument

        def value_currency_futures(
            val_date, trade_details, contract_number, trade_number
        ):
            futures = CurrencyFuturesPricer.CurrencyFuture(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = futures.value_with(mdc)
            instrument = futures.trade_details["product_type"]
            return final_value, instrument

        def value_spot(val_date, trade_details, contract_number, trade_number):
            spot = FXSpotPricer.Spot(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = spot.value_with(mdc)
            instrument = "Spot"
            return final_value, instrument

        def value_irs(val_date, trade_details, contract_number, trade_number):
            swap = IRSPricer.IRS(val_date, trade_details, contract_number, trade_number)
            final_value = swap.value_with(mdc)
            instrument = "IRS"
            return final_value, instrument

        def value_ccs(val_date, trade_details, contract_number, trade_number):
            swap = CCSPricer.CCS(val_date, trade_details, contract_number, trade_number)
            final_value = swap.value_with(mdc)
            instrument = "CCS"
            return final_value, instrument

        def value_gsec(val_date, trade_details, contract_number, trade_number):
            gsec = gSecPricer.GSecPricer(
                val_date, trade_details, contract_number, trade_number
            )
            if (trade_details["yield"] == 0) or (trade_details["yield"] is None):
                final_value = gsec.value_with(mdc)
            else:
                final_value = gsec.value_with(mdc)
            instrument = gsec.trade_details["product_type"]
            return final_value, instrument

        def value_debenture(val_date, trade_details, contract_number, trade_number):
            corporate_bond = CorporateBondPricer.CorporateBond(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = corporate_bond.value_with(mdc)
            instrument = corporate_bond.trade_details["product_type"]
            return final_value, instrument

        def value_commercial_paper(
            val_date, trade_details, contract_number, trade_number
        ):
            cp = CommercialPaperPricer.CommercialPaper(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = cp.value_with(mdc)
            instrument = cp.trade_details["product_type"]
            return final_value, instrument

        def value_cd(val_date, trade_details, contract_number, trade_number):
            cd = CDPricer.CD(val_date, trade_details, contract_number, trade_number)
            final_value = cd.value_with(mdc)
            instrument = cd.trade_details["product_type"]
            return final_value, instrument

        def value_fcb(val_date, trade_details, contract_number, trade_number):
            fcb = BondwithForeignCurrencyPricer.ForeignBondPricer(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = fcb.value_with(mdc)
            instrument = fcb.trade_details["product_type"]
            return final_value, instrument

        def value_bond_with_option(
            val_date, trade_details, contract_number, trade_number
        ):
            option = BondwithOptionPricer.BondWithOption(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = option.value_with(mdc)
            instrument = option.trade_details["product_type"]
            return final_value, instrument

        def value_perpetual_bond(
            val_date, trade_details, contract_number, trade_number
        ):
            bond = PerpetualBondPricer.PerpetualBond(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = bond.value_with(mdc)
            instrument = bond.trade_details["product_type"]
            return final_value, instrument

        def value_strips(val_date, trade_details, contract_number, trade_number):
            strips = StripsPricer.StripPricer(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = strips.value_with(mdc)
            instrument = strips.trade_details["product_type"]
            return final_value, instrument

        def value_zcb(val_date, trade_details, contract_number, trade_number):
            zcb = ZCBPricer.ZCB(val_date, trade_details, contract_number, trade_number)
            final_value = zcb.value_with(mdc)
            instrument = zcb.trade_details["product_type"]
            return final_value, instrument

        def value_swaption(val_date, trade_details, contract_number, trade_number):
            swaption = Swaptions.Swaption(
                val_date, trade_details, contract_number, trade_number
            )
            final_value = swaption.value_with(mdc)
            instrument = swaption.trade_details["product_type"]
            return final_value, instrument

        value_functions = {
            "Forex": {
                "Options": value_fx_option,
                "FX Swaps": value_fx_swap,
                "NDF": value_ndf,
                "Currency Forwards": value_currency_forward,
                "Currency Futures": value_currency_futures,
                "Spot": value_spot,
                "Swaption": value_swaption,
            },
            "Interest Rate": {"IRS": value_irs, "CCS": value_ccs},
            "Fixed Income": {
                "GSEC": value_gsec,
                "Debenture": value_debenture,
                "Commercial Paper": value_commercial_paper,
                "CD": value_cd,
                "FCB": value_fcb,
                "Bond with Option": value_bond_with_option,
                "Perpetual Bond": value_perpetual_bond,
                "Strips": value_strips,
                "ZCB": value_zcb,
            }
            # Add other asset classes, product types, and value functions here
        }

        value_func = value_functions[asset_class][product_type]
        if product_type == "Options":
            final_value, instrument = value_func(
                val_date,
                trade_details,
                contract_number,
                trade_number,
                self.curve_mapper_option,
            )
        else:
            final_value, instrument = value_func(
                val_date, trade_details, contract_number, trade_number
            )
        e = time.time()
        time_elapsed = e - s
        value_dict["date"] = dateConversion.date_convert(val_date).convert_date(
            "string"
        )
        value_dict["portfolio"] = self.portfolio_name
        value_dict["asset_class"] = asset_class
        value_dict["product_type"] = product_type
        value_dict["instrument"] = instrument
        value_dict["contract_number"] = contract_number
        value_dict["trade_number"] = trade_number
        value_dict["valuation"] = final_value
        value_dict["time_elapsed"] = time_elapsed
        # value_df = pd.DataFrame.from_dict(value_dict)
        # self.final_valuations = pd.concat([self.final_valuations, value_df])
        # print(self.final_valuations)
        return value_dict

    # def value_deal(self, mdc, deal_details: dict):
    #     asset_class = deal_details["asset_class"]
    #     product_type = deal_details["product_type"]
    #     contract_number = deal_details["contract_number"]
    #     trade_number = deal_details["trade_number"]
    #     trade_details = deal_details["trade_details"]
    #     value_dict = {}

    #     # Pass in new asset classes and product types here
    #     # Ensure to include instrument, for eg: USDINR is a forex instrument.
    #     if asset_class == "Forex":
    #         if product_type == "Options":
    #             s = time.time()
    #             option = fxOptionPricer.fxOption(trade_details, contract_number, trade_number, self.curve_mapper_option)
    #             final_value = option.value_with(mdc)
    #             instrument = option.curr_pair
    #             e = time.time()
    #             time_elapsed = e - s

    #         elif product_type == "FX Swaps":
    #             s = time.time()
    #             swap = FXswapPricer.FxSwap(trade_details, contract_number, trade_number)
    #             final_value = swap.value_with(mdc)
    #             instrument = swap.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #         elif product_type == "NDF":
    #             s = time.time()
    #             ndf = NDFPricer.NDFPricer(trade_details, contract_number, trade_number)
    #             final_value = ndf.value_with(mdc)
    #             instrument = ndf.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #         elif product_type == "Currency Forwards":
    #             s = time.time()
    #             forwards = CurrencyForwardsPricer.CurrencyForwardPricer(trade_details, contract_number, trade_details)
    #             final_value = forwards.value_with(self.mdc)
    #             instrument = forwards.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #         elif product_type == "Currency Futures":
    #             s = time.time()
    #             futures = CurrencyFuturesPricer.CurrencyFuture(trade_details, contract_number, trade_number)
    #             final_value = futures.value_with(self.mdc)
    #             instrument = futures.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #         elif product_type == "Spot":
    #             s = time.time()
    #             spot = FXSpotPricer.Spot(trade_details,contract_number,trade_number)
    #             final_value = spot.value_with(self.mdc)
    #             instrument = spot.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #     elif asset_class == "Interest Rate":
    #         if product_type == "IRS":
    #             s = time.time()
    #             swap = IRSPricer.IRS(trade_details, contract_number, trade_number)
    #             final_value = swap.value_with(mdc)
    #             # instrument = swap.trade_details["product_type"]
    #             instrument = "IRS"
    #             e = time.time()
    #             time_elapsed = e - s

    #         if product_type == "CCS":
    #             s = time.time()
    #             swap = CCSPricer.CCS(trade_details, contract_number, trade_number)
    #             final_value = swap.value_with(mdc)
    #             # instrument = json.dumps(swap.instruments)
    #             instrument = "CCS"
    #             e = time.time()
    #             time_elapsed = e - s

    #     elif asset_class == "Fixed Income":
    #         if product_type == "GSEC":
    #             s = time.time()
    #             gsec = gSecPricer.GSecPricer(trade_details, contract_number, trade_number)
    #             if (trade_details["yield"] == 0) | (trade_details["yield"] is None):
    #                 final_value = gsec.value_with(mdc)
    #             else:
    #                 final_value = gsec.value_with()
    #             instrument = gsec.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s
    #         elif product_type == "Debenture":
    #             s = time.time()
    #             corporate_bond = CorporateBondPricer.CorporateBond(trade_details, contract_number, trade_number)
    #             final_value = corporate_bond.value_with(mdc)
    #             instrument = corporate_bond.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s
    #         elif product_type == "Commercial Paper":
    #             s = time.time()
    #             cp = CommercialPaperPricer.CommercialPaper(trade_details, contract_number, trade_number)
    #             final_value = cp.value_with(self.mdc)
    #             instrument = cp.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #         elif product_type == "CD":
    #             s = time.time()
    #             cd = CDPricer.CD(trade_details, contract_number, trade_number)
    #             final_value = cd.value_with(self.mdc)
    #             instrument = cd.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #         elif product_type == "FCB":
    #             s = time.time()
    #             fcb = BondwithForeignCurrencyPricer.ForeignBondPricer(trade_details, contract_number, trade_number)
    #             final_value = fcb.value_with(self.mdc)
    #             instrument = fcb.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #         elif product_type == "Bond with Option":
    #             s = time.time()
    #             option = BondwithOptionPricer.BondWithOption(trade_details, contract_number, trade_number)
    #             final_value = option.value_with(self.mdc)
    #             instrument = option.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #         elif product_type == "Perpetual Bond":
    #             s = time.time()
    #             bond = PerpetualBondPricer.PerpetualBond(trade_details, contract_number, trade_number)
    #             final_value = bond.value_with(self.mdc)
    #             instrument = bond.trade_details["product_type"]
    #             e = time.time()
    #             time_elapsed = e - s

    #     value_dict["date"] = dateConversion.date_convert(self.date).convert_date("string")
    #     value_dict["portfolio"] = self.portfolio_name
    #     value_dict["asset_class"] = asset_class
    #     value_dict["product_type"] = product_type
    #     value_dict["instrument"] = instrument
    #     value_dict["contract_number"] = contract_number
    #     value_dict["trade_number"] = trade_number
    #     value_dict["valuation"] = final_value
    #     value_dict["time_elapsed"] = time_elapsed
    #     # value_df = pd.DataFrame.from_dict(value_dict)
    #     # self.final_valuations = pd.concat([self.final_valuations, value_df])
    #     # print(self.final_valuations)
    #     return value_dict

    # def value_portfolio(self, write_to_db=True, read_from_db=False):
    #     if (write_to_db is True) & (read_from_db is True):
    #         write_to_db = False
    #         warnings.warn("Warning: If specifying read_to_db, explicitly set write_to_db as False")

    #     if write_to_db:
    #         delayed_list = []
    #         for i in range(len(self.deals)):
    #             deal_dict = {}
    #             deal_dict["asset_class"] = self.deals.loc[i, "asset_class"]
    #             deal_dict["product_type"] = self.deals.loc[i, "product_type"]
    #             deal_dict["contract_number"] = self.deals.loc[i, "contract_number"]
    #             deal_dict["trade_number"] = self.deals.loc[i, "trade_number"]
    #             deal_dict["trade_details"] = json.loads(self.deals.loc[i, "trade_details"])
    #             delayed_list.append(delayed(self.value_deal)(self.mdc, deal_dict))
    #             # delayed_computation = delayed(self.value_deal)(self.mdc, deal_dict)
    #             # delayed_list.append(delayed_computation)
    #         # parallel_output = dask.compute(*delayed_list, scheduler="threads")
    #         parallel_output = Parallel(n_jobs=-2, backend="threading", verbose=1)(delayed_list)
    #         self.final_valuations = pd.DataFrame.from_records(parallel_output)
    #         test_output = self.final_valuations.groupby("product_type").agg(
    #             {"contract_number": "count", "time_elapsed": "sum"}
    #         )
    #         test_output["Time for 100 Deals"] = 100 * test_output["time_elapsed"] / test_output["contract_number"]
    #         print(test_output)
    #         self.final_valuations = self.final_valuations.drop("time_elapsed", axis=1)
    #         valuation = json.dumps(self.final_valuations.to_dict("records"))
    #         date = dateConversion.date_convert(self.date).convert_date("string")
    #         push_to_db = pd.DataFrame({"date": [date], "portfolio_valuation": valuation})
    #         data_handling.write_data_func("portfolio_valuations_test", push_to_db)
    #     elif read_from_db:
    #         sql_data = data_handling.read_data_func("portfolio_valuations")
    #         self.final_valuations = pd.DataFrame.from_records(sql_data["data"], columns=sql_data["columns"])
    #         self.final_valuations = self.final_valuations[
    #             self.final_valuations["last_modified"] == max(self.final_valuations["last_modified"])
    #         ]
    #     # for i in range(len(self.final_valuations)):
    #     #     query = f"""INSERT INTO dbo.portfolio_valuations (date, portfolio, asset_class, product_type, contract_number, trade_number, valuation, last_modified) VALUES ('{self.final_valuations.loc[i, "date"]}', '{self.final_valuations.loc[i, "portfolio"]}', '{self.final_valuations.loc[i, "asset_class"]}', '{self.final_valuations.loc[i, "product_type"]}', '{self.final_valuations.loc[i, "contract_number"]}', '{self.final_valuations.loc[i, "trade_number"]}', '{self.final_valuations.loc[i, "valuation"]}', '{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')"""
    #     #     print(query)
    #     #     connection.execute(text(query))
    #     #     print("Executed")
    #     return self.final_valuations
    def value_portfolio(self, write_to_db=True, read_from_db=False):
        if (write_to_db is True) & (read_from_db is True):
            write_to_db = False
            warnings.warn(
                "Warning: If specifying read_to_db, explicitly set write_to_db as False"
            )

        if write_to_db:
            delayed_list = []
            s = time.time()
            delayed_list = [
                delayed(self.value_deal)(
                    self.date,
                    self.mdc,
                    {
                        "asset_class": self.deals.loc[i, "asset_class"],
                        "product_type": self.deals.loc[i, "product_type"],
                        "contract_number": self.deals.loc[i, "contract_number"],
                        "trade_number": self.deals.loc[i, "trade_number"],
                        "trade_details": json.loads(self.deals.loc[i, "trade_details"]),
                    },
                )
                for i in range(len(self.deals))
            ]
            e = time.time()
            print(e - s)
            parallel_output = Parallel(n_jobs=-2, backend="threading", verbose=1)(
                delayed_list
            )
            self.final_valuations = pd.DataFrame.from_records(parallel_output)
            test_output = self.final_valuations.groupby("product_type").agg(
                {"contract_number": "count", "time_elapsed": "sum"}
            )
            test_output["Time for 100 Deals"] = (
                100 * test_output["time_elapsed"] / test_output["contract_number"]
            )
            self.final_valuations = self.final_valuations.drop("time_elapsed", axis=1)

            # delayed_list_30 = [
            #     delayed(self.value_deal)(
            #         self.date_30_ql,
            #         self.mdc_30,
            #         {
            #             "asset_class": self.deals.loc[i, "asset_class"],
            #             "product_type": self.deals.loc[i, "product_type"],
            #             "contract_number": self.deals.loc[i, "contract_number"],
            #             "trade_number": self.deals.loc[i, "trade_number"],
            #             "trade_details": json.loads(self.deals.loc[i, "trade_details"]),
            #         },
            #     )
            #     for i in range(len(self.deals))
            # ]
            # e = time.time()
            # print(e - s)
            # parallel_output_30 = Parallel(n_jobs=-2, backend="threading", verbose=1)(delayed_list_30)
            # self.final_valuations_30 = pd.DataFrame.from_records(parallel_output_30)
            # test_output_30 = self.final_valuations_30.groupby("product_type").agg(
            #     {"contract_number": "count", "time_elapsed": "sum"}
            # )
            # test_output_30["Time for 100 Deals"] = (
            #     100 * test_output_30["time_elapsed"] / test_output_30["contract_number"]
            # )
            # print(test_output)
            # self.final_valuations_30 = self.final_valuations_30.drop("time_elapsed", axis=1)
            valuation = json.dumps(self.final_valuations.to_dict("records"))
            # valuation_30 = json.dumps(self.final_valuations_30.to_dict("records"))

            date_string = dateConversion.date_convert(self.date).convert_date("string")
            # date_30_string = dateConversion.date_convert(self.date_30_ql).convert_date("string")

            portfolio = self.portfolio_name

            # print(date_30_string)
            push_to_db = pd.DataFrame(
                {
                    "date": [date_string],
                    "portfolio_valuation": valuation,
                    "portfolio": [portfolio],
                }
            )
            # push_to_db_30 = pd.DataFrame(
            #     {"date": [date_30_string], "portfolio_valuation": valuation_30, "portfolio": [portfolio]}
            # )

            data_handling.write_data_func("portfolio_valuations_test", push_to_db)
            # data_handling.write_data_func("portfolio_valuations_test", push_to_db_30)
        elif read_from_db:
            sql_data = data_handling.read_data_func("portfolio_valuations_test")
            self.final_valuations = pd.DataFrame.from_records(
                sql_data["data"], columns=sql_data["columns"]
            )
            self.final_valuations = self.final_valuations[
                self.final_valuations["last_modified"]
                == max(self.final_valuations["last_modified"])
            ]
        return self.final_valuations

    def compute_deal_sensitvities(self, val_date, mdc, shocked_mdc, deal_details: dict):
        self.sensitivities = {}
        # Looping over portfolio to get sensitivities
        # for i in range(len(self.deals)):
        asset_class_deal = deal_details["asset_class"]
        product_type = deal_details["product_type"]
        contract_number = deal_details["contract_number"]
        trade_number = deal_details["trade_number"]
        trade_details = deal_details["trade_details"]
        # trade_details = json.loads(self.deals.loc[i, "trade_details"])
        # Pass in new asset classes and product types here
        # Ensure to include instrument, for eg: USDINR is a forex instrument.
        if asset_class_deal == "Forex":
            if product_type == "Options":
                option = fxOptionPricer.fxOption(
                    trade_details,
                    contract_number,
                    trade_number,
                    self.curve_mapper_option,
                )
                # option.value_with(self.mdc)
                theoretical_greeks = option.compute_sensitivities(mdc)

                delta = (
                    option.value_with(self.mdc_dict["FX Options"]["Spot Up"])
                    - option.value_with(self.mdc_dict["FX Options"]["Spot Down"])
                ) / (
                    self.mdc_dict["FX Options"]["Spot Up"]
                    .fetch("FX Spot", option.curr_pair)
                    .rate
                    - self.mdc_dict["FX Options"]["Spot Down"]
                    .fetch("FX Spot", option.curr_pair)
                    .rate
                )

                delta_up = (
                    option.value_with(self.mdc_dict["FX Options"]["Spot Up Up"])
                    - option.value_with(self.mdc_dict["FX Options"]["Spot Up Down"])
                ) / (
                    self.mdc_dict["FX Options"]["Spot Up Up"]
                    .fetch("FX Spot", option.curr_pair)
                    .rate
                    - self.mdc_dict["FX Options"]["Spot Up Down"]
                    .fetch("FX Spot", option.curr_pair)
                    .rate
                )

                delta_down = (
                    option.value_with(self.mdc_dict["FX Options"]["Spot Up Down"])
                    - option.value_with(self.mdc_dict["FX Options"]["Spot Down Down"])
                ) / (
                    self.mdc_dict["FX Options"]["Spot Up Down"]
                    .fetch("FX Spot", option.curr_pair)
                    .rate
                    - self.mdc_dict["FX Options"]["Spot Down Down"]
                    .fetch("FX Spot", option.curr_pair)
                    .rate
                )

                gamma = (delta_up - delta_down) / (
                    self.mdc_dict["FX Options"]["Spot Up"]
                    .fetch("FX Spot", option.curr_pair)
                    .rate
                    - self.mdc_dict["FX Options"]["Spot Down"]
                    .fetch("FX Spot", option.curr_pair)
                    .rate
                )

                vol_shock = self.sensitivity_shocks.loc[
                    (self.sensitivity_shocks["asset_class"] == "FX Options")
                    & (self.sensitivity_shocks["risk_factor"] == "Volatility"),
                    "shock_value",
                ].values[0]
                vega = (
                    option.value_with(self.mdc_dict["FX Options"]["Vol Up"])
                    - option.value_with(self.mdc_dict["FX Options"]["Vol Down"])
                ) / (2 * vol_shock)

                ir_shock = self.sensitivity_shocks.loc[
                    (self.sensitivity_shocks["asset_class"] == "FX Options")
                    & (self.sensitivity_shocks["risk_factor"] == "Interest Rate"),
                    "shock_value",
                ].values[0]
                rho = (
                    option.value_with(self.mdc, shock_rd=True, shock_value=ir_shock)
                    - option.value_with(
                        self.mdc, shock_rd=True, shock_value=-1 * ir_shock
                    )
                ) / (2 * ir_shock)

                phi = (
                    option.value_with(self.mdc, shock_rf=True, shock_value=ir_shock)
                    - option.value_with(
                        self.mdc, shock_rf=True, shock_value=-1 * ir_shock
                    )
                ) / (2 * ir_shock)

                self.sensitivities["date"] = dateConversion.date_convert(
                    self.date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = option.curr_pair
                self.sensitivities["contract_number"] = option.cnt_nb
                self.sensitivities["trade_number"] = option.trade_no
                self.sensitivities["numerical_delta"] = delta
                self.sensitivities["numerical_gamma"] = gamma
                self.sensitivities["numerical_vega"] = vega
                self.sensitivities["numerical_rho"] = rho
                self.sensitivities["numerical_phi"] = phi
                self.sensitivities["theoretical_delta"] = theoretical_greeks["delta"]
                self.sensitivities["theoretical_gamma"] = theoretical_greeks["gamma"]
                self.sensitivities["theoretical_vega"] = theoretical_greeks["vega"]
                self.sensitivities["theoretical_rho"] = theoretical_greeks["rho"]
                self.sensitivities["theoretical_phi"] = theoretical_greeks["phi"]
                self.sensitivities["pv01"] = 0
                self.sensitivities["duration"] = 0
                self.sensitivities["convexity"] = 0
                self.sensitivities["risk_factors"] = json.dumps(
                    theoretical_greeks["risk_factors"]
                )

            elif product_type == "FX Swaps":
                s = time.time()
                deal = FXswapPricer.FxSwap(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities["PV01"]
                self.sensitivities["duration"] = 0
                self.sensitivities["convexity"] = 0
                self.sensitivities["risk_factors"] = []
                e = time.time()
                self.sensitivities["time_elapsed"] = time.time() - s

            elif product_type == "NDF":
                s = time.time()
                deal = NDFPricer.NDFPricer(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                # print(sensitivities)
                # print(sensitivities["PV01"])
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities.loc[0, "PV01"]
                self.sensitivities["duration"] = 0
                self.sensitivities["convexity"] = 0
                self.sensitivities["risk_factors"] = []
                e = time.time()
                time_elapsed = s - e
                self.sensitivities["time_elapsed"] = time.time() - s

            elif product_type == "Currency Futures":
                s = time.time()
                deal = CurrencyFuturesPricer.CurrencyFuture(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities["PV01"]
                self.sensitivities["duration"] = 0
                self.sensitivities["convexity"] = 0
                self.sensitivities["risk_factors"] = []
                e = time.time()
                time_elapsed = s - e
                self.sensitivities["time_elapsed"] = time.time() - s

            elif product_type == "Currency Forwards":
                s = time.time()
                deal = CurrencyForwardsPricer.CurrencyForwardPricer(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities["pv01"][0]
                self.sensitivities["duration"] = 0
                self.sensitivities["convexity"] = 0
                self.sensitivities["risk_factors"] = []
                self.sensitivities["time_elapsed"] = time.time() - s

        elif asset_class_deal == "Interest Rate":
            if product_type == "IRS":
                s = time.time()
                deal = IRSPricer.IRS(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc, shocked_mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = "IRS"
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = float(sensitivities["pv01"][0])
                self.sensitivities["duration"] = 0
                self.sensitivities["convexity"] = 0
                self.sensitivities["risk_factors"] = []
                # self.sensitivities["risk_factors"] = json.dumps(sensitivities["risk_factors"])
                self.sensitivities["time_elapsed"] = time.time() - s

            elif product_type == "CCS":
                s = time.time()
                deal = CCSPricer.CCS(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc, shocked_mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = "CCS"
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = float(sensitivities["pv01"][0])
                self.sensitivities["duration"] = 0
                self.sensitivities["convexity"] = 0
                self.sensitivities["risk_factors"] = []
                # self.sensitivities["risk_factors"] = json.dumps(sensitivities["risk_factors"])
                self.sensitivities["time_elapsed"] = time.time() - s

        elif asset_class_deal == "Fixed Income":
            if product_type == "GSEC":
                s = time.time()
                deal = gSecPricer.GSecPricer(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = 0
                self.sensitivities["duration"] = 0
                self.sensitivities["convexity"] = 0
                self.sensitivities["risk_factors"] = []
                e = time.time()
                self.sensitivities["time_elapsed"] = time.time() - s

            elif product_type == "Debenture":
                s = time.time()
                deal = CorporateBondPricer.CorporateBond(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities["PV01"][0]
                self.sensitivities["duration"] = sensitivities["Modified Duration"][0]
                self.sensitivities["convexity"] = sensitivities["Convexity"][0]
                self.sensitivities["risk_factors"] = []
                self.sensitivities["time_elapsed"] = time.time() - s

            elif product_type == "Commercial Paper":
                s = time.time()
                deal = CommercialPaperPricer.CommercialPaper(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities["PV01"][0]
                self.sensitivities["duration"] = sensitivities["Modified Duration"][0]
                self.sensitivities["convexity"] = sensitivities["Convexity"][0]
                self.sensitivities["risk_factors"] = []
                e = time.time()
                time_elapsed = s - e
                self.sensitivities["time_elapsed"] = time.time() - s

            elif product_type == "CD":
                s = time.time()
                deal = CDPricer.CD(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities["PV01"][0]
                self.sensitivities["duration"] = sensitivities["Modified Duration"][0]
                self.sensitivities["convexity"] = sensitivities["Convexity"][0]
                self.sensitivities["risk_factors"] = []
                e = time.time()
                time_elapsed = s - e
                self.sensitivities["time_elapsed"] = time.time() - s

            elif product_type == "FCB":
                s = time.time()
                deal = BondwithForeignCurrencyPricer.ForeignBondPricer(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities["PV01"]
                self.sensitivities["duration"] = sensitivities["Modified Duration"]
                self.sensitivities["convexity"] = sensitivities["Convexity"]
                self.sensitivities["risk_factors"] = []
                e = time.time()
                time_elapsed = s - e

            elif product_type == "Bond with Option":
                s = time.time()
                deal = BondwithOptionPricer.BondWithOption(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities["PV01"][0]
                self.sensitivities["duration"] = sensitivities["Modified Duration"][0]
                self.sensitivities["convexity"] = sensitivities["Convexity"][0]
                self.sensitivities["risk_factors"] = []
                e = time.time()
                time_elapsed = s - e
                self.sensitivities["time_elapsed"] = time.time() - s

            elif product_type == "Perpetual Bond":
                deal = PerpetualBondPricer.PerpetualBond(
                    val_date, trade_details, contract_number, trade_number
                )
                sensitivities = deal.compute_sensitivities(mdc)
                self.sensitivities["date"] = dateConversion.date_convert(
                    val_date
                ).convert_date("string")
                self.sensitivities["portfolio"] = self.portfolio_name
                self.sensitivities["asset_class"] = asset_class_deal
                self.sensitivities["product_type"] = product_type
                self.sensitivities["instrument"] = deal.trade_details["product_type"]
                self.sensitivities["contract_number"] = deal.contract_number
                self.sensitivities["trade_number"] = deal.trade_number
                self.sensitivities["numerical_delta"] = 0
                self.sensitivities["numerical_gamma"] = 0
                self.sensitivities["numerical_vega"] = 0
                self.sensitivities["numerical_rho"] = 0
                self.sensitivities["numerical_phi"] = 0
                self.sensitivities["theoretical_delta"] = 0
                self.sensitivities["theoretical_gamma"] = 0
                self.sensitivities["theoretical_vega"] = 0
                self.sensitivities["theoretical_rho"] = 0
                self.sensitivities["theoretical_phi"] = 0
                self.sensitivities["pv01"] = sensitivities["PV01"]
                self.sensitivities["duration"] = sensitivities["Modified Duration"]
                self.sensitivities["convexity"] = sensitivities["Convexity"]
                self.sensitivities["risk_factors"] = []
            # Insert forex products from here
            # Insert new asset classes from here
        # print(self.sensitivities)
        # print("Starting write of data")
        # data_handling.write_data_func("portfolio_sensitivities", self.sensitivities)
        return self.sensitivities

    def compute_portfolio_sensitvities(self, write_to_db=True, read_from_db=False):
        if (write_to_db is True) & (read_from_db is True):
            write_to_db = False
            warnings.warn(
                "Warning: If specifying read_to_db, explicitly set write_to_db as False"
            )

        if write_to_db:
            delayed_list = []
            for i in range(len(self.deals)):
                deal_dict = {}
                deal_dict["asset_class"] = self.deals.loc[i, "asset_class"]
                deal_dict["product_type"] = self.deals.loc[i, "product_type"]
                deal_dict["contract_number"] = self.deals.loc[i, "contract_number"]
                deal_dict["trade_number"] = self.deals.loc[i, "trade_number"]
                deal_dict["trade_details"] = json.loads(
                    self.deals.loc[i, "trade_details"]
                )
                delayed_list.append(
                    delayed(self.compute_deal_sensitvities)(
                        self.date, self.mdc, self.shocked_mdc, deal_dict
                    )
                )
                # delayed_computation = delayed(self.value_deal)(self.mdc, deal_dict)
                # delayed_list.append(delayed_computation)
            # parallel_output = dask.compute(*delayed_list, scheduler="threads")
            parallel_output = Parallel(n_jobs=-2, backend="threading", verbose=1)(
                delayed_list
            )
            self.final_output = pd.DataFrame.from_records(parallel_output)
            test_output = self.final_output.groupby("product_type").agg(
                {"contract_number": "count", "time_elapsed": "sum"}
            )
            test_output["Time for 100 Deals"] = (
                100 * test_output["time_elapsed"] / test_output["contract_number"]
            )
            print(test_output)
            self.final_output = self.final_output.drop("time_elapsed", axis=1)
            # valuation = json.dumps(self.final_output.to_dict("records"))
            # push_to_db = pd.DataFrame(json.loads(valuation))
            # push_to_db = self.final_output
            output = json.dumps(self.final_output.to_dict("records"))
            date = dateConversion.date_convert(self.date).convert_date("string")
            portfolio = self.portfolio_name
            push_to_db = pd.DataFrame(
                {
                    "date": [date],
                    "portfolio_valuation": output,
                    "portfolio": [portfolio],
                }
            )
            data_handling.write_data_func("portfolio_sensitivities_test", push_to_db)
            # data = {}
            # data["date"] = valuation["date"]
            # data["portfolio"] = valuation["portfolio"]
            # data["asset_class"] = valuation["asset_class"]
            # data["product_type"] = valuation["product_type"]
            # data["instrument"] = valuation["instrument"]
            # data["contract_number"] = valuation["contract_number"]
            # data["trade_number"] = valuation["trade_number"]
            # data["numerical_delta"] = valuation["numerical_delta"]
            # data["numerical_gamma"] = valuation["numerical_gamma"]
            # data["numerical_vega"] = valuation["numerical_vega"]
            # data["numerical_rho"] = valuation["numerical_rho"]
            # data["numerical_phi"] = valuation["numerical_phi"]
            # data["theoretical_delta"] = valuation["theoretical_delta"]
            # data["theoretical_gamma"] = valuation["theoretical_gamma"]
            # data["theoretical_vega"] = valuation["theoretical_vega"]
            # data["theoretical_rho"] = valuation["theoretical_rho"]
            # data["theoretical_phi"] = valuation["theoretical_phi"]
            # data["pv01"] = valuation["pv01"]
            # data["duration"] = valuation["duration"]
            # data["convexity"] = valuation["convexity"]
            # data["risk_factors"] = valuation["risk_factors"]

            # date = dateConversion.date_convert(self.date).convert_date("string")
            # push_to_db = pd.DataFrame(data)
            # print(data)
            data_handling.write_data_func("portfolio_sensitivities_test", push_to_db)
        elif read_from_db:
            sql_data = data_handling.read_data_func("portfolio_sensitivities_test")
            self.final_output = pd.DataFrame.from_records(
                sql_data["data"], columns=sql_data["columns"]
            )
            self.final_output = self.final_output[
                self.final_output["last_modified"]
                == max(self.final_output["last_modified"])
            ]
        # for i in range(len(self.final_valuations)):
        #     query = f"""INSERT INTO dbo.portfolio_valuations (date, portfolio, asset_class, product_type, contract_number, trade_number, valuation, last_modified) VALUES ('{self.final_valuations.loc[i, "date"]}', '{self.final_valuations.loc[i, "portfolio"]}', '{self.final_valuations.loc[i, "asset_class"]}', '{self.final_valuations.loc[i, "product_type"]}', '{self.final_valuations.loc[i, "contract_number"]}', '{self.final_valuations.loc[i, "trade_number"]}', '{self.final_valuations.loc[i, "valuation"]}', '{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')"""
        #     print(query)
        #     connection.execute(text(query))
        #     print("Executed")
        print(self.final_output)
        return self.final_output

    # def compute_portfolio_sensitvities(self):
    #     sensitivity_shocks = data_handling.read_data_func("sensitivity_shocks", "*", [])
    #     sensitivity_shocks = pd.DataFrame.from_records(
    #         sensitivity_shocks["data"], columns=sensitivity_shocks["columns"]
    #     )
    #     # Creating Shocked MDCs
    #     mdc_dict = {}
    #     for asset_class in sensitivity_shocks["asset_class"].unique():
    #         mdc_dict[asset_class] = dict()
    #     for i in range(len(sensitivity_shocks)):
    #         asset_class = sensitivity_shocks.loc[i, "asset_class"]
    #         risk_factor = sensitivity_shocks.loc[i, "risk_factor"]
    #         shock_value = sensitivity_shocks.loc[i, "shock_value"]
    #         shock_type = sensitivity_shocks.loc[i, "shock_type"]
    #         shock_unit = sensitivity_shocks.loc[i, "shock_unit"]
    #         if asset_class == "FX Options":
    #             if risk_factor == "Spot Delta":
    #                 for scenario in ["Spot Up", "Spot Down"]:
    #                     sys.stdout = open(os.devnull, "w")
    #                     shocked_mdc = marketData.MarketData(self.date)
    #                     shocked_mdc.createAll()  # No need to create all.
    #                     sys.stdout = sys.__stdout__
    #                     if scenario == "Spot Down":
    #                         shock_value = -1 * shock_value
    #                     for curr in shocked_mdc.spotList:
    #                         shocked_mdc.create_shock(
    #                             "FX Spot",
    #                             curr,
    #                             shock_value,
    #                             shock_unit,
    #                             shock_type,
    #                         )
    #                     mdc_dict[asset_class][scenario] = shocked_mdc

    #             elif risk_factor == "Spot Gamma":
    #                 for scenario in ["Spot Up Up", "Spot Down Down", "Spot Up Down"]:
    #                     shocked_mdc = marketData.MarketData(self.date)
    #                     shocked_mdc.createAll()
    #                     for curr in shocked_mdc.spotList:
    #                         if scenario == "Spot Up Up":
    #                             shocked_mdc.create_shock(
    #                                 "FX Spot",
    #                                 curr,
    #                                 shock_value,
    #                                 shock_unit,
    #                                 shock_type,
    #                             )
    #                             shocked_mdc.create_shock(
    #                                 "FX Spot",
    #                                 curr,
    #                                 shock_value,
    #                                 shock_unit,
    #                                 shock_type,
    #                             )
    #                         elif scenario == "Spot Down Down":
    #                             shocked_mdc.create_shock(
    #                                 "FX Spot",
    #                                 curr,
    #                                 -1 * shock_value,
    #                                 shock_unit,
    #                                 shock_type,
    #                             )
    #                             shocked_mdc.create_shock(
    #                                 "FX Spot",
    #                                 curr,
    #                                 -1 * shock_value,
    #                                 shock_unit,
    #                                 shock_type,
    #                             )
    #                         elif scenario == "Spot Up Down":
    #                             shocked_mdc.create_shock(
    #                                 "FX Spot",
    #                                 curr,
    #                                 shock_value,
    #                                 shock_unit,
    #                                 shock_type,
    #                             )
    #                             shocked_mdc.create_shock(
    #                                 "FX Spot",
    #                                 curr,
    #                                 -1 * shock_value,
    #                                 shock_unit,
    #                                 shock_type,
    #                             )
    #                     mdc_dict[asset_class][scenario] = shocked_mdc

    #             elif risk_factor == "Volatility":
    #                 for scenario in ["Vol Up", "Vol Down"]:
    #                     shocked_mdc = marketData.MarketData(self.date)
    #                     shocked_mdc.createAll()
    #                     if scenario == "Vol Down":
    #                         shock_value = -1 * shock_value
    #                     for vol_surface in shocked_mdc.volList:
    #                         shocked_mdc.create_shock(
    #                             "FX Volatilities",
    #                             vol_surface,
    #                             shock_value,
    #                             shock_unit,
    #                             shock_type,
    #                         )
    #                     mdc_dict[asset_class][scenario] = shocked_mdc

    #     # Looping over portfolio to get sensitivities
    #     for i in range(len(self.deals)):
    #         asset_class_deal = self.deals.loc[i, "asset_class"]
    #         product_type = self.deals.loc[i, "product_type"]
    #         contract_number = self.deals.loc[i, "contract_number"]
    #         trade_number = self.deals.loc[i, "trade_number"]
    #         trade_details = json.loads(self.deals.loc[i, "trade_details"])
    #         # Pass in new asset classes and product types here
    #         # Ensure to include instrument, for eg: USDINR is a forex instrument.
    #         if asset_class_deal == "Forex":
    #             if product_type == "Options":
    #                 option = fxOptionPricer.fxOption(
    #                     trade_details, contract_number, trade_number, self.curve_mapper_option
    #                 )
    #                 option.value_with(self.mdc)
    #                 theoretical_greeks = option.compute_sensitivities()

    #                 delta = (
    #                     option.value_with(mdc_dict["FX Options"]["Spot Up"])
    #                     - option.value_with(mdc_dict["FX Options"]["Spot Down"])
    #                 ) / (
    #                     mdc_dict["FX Options"]["Spot Up"].fetch("FX Spot", option.curr_pair).rate
    #                     - mdc_dict["FX Options"]["Spot Down"].fetch("FX Spot", option.curr_pair).rate
    #                 )

    #                 delta_up = (
    #                     option.value_with(mdc_dict["FX Options"]["Spot Up Up"])
    #                     - option.value_with(mdc_dict["FX Options"]["Spot Up Down"])
    #                 ) / (
    #                     mdc_dict["FX Options"]["Spot Up Up"].fetch("FX Spot", option.curr_pair).rate
    #                     - mdc_dict["FX Options"]["Spot Up Down"].fetch("FX Spot", option.curr_pair).rate
    #                 )

    #                 delta_down = (
    #                     option.value_with(mdc_dict["FX Options"]["Spot Up Down"])
    #                     - option.value_with(mdc_dict["FX Options"]["Spot Down Down"])
    #                 ) / (
    #                     mdc_dict["FX Options"]["Spot Up Down"].fetch("FX Spot", option.curr_pair).rate
    #                     - mdc_dict["FX Options"]["Spot Down Down"].fetch("FX Spot", option.curr_pair).rate
    #                 )

    #                 gamma = (delta_up - delta_down) / (
    #                     mdc_dict["FX Options"]["Spot Up"].fetch("FX Spot", option.curr_pair).rate
    #                     - mdc_dict["FX Options"]["Spot Down"].fetch("FX Spot", option.curr_pair).rate
    #                 )

    #                 vol_shock = sensitivity_shocks.loc[
    #                     (sensitivity_shocks["asset_class"] == "FX Options")
    #                     & (sensitivity_shocks["risk_factor"] == "Volatility"),
    #                     "shock_value",
    #                 ].values[0]
    #                 vega = (
    #                     option.value_with(mdc_dict["FX Options"]["Vol Up"])
    #                     - option.value_with(mdc_dict["FX Options"]["Vol Down"])
    #                 ) / (2 * vol_shock)

    #                 ir_shock = sensitivity_shocks.loc[
    #                     (sensitivity_shocks["asset_class"] == "FX Options")
    #                     & (sensitivity_shocks["risk_factor"] == "Interest Rate"),
    #                     "shock_value",
    #                 ].values[0]
    #                 rho = (
    #                     option.value_with(self.mdc, shock_rd=True, shock_value=ir_shock)
    #                     - option.value_with(self.mdc, shock_rd=True, shock_value=-1 * ir_shock)
    #                 ) / (2 * ir_shock)

    #                 phi = (
    #                     option.value_with(self.mdc, shock_rf=True, shock_value=ir_shock)
    #                     - option.value_with(self.mdc, shock_rf=True, shock_value=-1 * ir_shock)
    #                 ) / (2 * ir_shock)

    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = option.curr_pair
    #                 self.sensitivities.loc[i, "contract_number"] = option.cnt_nb
    #                 self.sensitivities.loc[i, "trade_number"] = option.trade_no
    #                 self.sensitivities.loc[i, "numerical_delta"] = delta
    #                 self.sensitivities.loc[i, "numerical_gamma"] = gamma
    #                 self.sensitivities.loc[i, "numerical_vega"] = vega
    #                 self.sensitivities.loc[i, "numerical_rho"] = rho
    #                 self.sensitivities.loc[i, "numerical_phi"] = phi
    #                 self.sensitivities.loc[i, "theoretical_delta"] = theoretical_greeks["delta"]
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = theoretical_greeks["gamma"]
    #                 self.sensitivities.loc[i, "theoretical_vega"] = theoretical_greeks["vega"]
    #                 self.sensitivities.loc[i, "theoretical_rho"] = theoretical_greeks["rho"]
    #                 self.sensitivities.loc[i, "theoretical_phi"] = theoretical_greeks["phi"]
    #                 self.sensitivities.loc[i, "pv01"] = 0
    #                 self.sensitivities.loc[i, "duration"] = 0
    #                 self.sensitivities.loc[i, "convexity"] = 0
    #                 self.sensitivities.loc[i, "risk_factors"] = json.dumps(theoretical_greeks["risk_factors"])

    #             elif product_type == "FX Swaps":
    #                 deal = FXswapPricer.FxSwap(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities["PV01"]
    #                 self.sensitivities.loc[i, "duration"] = 0
    #                 self.sensitivities.loc[i, "convexity"] = 0

    #             elif product_type == "NDF":
    #                 deal = NDFPricer.NDFPricer(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 # print(sensitivities)
    #                 # print(sensitivities["PV01"])
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities.loc[0, "PV01"]
    #                 self.sensitivities.loc[i, "duration"] = 0
    #                 self.sensitivities.loc[i, "convexity"] = 0

    #             elif product_type == "Currency Futures":
    #                 deal = CurrencyFuturesPricer.CurrencyFuture(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities["PV01"]
    #                 self.sensitivities.loc[i, "duration"] = 0
    #                 self.sensitivities.loc[i, "convexity"] = 0

    #             elif product_type == "Currency Forwards":
    #                 deal = CurrencyForwardsPricer.CurrencyForwardPricer(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities["PV01"]
    #                 self.sensitivities.loc[i, "duration"] = 0
    #                 self.sensitivities.loc[i, "convexity"] = 0

    #         elif asset_class_deal == "Interest Rate":
    #             if product_type == "IRS" or product_type == "CCS":
    #                 deal = 0
    #                 sensitivities = 0
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = 0
    #                 self.sensitivities.loc[i, "contract_number"] = 0
    #                 self.sensitivities.loc[i, "trade_number"] = 0
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = 0
    #                 self.sensitivities.loc[i, "duration"] = 0
    #                 self.sensitivities.loc[i, "convexity"] = 0
    #                 self.sensitivities.loc[i, "risk_factors"] = 0
    #                 # sensitivities = deal.compute_sensitivities(self.mdc)
    #                 # self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 # self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 # self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 # self.sensitivities.loc[i, "product_type"] = product_type
    #                 # self.sensitivities.loc[i, "instrument"] = deal.trade_details["Type"]
    #                 # self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 # self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 # self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 # self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 # self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 # self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 # self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 # self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 # self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 # self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 # self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 # self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 # self.sensitivities.loc[i, "pv01"] = sensitivities["total_pv01"]
    #                 # self.sensitivities.loc[i, "duration"] = 0
    #                 # self.sensitivities.loc[i, "convexity"] = 0
    #                 # self.sensitivities.loc[i, "risk_factors"] = json.dumps(sensitivities["risk_factors"])

    #         elif asset_class_deal == "Fixed Income":
    #             if product_type == "GSEC":
    #                 deal = gSecPricer.GSecPricer(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = 0
    #                 self.sensitivities.loc[i, "duration"] = 0
    #                 self.sensitivities.loc[i, "convexity"] = 0

    #             elif product_type == "Debenture":
    #                 deal = CorporateBondPricer.CorporateBond(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities["PV01"]
    #                 self.sensitivities.loc[i, "duration"] = sensitivities["Modified Duration"]
    #                 self.sensitivities.loc[i, "convexity"] = sensitivities["Convexity"]

    #             elif product_type == "Commercial Paper":
    #                 deal = CommercialPaperPricer.CommercialPaper(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities["PV01"]
    #                 self.sensitivities.loc[i, "duration"] = sensitivities["Modified Duration"]
    #                 self.sensitivities.loc[i, "convexity"] = sensitivities["Convexity"]

    #             elif product_type == "CD":
    #                 deal = CDPricer.CD(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities["PV01"]
    #                 self.sensitivities.loc[i, "duration"] = sensitivities["Modified Duration"]
    #                 self.sensitivities.loc[i, "convexity"] = sensitivities["Convexity"]

    #             elif product_type == "FCB":
    #                 deal = BondwithForeignCurrencyPricer.ForeignBondPricer(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities["PV01"]
    #                 self.sensitivities.loc[i, "duration"] = sensitivities["Modified Duration"]
    #                 self.sensitivities.loc[i, "convexity"] = sensitivities["Convexity"]

    #             elif product_type == "Bond with Option":
    #                 deal = BondwithOptionPricer.BondWithOption(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities["PV01"]
    #                 self.sensitivities.loc[i, "duration"] = sensitivities["Modified Duration"]
    #                 self.sensitivities.loc[i, "convexity"] = sensitivities["Convexity"]

    #             elif product_type == "Perpetual Bond":
    #                 deal = PerpetualBondPricer.PerpetualBond(trade_details, contract_number, trade_number)
    #                 sensitivities = deal.compute_sensitivities(self.mdc)
    #                 self.sensitivities.loc[i, "date"] = dateConversion.date_convert(self.date).convert_date("string")
    #                 self.sensitivities.loc[i, "portfolio"] = self.portfolio_name
    #                 self.sensitivities.loc[i, "asset_class"] = asset_class_deal
    #                 self.sensitivities.loc[i, "product_type"] = product_type
    #                 self.sensitivities.loc[i, "instrument"] = deal.trade_details["product_type"]
    #                 self.sensitivities.loc[i, "contract_number"] = deal.contract_number
    #                 self.sensitivities.loc[i, "trade_number"] = deal.trade_number
    #                 self.sensitivities.loc[i, "numerical_delta"] = 0
    #                 self.sensitivities.loc[i, "numerical_gamma"] = 0
    #                 self.sensitivities.loc[i, "numerical_vega"] = 0
    #                 self.sensitivities.loc[i, "numerical_rho"] = 0
    #                 self.sensitivities.loc[i, "numerical_phi"] = 0
    #                 self.sensitivities.loc[i, "theoretical_delta"] = 0
    #                 self.sensitivities.loc[i, "theoretical_gamma"] = 0
    #                 self.sensitivities.loc[i, "theoretical_vega"] = 0
    #                 self.sensitivities.loc[i, "theoretical_rho"] = 0
    #                 self.sensitivities.loc[i, "theoretical_phi"] = 0
    #                 self.sensitivities.loc[i, "pv01"] = sensitivities["PV01"]
    #                 self.sensitivities.loc[i, "duration"] = sensitivities["Modified Duration"]
    #                 self.sensitivities.loc[i, "convexity"] = sensitivities["Convexity"]
    #             # Insert forex products from here
    #         # Insert new asset classes from here
    #     print(self.sensitivities)
    #     print("Starting write of data")
    #     data_handling.write_data_func("portfolio_sensitivities", self.sensitivities)
    #     return self.sensitivities


# client.close()
