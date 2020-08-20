
import pandas as pd
import numpy as np
from dateutil.parser import parse
import plotly.graph_objects as go
import plotly.express as px
import dash_html_components as html

from dash.dependencies import Input, Output

import plotly.io as pio
pio.templates.default = "plotly_white"
config_dash = {'displayModeBar': False, 'showAxisDragHandles':False, 'responsive':True } #responsive=True
margin = dict(l=0, r=0, t=0, b=0)

df = pd.read_csv(r'C:\Users\Dante\OneDrive\Bureau\projet-agensit-portail-analyse-master\app\dashapp1\data\df_covid19.csv')

df['marker_Confirmed'] = df['Confirmed'].map(lambda x: x ** 0.4)
df['marker_Death'] = df['Death'].map(lambda x: x ** 0.4)

with open('mapbox_token.txt') as f:
    lines = [x.rstrip() for x in f]
mapbox_access_token = lines[0]
def millify(n):
    if n > 999:
        if n > 1e6-1:
            return f'{round(n/1e6,1)}M'
        return f'{round(n/1e3,1)}K'
    return n

def pretty_date(str_date, date_format):
    date = parse(str_date)
    return date.strftime(date_format) 

def register_callbacks(dashapp):
    @dashapp.callback(
        [
            Output('my_title', 'children'),
            Output('my_date', 'children'),
            Output('tab_conf', 'label'),
            Output('tab_death', 'label'),
            Output('map_plot', 'figure'),
            Output('total_case_plot', 'figure'),
            Output('new_cases', 'figure'),
            Output('top10', 'figure'),
            Output('total_case_title', 'children'),
            Output('new_cases_title', 'children'),
        ],
        [
            Input('date_slider', 'value'),
            Input('tabs', 'value'),
            Input('country_dropdown', 'value'),
        ],
    )
    def global_update(slider_date, tabs_type, country_dropdown):
# 0. Design
    # date panel (top - right)
        min_date = pretty_date(df['Date'][slider_date[0]], '%d %B')
        max_date = pretty_date(df['Date'][slider_date[1]], '%d %B %Y')

        # color and french legend
        if tabs_type == 'Death':
            marker_color = 'rgb(237, 29, 48)'
            type_value = 'morts'
        else:
            marker_color = 'rgb(21, 99, 255)'
            type_value = 'cas'
        colorized_elm = html.Span(children='COVID-19', style={'color': marker_color})

    # 1. Preparation
        # global or detailed analysis ?
        if country_dropdown:
            df1 = df[df['State'].isin(country_dropdown)].reset_index(drop=True)
        else:
            df1 = df.copy()

        # filtred by date
        min_range_slider = df1[df1['Date'] == df1['Date'][slider_date[0]]].reset_index(drop=True)
        max_range_slider = df1[df1['Date'] == df1['Date'][slider_date[1]]].reset_index(drop=True)
        filtred_df = max_range_slider.copy()
        numeric_column = ['Confirmed', 'Death','marker_Confirmed', 'marker_Death']
        filtred_df[numeric_column] = max_range_slider[numeric_column] - min_range_slider[numeric_column] 
        filtred_df = filtred_df[filtred_df['Confirmed'] > 0]

        slice_df = df1[df1['Date'] <= df1['Date'][slider_date[1]]]
        slice_df = slice_df[slice_df['Date'] >= slice_df['Date'][slider_date[0]]].reset_index(drop=True)

        if country_dropdown:
            country_order = slice_df.groupby('State').sum().sort_values(by=tabs_type).index
        # create 'new_cases' and 'new_deaths'
        diff = slice_df.copy()
        diff['new_cases'] = diff['Confirmed'] - diff['Confirmed'].shift(1)
        diff['new_deaths'] = diff['Death'] - diff['Death'].shift(1)
        diff.dropna(inplace=True)
        # total count
        confirmed_count = filtred_df['Confirmed'].sum()
        death_count = filtred_df['Death'].sum()
        
    # 2. MAP
        if country_dropdown: 
            df_map = filtred_df[filtred_df['Death']>0].set_index('State')
            df_map = filtred_df.set_index('State')
            # plot
            map_plot = go.Figure()
            for c in country_order:
                map_plot.add_traces(go.Scattermapbox(
                    lat=[df_map.loc[c,'Lat']],
                    lon=[df_map.loc[c,'Long']],
                    text=[c],
                    customdata=np.dstack((df_map.loc[c,'Confirmed'],df_map.loc[c,'Death']))[0],
                    marker=dict(size=[df_map.loc[c,f'marker_{tabs_type}']], sizemin=3, sizeref=8),
                    hovertemplate='<b>%{text}</b><br><br>' + 
                        '%{customdata[0]:.3s} cas<br>' +
                        '%{customdata[1]:.3s} morts<extra></extra>'))
        else:
            if tabs_type == 'Death':
                df_map = filtred_df[filtred_df['Death']>0] 
            else:
                df_map = filtred_df.copy()
            # plot
            map_plot = go.Figure(go.Scattermapbox(
                lat=df_map['Lat'],
                lon=df_map['Long'],
                customdata=np.dstack((df_map['Confirmed'],df_map['Death']))[0], 
                text=df_map['State'],
                marker_color=marker_color,
                marker=dict(size=df_map[f'marker_{tabs_type}'],sizemin=2, sizeref=8),
                hovertemplate='<b>%{text}</b><br><br>' + 
                    '%{customdata[0]:.3s} cas<br>' +
                    '%{customdata[1]:.3s} morts<extra></extra>'))
        map_plot.update_layout(hoverlabel=dict(bgcolor="white", font_size=12), margin=margin,
                            mapbox={'zoom':0.4, 'accesstoken': mapbox_access_token}, showlegend=False)

    # 3. Top 10
        top10 = filtred_df.groupby(['State', 'Date']).sum().reset_index()
        if country_dropdown:
            top10 = top10.nlargest(len(country_dropdown), tabs_type)
            top10.sort_values(tabs_type, inplace=True)
            top10.set_index('State',inplace=True)
            # plot
            top10_plot = go.Figure()
            for c in top10.index.unique():
                top10_plot.add_traces(go.Bar(
                    x=[top10.loc[c,tabs_type]],
                    y=[c], 
                    customdata=np.dstack((top10.loc[c,'Confirmed'],top10.loc[c,'Death']))[0],
                    hovertemplate='%{customdata[0]:.3s} cas<br>' +
                    '%{customdata[1]:.3s} morts <extra></extra>'))
        else:
            top10 = top10.nlargest(5, tabs_type)
            top10.sort_values(tabs_type, inplace=True)
            # plot
            top10_plot = go.Figure(go.Bar(
                x=top10[tabs_type],
                y=top10['State'],
                customdata=np.dstack((top10['Confirmed'],top10['Death']))[0],
                hovertemplate='%{customdata[0]:.3s} cas<br>' +
                '%{customdata[1]:.3s} morts <extra></extra>',
                marker_color=marker_color))
        top10_plot.update_layout(showlegend=False, margin=margin)
        top10_plot.update_traces(textposition='outside', orientation='h')
        top10_plot.update_xaxes(showgrid=False, showticklabels=False)

    # 4. Cases over time
        if country_dropdown:
            global_increase = slice_df.groupby(['Date', 'State']).sum().reset_index(level='Date')
            total_case = go.Figure()
            for c in country_order:
                total_case.add_traces(go.Scatter(
                    x=global_increase.loc[[c],'Date'].map(lambda x: pretty_date(x,'%d %B %Y')),
                    y=global_increase.loc[[c], tabs_type],
                    name=c))
        else:
            global_increase = slice_df.groupby('Date').sum().reset_index()
            total_case = go.Figure(go.Scatter(
                x=global_increase['Date'].map(lambda x: pretty_date(x,'%d %B %Y')),
                y=global_increase[tabs_type],
                customdata=global_increase[tabs_type],
                hovertemplate='%{customdata:.3s} '+ f'{type_value}<extra></extra>',
                marker_color=marker_color))
        total_case.update_yaxes(showline=True)
        total_case.update_xaxes(showline=True, showgrid=False, showticklabels=False)
        total_case.update_layout( margin=margin, showlegend=False)

    # 5. New Cases Over time
        new_type = 'new_cases' if tabs_type == 'Confirmed' else 'new_deaths'
        if country_dropdown:
            global_diff = diff.groupby(['Date', 'State']).sum().reset_index(level='Date')
            # delete negative value
            global_diff.loc[global_diff['new_cases'] < 0,'new_cases'] = 0
            global_diff.loc[global_diff['new_deaths'] < 0,'new_deaths'] = 0
            # plot
            new_cases_plot = go.Figure()
            for c in country_order:
                new_cases_plot.add_traces(go.Bar(
                x=global_diff.loc[[c],'Date'].map(lambda x: pretty_date(x,'%d %B %Y')),
                y=global_diff.loc[[c], new_type],
                name=c))
        else:
            global_diff = diff.groupby('Date').sum().reset_index()
            global_diff .loc[global_diff['new_cases'] < 0,'new_cases'] = 0
            global_diff.loc[global_diff['new_deaths'] < 0,'new_deaths'] = 0
            # plot    
            new_cases_plot = go.Figure(go.Bar(
                x=global_diff['Date'].map(lambda x: pretty_date(x,'%d %B %Y')),
                y=global_diff[new_type],
                marker_color=marker_color,
                hovertemplate='%{y:.3s} '+ f'nouveau {type_value}<extra></extra>',))
        new_cases_plot.update_yaxes(showline=True)
        new_cases_plot.update_xaxes(showticklabels=False)
        new_cases_plot.update_layout(showlegend=False, barmode='stack', margin=margin)

    # 6. Output
        output_tuple = (
            ['Evolution du ', colorized_elm,' à travers le monde'],
            '{} au {}'.format(min_date, max_date),
            f'{millify(confirmed_count)}',
            f'{millify(death_count)}',
            map_plot,
            total_case,
            new_cases_plot,
            top10_plot,
            f'Evolution du nombre total de {type_value}',
            f'Nombre de nouveau {type_value} par jour',
        )
        return output_tuple