import pandas as pd
from functools import reduce
import numpy as np
import os


class NoopReport:
    def __init__(
        self,
        income_expense,
        income_int,
        expense_int,
        currency_control,
        not_accounted,
        mlc,
        overdue_bills,
        overdue_fwds,
        lcbg,
        mid_rates,
    ):
        self.income_expense = income_expense
        self.income_int = income_int
        self.expense_int = expense_int
        self.currency_control = currency_control
        self.not_accounted = not_accounted
        self.mlc = mlc
        self.overdue_bills = overdue_bills
        self.overdue_fwds = overdue_fwds
        self.lcbg = lcbg
        self.mid_rates = mid_rates

    def income_expense_calc(self):
        income_expenses = (
            self.income_expense.groupby(["CURRENCY", "CGL_TYPE"]).sum().reset_index()
        )

        self.income = income_expenses[income_expenses["CGL_TYPE"] == "INCOME"]
        self.expenses = income_expenses[income_expenses["CGL_TYPE"] == "EXPENSES"]

        self.income = self.income[["CURRENCY", "CGL_TYPE", "AMOUNT"]].merge(
            self.income_int[["CURRENCY", "ACCRUED_INTT"]], on="CURRENCY", how="outer"
        )
        self.income.fillna(0, inplace=True)
        self.income["Income Amount"] = (
            self.income["AMOUNT"] - self.income["ACCRUED_INTT"]
        )
        self.income.drop(["ACCRUED_INTT", "AMOUNT", "CGL_TYPE"], axis=1, inplace=True)
        self.income.rename({"CURRENCY": "Currency"}, axis=1, inplace=True)

        self.expenses = self.expenses[["CURRENCY", "CGL_TYPE", "AMOUNT"]].merge(
            self.expense_int[["CURRENCY", "ACCRUED_INTT"]], on="CURRENCY", how="outer"
        )
        self.expenses.fillna(0, inplace=True)
        self.expenses["Expense Amount"] = (
            self.expenses["AMOUNT"] - self.expenses["ACCRUED_INTT"]
        )
        self.expenses.drop(["ACCRUED_INTT", "AMOUNT", "CGL_TYPE"], axis=1, inplace=True)
        self.expenses.rename({"CURRENCY": "Currency"}, axis=1, inplace=True)

        return self.income, self.expenses

    def currency_control_calc(self):
        self.currency_control = self.currency_control[
            self.currency_control["BGL_TYPE"] == "CURR_CONTROL"
        ]
        self.currency_control = (
            self.currency_control.groupby("CURRENCY")
            .sum()["AMOUNT"]
            .reset_index()
            .rename({"CURRENCY": "Currency", "AMOUNT": "Currency Control"}, axis=1)
        )

        return self.currency_control

    def not_accounted_data_calc(self):
        self.not_accounted = (
            self.not_accounted.groupby(["EXP_CURR"])
            .sum()["EXP_AMOUNT"]
            .reset_index()
            .rename(
                {"EXP_CURR": "Currency", "EXP_AMOUNT": "Not Accounted Data"}, axis=1
            )
        )

        return self.not_accounted

    def net_spot_calc(self):
        self.post_eod = pd.DataFrame(columns=["Currency", "Post EOD Amount"])
        dfs = [
            self.currency_control,
            self.income,
            self.expenses,
            self.not_accounted,
            self.post_eod,
        ]
        self.net_spot = reduce(
            lambda left, right: pd.merge(left, right, on="Currency", how="outer"), dfs
        ).fillna(0)
        self.net_spot["Net Spot Amount"] = self.net_spot.sum(axis=1)

    def mlc_calc(self):
        self.mlc = self.mlc[self.mlc["INTERNAL_FLAG"] == "N"]
        self.borrowing = self.mlc
        self.mlc = (
            self.mlc.groupby("M_KEY")
            .sum()["CONTR_AMT"]
            .reset_index()
            .rename(
                {"M_KEY": "Currency", "CONTR_AMT": "Off B/S Positon in MLC"}, axis=1
            )
        )
        return self.mlc

    def borrowing_placement_calc(self):
        self.borrowing = (
            self.borrowing[self.borrowing["M_B_MXPRODUC"].isin(["Deposit", "Loan"])]
            .groupby("M_KEY")
            .sum()["CONTR_AMT"]
            .reset_index()
            .rename(
                {"M_KEY": "Currency", "CONTR_AMT": "Placement Borrowing Amount"}, axis=1
            )
        )

    def overdure_bills_calc(self):
        self.overdue_bills = (
            self.overdue_bills.groupby("CURRENCY1")
            .sum()["FCAMT1"]
            .reset_index()
            .rename({"CURRENCY1": "Currency", "FCAMT1": "Overdue Bills"}, axis=1)
        )

        return self.overdue_bills

    def overdue_fwds_calc(self):
        self.overdue_fwds = (
            self.overdue_fwds.groupby("EXP_CURR")
            .sum()["EXP_AMT"]
            .reset_index()
            .rename({"EXP_CURR": "Currency", "EXP_AMT": "Overdue Forwards"}, axis=1)
        )

        return self.overdue_fwds

    def lcbg_calc(self):
        self.lcbg = self.lcbg[self.lcbg["RECORD_STATUS"] == "AUTHORISED"]
        self.lcbg = self.lcbg.sort_values(by="EFFECTIVE_DATE").drop_duplicates(
            subset=["CURRENCY"], keep="last"
        )
        self.lcbg = self.lcbg.drop(
            ["EFFECTIVE_DATE", "RECORD_STATUS"], axis=1
        ).reset_index(drop=True)
        self.lcbg.rename(
            {"CURRENCY": "Currency", "AMOUNT": "LC/BG Amount"}, axis=1, inplace=True
        )
        return self.lcbg

    def overdue_bills_fwds_lcbg_calc(self):
        dfs = [self.overdue_bills, self.overdue_fwds, self.lcbg]
        print(dfs)
        self.overdue_bills_fwds_lcbg = reduce(
            lambda left, right: pd.merge(left, right, on="Currency", how="outer"), dfs
        ).fillna(0)
        self.overdue_bills_fwds_lcbg[
            "Overdue Bills/Fwds and Invoked LC/BG"
        ] = self.overdue_bills_fwds_lcbg.sum(axis=1)
        return self.overdue_bills_fwds_lcbg

    def collate_tables_calc(self):
        dfs = [self.net_spot, self.mlc, self.borrowing, self.overdue_bills_fwds_lcbg]
        self.final_report_table = reduce(
            lambda left, right: pd.merge(left, right, on="Currency", how="outer"), dfs
        ).fillna(0)
        return self.final_report_table

    def final_calcs(self):
        self.final_report_table["Net Forward Amonut"] = (
            self.final_report_table["Off B/S Positon in MLC"]
            - self.final_report_table["Placement Borrowing Amount"]
            + self.final_report_table["Overdue Bills/Fwds and Invoked LC/BG"]
        )
        self.final_report_table["NOOP FC"] = (
            self.final_report_table["Net Spot Amount"]
            + self.final_report_table["Net Forward Amonut"]
        )
        self.final_report_table = self.final_report_table.merge(
            self.mid_rates, on="Currency"
        )
        self.final_report_table["NOOP INR"] = self.final_report_table["NOOP FC"] * (
            self.final_report_table["Mid Rate"] / 10
        )
        numeric_cols = [
            "Currency Control",
            "Income Amount",
            "Expense Amount",
            "Not Accounted Data",
            "Post EOD Amount",
            "Net Spot Amount",
            "Off B/S Positon in MLC",
            "Placement Borrowing Amount",
            "Overdue Bills",
            "Overdue Forwards",
            "LC/BG Amount",
            "Overdue Bills/Fwds and Invoked LC/BG",
            "Net Forward Amonut",
            "NOOP FC",
            "NOOP INR",
        ]
        for i in range(len(self.final_report_table)):
            if self.final_report_table.loc[i, "Currency"] == "INR":
                self.final_report_table.loc[i, numeric_cols] = (
                    self.final_report_table.loc[i, numeric_cols] / 10000000
                )
            else:
                self.final_report_table.loc[i, numeric_cols] = (
                    self.final_report_table.loc[i, numeric_cols] / 1000000
                )
        self.final_report_table[numeric_cols] = self.final_report_table[
            numeric_cols
        ].round(2)
        return self.final_report_table

    def calculate_report(self):
        self.income_expense_calc()
        self.currency_control_calc()
        self.not_accounted_data_calc()
        self.net_spot_calc()
        self.mlc_calc()
        self.borrowing_placement_calc()
        self.overdure_bills_calc()
        self.overdue_fwds_calc()
        self.lcbg_calc()
        self.overdue_bills_fwds_lcbg_calc()
        self.collate_tables_calc()
        final = self.final_calcs()

        return final
