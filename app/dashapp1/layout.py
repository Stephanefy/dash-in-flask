import os

import pandas as pd
import numpy as np
from dateutil.parser import parse
import plotly.graph_objects as go
import plotly.express as px

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input


# config dash & plotly
import plotly.io as pio
pio.templates.default = "plotly_white"
config_dash = {'displayModeBar': False, 'showAxisDragHandles':False, 'responsive':True } #responsive=True
margin = dict(l=0, r=0, t=0, b=0)

# basedir = os.path.abspath(os.path.dirname(__file__))
# aboslute_path = basedir + '/data/df_covid19.csv'
url = "https://raw.githubusercontent.com/Stephanefy/dash-in-flask/master/app/dashapp1/data/df_covid19.csv"
# load data
df = pd.read_csv(url,sep=",")




print(df)

# create the counter
last_date = df['Date'].max()
confirmed_count = df[df['Date'] == last_date]['Confirmed'].sum()
death_count = df[df['Date'] == last_date]['Death'].sum()

# map markers' size
df['marker_Confirmed'] = df['Confirmed'].map(lambda x: x ** 0.4)
df['marker_Death'] = df['Death'].map(lambda x: x ** 0.4)
# create readable number
def millify(n):
    if n > 999:
        if n > 1e6-1:
            return f'{round(n/1e6,1)}M'
        return f'{round(n/1e3,1)}K'
    return n

def pretty_date(str_date, date_format):
    date = parse(str_date)
    return date.strftime(date_format) 


# mapbox token acess
with open('mapbox_token.txt') as f:
    lines = [x.rstrip() for x in f]
mapbox_access_token = lines[0]

# External CSS + Dash Bootstrap components
# external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/main.css"]

# DASH APP
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# filters component
filters = dbc.Card([
    html.Div([
        dcc.RangeSlider(
            id='date_slider',
            count=1,
            min=0,
            max=len(df['Date'].unique())-1,
            marks={i: pretty_date(date,'%B').title() for i, date in enumerate(df['Date'].unique()) if parse(date).day == 1},
            value=[0,len(df['Date'].unique())-1]), 
        dcc.Dropdown(
            id='country_dropdown',
            options=[{'label': country, 'value': country}
                     for country in df['State'].unique()],
            multi=True,
            value=None,
            placeholder='Réaliser une étude par pays',
            className='country-dropdown-el')
    ], style={'width': '100%', 'height': '100%', 'padding': '.9rem'})
], className='filter-card')

# layout and DASH components display

layout = html.Div(
    [
        dbc.Container(
            [
            # Headers
            dbc.Card(
                dbc.Row([html.Div(children=
                                [
                                dbc.Col(html.H1(id='my_title', className="title"), sm=12, md=8),
                                dbc.Col(html.H2(id='my_date', className='header-date'), sm=12, md=4)
                                ],className='header'
                            )
                    ],className='d-flex justify-content-between h-100 align-items-center'
                    ),className=' p-3 my-3 w-100 header-container'
                ),
            #Tabs & Filters
            dbc.Row([dbc.Col(dcc.Tabs(id="tabs", value='Confirmed', children=
                            [
                            dcc.Tab(id='tab_conf', label=f'{confirmed_count}', value='Confirmed', style={'color': 'rgb(21, 99, 255)'},
                            className='count-card confirmed-case', selected_className='count-selected count-selected-case'),
                            dcc.Tab(id='tab_death', label=f'{death_count}', value='Death', style={'color': 'rgb(237, 29, 48)'},
                            className='count-card confirmed-death', selected_className='count-selected count-selected-death')
                            ]
                                     ),
                            className='tabs',
                            ), 
                    dbc.Col(filters, lg=7, sm=12,)
                    ],
                    className='h-50 tabs-filter-container'
                ),
            #Figures
                dbc.Row([
                    dbc.Col(dcc.Graph(id='map_plot', className='map', config=config_dash), sm=9, lg=5, className="mx-auto"),
                    dbc.Col(html.Div([
                                dbc.Card([
                                    dbc.CardHeader(children='Nouveau cas', id='new_cases_title'),
                                    dbc.CardBody(dcc.Graph(id='new_cases', className='new', config=config_dash)),
                                ],className='graph-card new-case-card'),
                                dbc.Card([
                                    dbc.CardHeader(children='Nouveau cas', id='total_case_title'),
                                    dbc.CardBody(dcc.Graph(id='total_case_plot', className='new', config=config_dash)),
                                ],className='graph-card total-case-card'),
                                
                                ]),
                            sm=12, lg=7),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader('Pays les plus touchés'),
                        dbc.CardBody(dcc.Graph(id='top10', className='top-10-graph', config=config_dash))
                        ],className='graph-card top-10-card'),lg=12),
                ], id="graph-display"),
            ],
            fluid=True,
            className='main-container'),
            # Footer
            html.Footer(
            children=[html.P(children='©️2020 Agensit')], className='footer')
        ])

