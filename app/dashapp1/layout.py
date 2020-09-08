import os
import io
import requests
import pandas as pd
import numpy as np
from dateutil.parser import parse
import plotly.graph_objects as go

import datetime
import calendar

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input


'''
   ------------------------------------------------------------------------------------------- 
                                            CONFIG
   ------------------------------------------------------------------------------------------- 
'''
# ## TODO: GET RESOLUTION OF THE WEB BROWSER

## PLOTLY
import plotly.io as pio
pio.templates.default = "plotly_white"

## DASH
config_dash = {'displayModeBar': False, 'showAxisDragHandles':False}  
margin = dict(l=20, r=20, t=10, b=10)
# External CSS + Dash Bootstrap components
external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/main.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

## USE THE FRENCH DATE - not working with heroku
import locale
locale.setlocale(locale.LC_TIME, "fr_FR")

## COLOR & OPACITY
blue = '#3980b7'
green = '#55a630'
red ='#e71d36'  
grey = '#6c757d'
target_opacity = 0.7

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



'''
   ------------------------------------------------------------------------------------------- 
                                            LOAD THE DATA
   ------------------------------------------------------------------------------------------- 

'''
basedir = os.path.abspath(os.path.dirname(__file__))
#fetching data on github repo


url_sales = "https://raw.githubusercontent.com/Stephanefy/dash-in-flask/master/app/static/data1/sales_summary.csv"
sales_data= requests.get(url_sales).content



sales = pd.read_csv(io.StringIO(sales_data.decode('utf-8')), parse_dates=[0])
dashboard_date = datetime.date(2019, 5, 23)


'''------------------------------------------------------------------------------------------- 
                                        DASH COMPONENTS
   ------------------------------------------------------------------------------------------- 
'''

## 1. CREATION DU HEADER
# --------------------------------------------------------

metric_dropdown = dcc.Dropdown(
    id='metric_dropwdown',
    options=[
        {'label': "Chiffre d'affaire", 'value': 'sales_2020'},
        {'label': "Bénéfices", 'value': 'profit_2020'},
    ],
    value='sales_2020',
    searchable=False,
    clearable=False,
    style={"border": "none"}
)

months = sales['Date'].dt.month.unique()
month_option = [{'label':calendar.month_abbr[m], 'value':m}for m in range(1,dashboard_date.month+1)]
# month_option.append({'label':None, 'value':"Année"}) # TODO: ajouter une option "Année"
date_dropdown = dcc.Dropdown(
    id='date_dropwdown',
    options=month_option,
    value=dashboard_date.month,
    searchable=False,
    clearable=False,
    style={"border": "none"}
)

header = dbc.Card([
    dbc.Row(html.H1("Centre de Commande"), className='ml-2 mt-1'),
    html.Hr(className="mt-1 mb-0"),
    dbc.Row(
        [
            dbc.Col(metric_dropdown, className="ml-2", lg=2, xs=4),
            dbc.Col(date_dropdown, lg=2, xs=4)
        ],
        justify="start",
        className="mt-2 mb-2"
    )
])

# 2. Colonne de Gauche
# --------------------------------------------------------

progress_bar = dcc.Graph(id='progress_pie', className="progress_pie", config=config_dash, style={'height':'28vh'})
summary = dcc.Graph(id='card_sum', className="card_sum" ,config=config_dash, style={'height':'28vh'})
monthly_sales = dcc.Graph(id='monthly_sales', config=config_dash, style={'width':'100%','height':'45vh'}, className="border")

left_block = dbc.Col(
        dbc.Container(
            children=[
            dbc.Row(
            children = [
                dbc.Col(progress_bar, className="border progress_bar mr-3 mt-3 ", style={"background-color": "white"},sm=12,md=6), 
                dbc.Col(summary, className="border summary mt-3", style={"background-color": "white"}),
                
            ],className="left-block--indicators"),
            dbc.Row(monthly_sales, style={"height": "58%"}, className="monthly_sales mt-3 ")
            ],fluid=True, className="p-0 m-0 h-100"),
    lg=8,
    xs=12,
    className="mr-3 mb-3",
    )

#  3. Colonne de droite
# --------------------------------------------------------
city_sales = dcc.Graph(
    id='city_sales', 
    config=config_dash, 
    style={'height':'100%', 'width':'100%'}
)

right_block = dbc.Col(
    city_sales, 
    style={"background-color": "white"}, 
    className=" mt-3 mb-3 border",
)
    
                


'''------------------------------------------------------------------------------------------- 
                                            LAYOUT
   ------------------------------------------------------------------------------------------- 
'''
layout = html.Div(
    [
    header,
    dbc.Container(
        [
        dbc.Row(
                [
                    left_block,
                    right_block
                ],
                className="mr-3 ml-3 p-0"
            )
        ],fluid=True, className="p-0 mb-3"),
    ],
    style={"height": "100%"}   
)