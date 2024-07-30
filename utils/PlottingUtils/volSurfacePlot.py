# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 15:19:48 2022

@author: adimehta
"""
import os

os.chdir(
    r"C:\Users\gduremanthi.ext\Deloitte (O365D)\RiskAdvisory-FinancialRisk - Documents\SBI MLC Review\RetailCube07062022"
)
from Utils.FXVolSurface_Class import *
import datetime as dt
from scipy import stats
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.animation as animation

%matplotlib qt
dataPath = os.getcwd() + r"\Data\FXVolSurfaceData.csv"
data = pd.read_csv(dataPath)

startDate = Date(3, 1, 2020)
endDate = Date(3, 2, 2020)
instrument = "USDINR_FXVol"


def generateVolPlot(startDate, endDate, data, instrument):
    data["Datetime"] = [dt.datetime.strptime(d, "%m/%d/%Y") for d in data["Date"]]
    data["QuantLib"] = [Date(d.day, d.month, d.year) for d in data["Datetime"]]

    df_ = data.loc[(data["QuantLib"] > startDate) & (data["QuantLib"] < endDate), :]
    df_ = df_.loc[df_.Instrument == instrument, :]

    out = []

    for date in np.unique(df_["QuantLib"]):
        print(date)
        data = df_.loc[df_["QuantLib"] == date, :]
        data = data[["Strike", "Tenor", "Value"]]
        data = pd.DataFrame(data.pivot(columns="Strike", index="Tenor"))
        data.columns = data.columns.droplevel(0)
        data.columns.name = None
        data = data.reset_index()
        data["Date"] = [date + int(x * 365) for x in data["Tenor"]]
        data = data.drop("Tenor", axis=1)
        cols = list(data.columns.values)
        cols = [cols[-1]] + cols[:-1]
        data = data[cols]

        configs = {
            "Spot Delta Last Tenor": None,
            "Interpolate Outright Variance": True,
            "Quotes are Delta with Premium": False,
            "ATM Zero Straddle Last Tenor": None,
            "Up Extrap 1.0 Delta": 1,
            "Down Extrap 1.0 Delta": 0,
            "Interpolator": "Interpolator3DSpline1D",
            "DayCount": 3,
        }

        surface = FXVolSurface(data, configs, date)
        deltaGrid = pd.DataFrame(
            columns=list(range(1, 100, 10)), index=surface.OffsetYears
        )
        for col in deltaGrid.columns:
            deltaGrid[col] = [
                surface.GetVolFromDelta(col, k) for k in surface.OffsetYears
            ]

        dfTS = surface.TermStructure
        deltaS = [1, 5.5, 10, 25, 50, 75, 90, 94.5, 99]
        tenorS = surface.OffsetYears
        delta_range = deltaS * len(tenorS)
        tenor_range = np.repeat(tenorS, len(deltaS))
        df = pd.DataFrame()
        df["Tenor"] = tenor_range
        df["Delta"] = delta_range
        df["Vol"] = dfTS.iloc[:, 1:].values.ravel()
        df["SurfaceDate"] = date
        out.append(df)

    out = pd.concat(out)

    def plotSurface(i):
        plt.cla()
        date = np.unique(out.SurfaceDate)[i]
        data = out.loc[
            out.SurfaceDate == date,
        ]
        data = data.iloc[:, :-1]
        deltaS = np.unique(data.Delta)
        tenors = np.unique(data.Tenor)
        X, Y = np.meshgrid(deltaS, tenors)
        data = data.pivot(index="Tenor", columns="Delta")[["Vol"]]
        data = data.values
        Z = data
        ax.set_zlim(0, 25)
        ax.set_ylim(0, 5)
        ax.grid(True, line_width=0.5, linestyle="--", color="black")
        ax.set_zlim(0, 25)
        ax.set_ylim(0, 5)
        ax.set_xlabel("Delta", color="white", fontfamily="verdana")
        ax.set_ylabel("Time to expiration", color="white")
        ax.set_zlabel("Volatility", color="white")
        # ax.xaxis.label.set_font_properties(fontS)

        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        ax.plot_surface(
            X,
            Y,
            Z,
            alpha=0.8,
            color="#bf4efc",
            rstride=1,
            cstride=1,
            lw=0.1,
            antialiased=True,
        )
        # show plot

    fig = plt.figure(figsize=(32, 32), facecolor="white")
    ax = plt.axes(projection="3d")
    # ax.grid(True,line_width=0.5,linestyle = '--', color='black')
    ax.set_title("Volatility Surface")
    ax.set_facecolor("black")
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_lw(0.1)
    ax.yaxis.pane.set_lw(0.1)
    ax.zaxis.pane.set_lw(0.1)
    ax.xaxis._axinfo["grid"].update({"linestyle": "--", "linewidth": 0.3})
    ax.yaxis._axinfo["grid"].update({"linestyle": "--", "linewidth": 0.3})
    ax.zaxis._axinfo["grid"].update({"linestyle": "--", "linewidth": 0.3})

    ax.xaxis.set_tick_params(colors="white")
    ax.yaxis.set_tick_params(colors="white")
    ax.zaxis.set_tick_params(colors="white")

    ani = animation.FuncAnimation(
        fig, plotSurface, len(np.unique(out.SurfaceDate)), repeat=False
    )

    return ani


volPlot = generateVolPlot(startDate, endDate, data, instrument)
plt.show()
plt.savefig(r'myAnimation.jpg')
