# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 17:05:29 2022

@author: robhandari
"""

import pandas as pd
from plotly import graph_objects as go
df = pd.DataFrame({
    "a": ["a1", "a1", "a1", "a2", "a2", "a2", "a3", "a3", "a3"],
    "b": ["b1", "b2", "b3", "b1", "b2", "b3", "b1", "b2", "b3"],
    "c": [10, 20, 30, 40, 50, 60, 80, 90, 100],
    "d": [100, 200, 300, 400, 500, 600, 1000, 2000, 3000]
})

frames = df['a'].unique() # use to slice dataframe
figs = {} # container for figures
for i, f in enumerate(frames, start = 1):
    di = df[df['a']==f]
    fig = go.Figure()
    fig.add_bar(name = "ccc", x=di.b, y=di.c)
    fig.add_bar(name = "ddd", x=di.b, y=di.d)
    fig.update_layout(barmode='group', title="fig" + str(i) + " for a" + str(i))
    figs['fig'+str(i)] = fig
import plotly.io as pio
pio.renderers.default = "browser"
figs['fig1'].show()