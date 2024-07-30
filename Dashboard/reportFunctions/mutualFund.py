import pandas as pd
from functools import reduce

class mutualFund:
    def __init__(self, data, scrip_col, report_date, prices):
        # df is the transactions data
        # scrip_col is the name of the column that contains the names of the
        # securities.
        # prices is a df containing todays MF NAVs

        self.df = data
        self.scrip_col = scrip_col
        self.report_date = pd.to_datetime(report_date)
        self.prices = prices

    def qty_calc(self, data=None):
        self.df["Quantity"] = 0
        for i in range(len(self.df)):
            if self.df.loc[i, "B/S"] == "Sell":
                self.df.loc[i, "Quantity"] = -1 * self.df.loc[i, "QTY"]
            else:
                self.df.loc[i, "Quantity"] = self.df.loc[i, "QTY"]
        return self.df

    def bought_sold(self, data=None):
        scrip_col = self.scrip_col
        if not data:
            df = self.qty_calc()
        else:
            df = data
        for i in range(len(df)):
            if df.loc[i, "Quantity"] < 0:
                df.loc[i, "SoldQuantity"] = -1 * df.loc[i, "Quantity"]
                df.loc[i, "BoughtQuantity"] = 0
            elif df.loc[i, "Quantity"] >= 0:
                df.loc[i, "SoldQuantity"] = 0
                df.loc[i, "BoughtQuantity"] = df.loc[i, "Quantity"]
        final = df.groupby(scrip_col).sum()[
            ["Quantity", "BoughtQuantity", "SoldQuantity"]
        ]
        return final
    
    def map_portfolio(self):
        inter = self.df.groupby([self.scrip_col, "PORTFOLIO"]).sum().reset_index()[["DSP_LABEL", "PORTFOLIO"]]
        self.portfolio_mapper = inter
        return self.portfolio_mapper
        

    def calc_holding_cost(self, date=None):
        df = self.qty_calc()
        if not date:
            date = self.report_date
        df = df[df["Date"] <= date]
        scrip_col = self.scrip_col
        holding_price = {}
        for scrip in df[scrip_col].unique():
            # print(scrip)
            scrip_df = df[df[scrip_col] == scrip].reset_index(drop=True)
            scrip_df["CumQty"] = scrip_df["Quantity"].cumsum()
            scrip_df["HC"] = 0
            for i in range(len(scrip_df)):
                if scrip_df.loc[i, "B/S"] == "Buy":
                    if i == 0:
                        scrip_df.loc[i, "HC"] = scrip_df.loc[i, "PRICE"]
                    else:
                        if scrip_df.loc[i, "CumQty"] <= 0:
                            scrip_df.loc[i, "HC"] = 0
                        else:
                            scrip_df.loc[i, "HC"] = (
                                (
                                    scrip_df.loc[i - 1, "HC"]
                                    * scrip_df.loc[i - 1, "CumQty"]
                                )
                                + (
                                    scrip_df.loc[i, "Quantity"]
                                    * scrip_df.loc[i, "PRICE"]
                                )
                            ) / (scrip_df.loc[i, "CumQty"])
                else:
                    if i == 0:
                        scrip_df.loc[i, "HC"] = 0
                    else:
                        scrip_df.loc[i, "HC"] = scrip_df.loc[i - 1, "HC"]
            holding_price[scrip] = scrip_df.tail(1).reset_index().loc[0, "HC"]

        # holding_price = pd.Series(holding_price)
        # holding_price = holding_price.reset_index()
        # holding_price.columns = ["DSP_LABEL", "HC"]
        return pd.Series(holding_price).reset_index().rename({"index": mf.scrip_col, 0: "Holding Cost"}, axis=1)

    def trans_today(self):
        bs = self.qty_calc()
        todays_buy = bs[(bs["Date"] == self.report_date) & (bs["Quantity"]>=0)]
        todays_sell = bs[(bs["Date"] == self.report_date) & (bs["Quantity"]<0)]
        return todays_buy, todays_sell

    def benckmark_returns(self, benchmark_values: dict) -> dict:
        final = {}
        final["ccil_broad"] = (
            benchmark_values["ccil_broad"][0] / benchmark_values["ccil_broad"][1]
        ) - 1
        final["ccil_liquid"] = (
            benchmark_values["ccil_liquid"][0] / benchmark_values["ccil_liquid"][1]
        ) - 1
        final["nifty_200"] = (
            benchmark_values["nifty_200"][0] / benchmark_values["nifty_200"][1]
        ) - 1
        return final
    
    def overall_qty_calc(self):
        qty_dict_overall = {}
        for scrip in self.df[self.scrip_col].unique():
            scrip_df = self.df[
                (self.df[self.scrip_col] == scrip)
            ].reset_index(drop=True)
            scrip_df["CumQty"] = scrip_df["Quantity"].cumsum()
            qty_dict_overall[scrip] = scrip_df["CumQty"].iloc[-1]
        print(qty_dict_overall)
        final_qty = (
            pd.Series(qty_dict_overall, name="Final Quantity")
            .reset_index()
        )
        final_qty.rename({"index": self.scrip_col}, axis=1, inplace=True)
        final_qty = final_qty.loc[(final_qty != 0).any(axis=1)]
        
        return final_qty[final_qty["Final Quantity"] >= 1].reset_index(drop=True)
        
        
    def mtm_calc(self, previous_day=False):
        qty_dict = {}
        
        if previous_day:
            date = self.report_date - pd.offsets.Day(1)
        else:
            date = self.report_date

        for scrip in self.df[self.scrip_col].unique():
            scrip_df = self.df[
                (self.df[self.df["Date"] == date]) & (self.df[self.scrip_col] == scrip)
            ].reset_index(drop=True)
            scrip_df["CumQty"] = scrip_df["Quantity"].cumsum()
            qty_dict[scrip] = scrip_df["CumQty"].iloc[-1]
        final_qty = (
            pd.Series(qty_dict, name="Final Quantity")
            .reset_index()
            .remname({"index": self.scrip_col}, axis=1)
        )
        final_qty = final_qty.loc[(final_qty != 0).any(axis=1)]
        final = final_qty.merge(self.prices, on=self.scrip_col).dropna()
        mtms = final["Final Quantity"] * final["Prices"]
        return mtms

    # def realised_pl(self):
    #     prev_date = self.report_date - pd.tseries.offsets.DateOffset(years=1)
    #     data = self.df[
    #         (self.df["Date"] > prev_date) & (self.df["Date"] <= self.df["Date"])
    #     ]
    #     data = self.bought_sold(data).reset_index(drop = True)
        
    #     data["Realised Profit"] = 0
    #     for i in range(len(data)):
    #         if data.loc[i, "SoldQuantity"] == 0:
    #             data.loc['Realised Profit'] = 0
    #         else:
    #             holding_df = self.calc_holding_cost(date = data.loc[i, "Date"])
    #             pl_realised = (data["Price"] * data["QTY"])
    
if __name__ == "__main__":
    data = pd.read_excel(
        r"C:\Users\gduremanthi.ext\Deloitte (O365D)\RiskAdvisory-FinancialRisk - Documents\Domestic\SBI\SBI Veracity Check\Mutual Fund Report\DataFiles\MFFiltered.xlsx"
    )
    data = data[data["TRN.DATE"] <= pd.to_datetime("31-03-2022", dayfirst=True)]
    data = data[(data["TRN.STATUS"] == "LIVE") & (data["STP.STATUS"] == "Matched")]
    mutualfund = data.rename({"TRN.DATE":"Date"}, axis=1).reset_index()
    prices = pd.read_excel(r"C:\Users\gduremanthi.ext\Deloitte (O365D)\RiskAdvisory-FinancialRisk - Documents\Domestic\SBI\SBI Veracity Check\Mutual Fund Report\DVal\MFPrices1.xlsx")
    mf = mutualFund(mutualfund, "DSP_LABEL", pd.to_datetime('31-03-2022', dayfirst=True), prices)
    mf.qty_calc()
    prices = prices[[mf.scrip_col, 'Price', 'Price Prev Day','Price Last Year']]
    quantity = mf.overall_qty_calc()
    hc = mf.calc_holding_cost()
    portfolio_mapping = mf.map_portfolio()
    dfs = [quantity, hc, portfolio_mapping, prices]
    report_data = reduce(lambda x, y: pd.merge(x, y, on=mf.scrip_col), dfs)
    report_data["Unrealised Yearly Profit"]
    # ICICPLSPG :  296895451.61738837
