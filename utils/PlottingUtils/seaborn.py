# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 10:20:25 2022

@author: adimehta
"""

curve = m.fetch('IR','EUR Basis')
curve = curve.Data[['Tenor','Value']]

import seaborn as sns
sns.set_theme(style="dark")
sns.lineplot(data=curve, x="Tenor", y="Value")
