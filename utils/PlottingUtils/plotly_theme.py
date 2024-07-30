# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 14:53:27 2022

@author: adimehta
"""
from plotnine import *
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.tools import mpl_to_plotly as ggplotly
import plotly.io as pio

pio.renderers.default = "browser"

df = pd.read_csv(
    r"C:\Users\adimehta\Deloitte (O365D)\RiskAdvisory-FinancialRisk - SBI MLC Review\RetailCube07062022\VolData.csv"
)
df_ = df.loc[
    df.SurfaceDate == df.SurfaceDate[0],
]
df_ = df_.iloc[:, 1:]
del df

y = np.unique(df_.Delta)
x = np.unique(df_.Tenor)
X, Y = np.meshgrid(x, y)
Z = df_.pivot(index="Delta", columns="Tenor")["Vol"].values


bgColor = (0.3, 0, 29, 74)
surfaceColor = "rgb(72, 242, 29)"

colorscale = [[0, surfaceColor], [1, surfaceColor]]

fig = go.Figure(
    data=[
        
         go.Surface(
            x=X,
            y=Y,
            z=Z,
            opacity=1,
            showscale=False,
           # surfacecolor=np.zeros(Z.shape),
           colorscale='turbo'            
        )]
)

line_marker = dict(color='black', width=2)
for xx, yy, zz in zip(X, Y, Z):
    fig.add_scatter3d(x=xx, y=yy, z=zz, mode='lines', line=line_marker, name='')

Y2,X2 = np.meshgrid(y, x)
Z2 = df_.pivot(index="Tenor", columns="Delta")["Vol"].values
for yy, xx, zz in zip(Y2, X2, Z2):
    fig.add_scatter3d(x=xx, y=yy, z=zz, mode='lines', line=line_marker, name='')

scene = {
    "xaxis": {
        "backgroundcolor": "rgba" + str(bgColor),
        "gridcolor": "white",
        "color": "white",
        "showbackground": True,
        "gridwidth": 0.5,
        "title": "Tenor",
    },
    "yaxis": {
        "backgroundcolor": "rgba" + str(bgColor),
        "gridcolor": "white",
        "color": "white",
        "showbackground": True,
        "gridwidth": 0.5,
        "title": "Delta",
    },
    "zaxis": {
        "backgroundcolor": "rgba" + str(bgColor),
        "gridcolor": "white",
        "color": "white",
        "showbackground": True,
        "gridwidth": 0.5,
        "title": "Volatility",
    },
    "bgcolor": "rgba" + str(bgColor),
}


fig.update_layout(
    scene=scene,
    paper_bgcolor="rgba" + str(bgColor),
    margin=dict(l=20, r=20, t=20, b=20),
)

fig.show()


