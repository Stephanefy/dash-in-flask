'''------------------------------------------------------------------------------------------- 
                                            INTERACT
   ------------------------------------------------------------------------------------------- 
'''
import os
import io
import requests

import pandas as pd
import numpy as np
from dateutil.parser import parse
import plotly.graph_objects as go
import math
import datetime
import calendar

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
from dash.dependencies import Output, Input, State

basedir = os.path.abspath(os.path.dirname(__file__))
#fetching data on github repo


url_sales = "https://raw.githubusercontent.com/Stephanefy/dash-in-flask/master/app/static/data1/sales_summary.csv"
sales_data= requests.get(url_sales).content



sales = pd.read_csv(io.StringIO(sales_data.decode('utf-8')), parse_dates=[0])
margin = dict(l=20, r=20, t=10, b=10)

## USEFUL FUNCTION
def millify(n):
    if n > 999:
        if n > 1e6-1:
            return f'{round(n/1e6,1)}M'
        return f'{round(n/1e3,1)}K'
    return n

def format_date(str_date, date_format):
    date = parse(str_date)
    return date.strftime(date_format) 

def red_or_green(df):
    return df.apply(lambda x: green if x >=1 else red)

dashboard_date = datetime.date(2019, 5, 23)

## COLOR & OPACITY
blue = '#3980b7'
green = '#55a630'
red ='#e71d36'  
grey = '#6c757d'
target_opacity = 0.7

def register_callbacks(dashapp):
    @dashapp.callback(
        [
            Output('progress_pie', 'figure'),
            Output('card_sum', 'figure'),
            Output('city_sales', 'figure'),
            Output('monthly_sales', 'figure')
        ],
        [
            Input('metric_dropwdown', 'value'),
            Input('date_dropwdown', 'value')
        ]
    )

    def global_update(metric, month):
        filtred_sales = sales.loc[sales['Date'].dt.month.isin([month])]
        target = 'sales_target' if metric == 'sales_2020' else 'profit_target'

        #  CREATION DES KPI
        # --------------------------------------------------------

        # Pie Progress
        amount = filtred_sales[metric].sum()
        progress = amount /  filtred_sales[target].sum()
        rest = 1 - progress if 1 - progress > 0 else 0
        progress_color = green if progress > 1 else red 
        values = [progress, rest]
        colors = [progress_color, 'white']
        progress_pie = go.Figure(
            go.Pie(
                values = values, 
                hole = .95, 
                marker_colors = colors
            )
        )
        progress_pie.update_layout(showlegend = False, hovermode = False )
        progress_pie.update_traces(textinfo='none')
        progress_pie.update_layout(
            margin = margin,
            annotations = [
                dict(
                    x=0.5,
                    y=0.40,
                    text="Objectif pour Mars",
                    showarrow=False,
                    font=dict(
                        color="#000000",
                        size=20,
                    )
                ),
                dict(
                    x=0.5,
                    y=0.60,
                    text='{}%'.format(int(progress*100)),
                    showarrow=False,
                    font=dict(
                        color=progress_color,
                        size=70
                    )
                )
            ]
        )

        # Summary card 
        target_goal = filtred_sales.loc[filtred_sales['Date'].dt.date <= dashboard_date, target].sum()
        score = amount / target_goal -1

        if score > 0:
            color = green
            text_score = '+ {}% ⬆︎'.format(int(score*100))
        else:
            color = red
            text_score = '{}% ⬇︎'.format(int(score*100))
        # create a white pie
        card_sum = go.Figure(go.Pie(values = [0,0]))
        # add annotation
        card_sum.update_layout(
            margin = margin,
            annotations = [
                dict(
                    x = 0.5,
                    y = 0.40,
                    text = "Chiffre d'Affaires ($)" if metric=="sales_2020" else "Bénéfices",
                    showarrow = False,
                    font = dict(
                        size = 25,
                        color = "#000000"
                    )
                ),
                dict(
                    x = 0.5,
                    y = 0.80,
                    text = '{}'.format(millify(amount)),
                    showarrow = False,
                    font = dict(
                        size = 70,
                        color = blue
                    )
                ),
                dict(
                    x = 0.5,
                    y = 0.20,
                    text = text_score,
                    showarrow = False,
                    # bgcolor=green,
                    font = dict(
                        size = 23,
                        color = color
                    )
                )
            ]
        )

        #  CITY SALES
        # --------------------------------------------------------
        city_sales = filtred_sales.groupby('City').sum()
        # percents = np.round((city_sales[metric] / city_sales[target]) * 100)
        # text = percents.apply(lambda x: f"{int(x)}%")
        percents = city_sales[metric] / city_sales[target] 
        # plot
        city_plot = go.Figure([
            go.Bar(
                name = 'Objectif', 
                y = city_sales.index, 
                x = city_sales[target], 
                marker_color=grey,
                marker_line_width=0.5,
                marker_line_color='black',
                opacity=target_opacity
            ),
            go.Bar(
                name = "Chiffre d'affaires" if metric=="sales_2020" else "Bénéfices", 
                y = city_sales.index, 
                x = city_sales[metric],
                text = percents,
                marker_color = red_or_green(percents),
                marker_line_width=0,
                width = 0.5,
            )
        ])
        # update
        city_plot.update_traces(texttemplate='%{text:.0%}',textposition='inside', selector=dict(marker_line_width=0))
        city_plot.update_traces(orientation='h', hovertemplate="%{x:.2s} $",)
        city_plot.update_layout(
            hovermode="y unified",
            barmode='overlay', 
            margin = margin, 
            showlegend=False)
        city_plot.update_xaxes(nticks=5)
        city_plot.update_yaxes(linewidth=0.5, linecolor='black', zeroline=True)

        #  MONTH SALES
        # --------------------------------------------------------
        daily_sales = sales.groupby('Date').sum()
        monthly_sales = daily_sales.resample('MS').sum()
        percents = monthly_sales[metric] / monthly_sales[target]
        # plot
        monthly_plot = go.Figure([
            go.Bar(
                name = 'Objectif', 
                x = monthly_sales.index, 
                y = monthly_sales[target], 
                marker_color=grey,
                marker_line_width=0.5,
                marker_line_color='black',
                opacity=target_opacity
            ),
            go.Bar(
                name = "Chiffre d'affaires" if metric=="sales_2020" else "Bénéfices", 
                x = monthly_sales.index, 
                y = monthly_sales[metric],
                text = percents,
                width = 0.6 *(1000*3600*24*22),
                marker_color = red_or_green(percents),
                marker_line_width=0,
            )
        ])
        monthly_plot.update_traces(texttemplate='%{text:.0%}', textposition='auto', selector=dict(marker_line_width=0))
        monthly_plot.update_traces(hovertemplate="%{y:.2s} $")
        monthly_plot.update_layout(
            hovermode="x unified",
            barmode='overlay', 
            showlegend=False,
            margin =margin)
        monthly_plot.update_xaxes(
            nticks=12, 
            linecolor='black', 
            zeroline=True,
            ticktext=[datetime.datetime.strftime(date, "%b") for date in monthly_sales.index],
            tickvals=monthly_sales.index)
        monthly_plot.update_yaxes(nticks=6)    

        # OUTPUT
        # --------------------------------------------------------
        output_tuple = (
            progress_pie,
            card_sum,
            city_plot,
            monthly_plot
        )
        return output_tuple