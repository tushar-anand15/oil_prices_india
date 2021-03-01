#importing packages

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

#reading data
#merged price data
df = pd.read_csv('price_data/price_df_merged.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
cols_to_plot = ['Delhi', 'Mumbai', 'Chennai', 'Kolkata','Mean','All']

#international price merged data
merged_df = pd.read_csv('price_data/merged_data_int.csv')
merged_df['Date'] = pd.to_datetime(merged_df['Date'])
merged_df['Year'] = merged_df['Date'].dt.year
merged_df['Month'] = merged_df['Date'].dt.month


#merged monthly average price data
month_avg = pd.read_csv("price_data/merged_monthly_average.csv")
month_avg['Date'] = pd.to_datetime(month_avg['Date'])
month_avg_cols = ['Delhi','Mumbai','Chennai','Kolkata','Mean','All']
month_avg['year'] = month_avg['Date'].dt.year

#merged monthly average and consumption data
##TODO


# month_avg_cons = pd.read_csv("month_avg_cons.csv")
# month_avg_cons['Date'] = pd.to_datetime(month_avg_cons['Date'])
# month_avg_cons_cols = ['Delhi','Mumbai','Chennai','Kolkata','All','Mean']
# month_avg_cons['year'] = month_avg_cons['Date'].dt.year



markdown_text_heading = """
## Petrol and diesel prices in India \

The dashboard uses RSP data for petrol and diesel from the [PPAC](https://www.ppac.gov.in/) website.
It tracks prices in four metropolitan cities: Delhi, Mumbai, Chennai and Kolkata. \
    

"""

markdown_text_graph_pc = """
### Percent change in oil prices from June, 2017.\



"""

markdown_text_graph_int = """
## Oil prices in relation to Brent crude oil prices\

Brent crude prices are reported in dollars per barrel. This is converted to rupees per litre using the dollar exchange price
on the reported date and conversion factor of 159 litres per barrel.
"""

markdown_text_graph_int_pc = """
## Percent change in domestic oil prices and Brent crude oil price\

"""


markdown_text_monthly_average = """
## Monthly average retail price of petrol and diesel with the price of Indian basket of crude oil import (converted to rupees per litre from dollars per barrel.)

"""

# markdown_text_monthly_average_consumption = """

# ## Monthly average consumption with the monthly average retail price and monthly average crude oil price

# """


app.layout = html.Div([
    dcc.Markdown(children=markdown_text_heading),

    html.Div([
#first plot: petrol and diesel price
        html.Div([
            dcc.Dropdown(
                id='graph-type',
                options=[{'label': i, 'value': i} for i in ['Petrol','Diesel']],
                value='Petrol'
            ),
            
        ],
        style={'width': '10%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='city-column',
                options=[{'label': i, 'value': i} for i in cols_to_plot],
                value='All',
                multi=True
            )
        ],style={'width': '20%', 'float': 'center','display': 'inline-block'}),
        
    ]),
    
    dcc.Graph(id='price-graphic'),
    html.Div([
        dcc.RangeSlider(
        id='year-slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        step=None,
        value=[df['Year'].min(), df['Year'].max()],
        marks={str(i):str(i) for i in df['Year'].unique()},
        updatemode = 'mouseup'
    )],style={'width': '80%','padding-left':'10%', 'padding-right':'10%'}, 
    
    ),
    
    html.Div([
        dcc.Markdown(children=markdown_text_graph_pc),
      html.Div([dcc.Dropdown(
                id='graph-type-pc',
                options=[{'label': i, 'value': i} for i in ['Petrol','Diesel']],
                value='Petrol'
            ),
            
        ],
        style={'width': '10%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='city-column-pc',
                options=[{'label': i, 'value': i} for i in cols_to_plot],
                value='All',
                multi=True
            )
        ],style={'width': '20%', 'float': 'center','display': 'inline-block'}),
        
    ]),

    dcc.Graph(id='price-graphic-pc'),
    html.Div([
        dcc.RangeSlider(
        id='year-slider-pc',
        min=df['Year'].min(),
        max=df['Year'].max(),
        step=None,
        value=[df['Year'].min(), df['Year'].max()],
        marks={str(i):str(i) for i in df['Year'].unique()},
        updatemode = 'mouseup'
    )
    ],style={'width': '80%','padding-left':'10%', 'padding-right':'10%'}),

    html.Div([
        dcc.Markdown(children=markdown_text_graph_int),
      html.Div([dcc.Dropdown(
                id='graph-type-int',
                options=[{'label': i, 'value': i} for i in ['Petrol','Diesel']],
                value='Petrol'
            ),
            
        ],
        style={'width': '10%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='city-column-int',
                options=[{'label': i, 'value': i} for i in cols_to_plot],
                value='All',
                multi=True
            )
        ],style={'width': '20%', 'float': 'center','display': 'inline-block'}),
        
    ]),

    dcc.Graph(id='price-graphic-int'),
    html.Div([dcc.RangeSlider(
        id='year-slider-int',
        min=merged_df['Year'].min(),
        max=merged_df['Year'].max(),
        step=None,
        value=[merged_df['Year'].min(), merged_df['Year'].max()],
        marks={str(i):str(i) for i in merged_df['Year'].unique()},
        updatemode = 'mouseup'
    )], style = {'width': '80%','padding-left':'10%', 'padding-right':'10%'}),
    html.Div([
        dcc.Markdown(children=markdown_text_graph_int_pc),
      ]),

    dcc.Graph(id='price-graphic-int-pc'),
        html.Div([dcc.RangeSlider(
        id='year-slider-int-pc',
        min=merged_df['Year'].min(),
        max=merged_df['Year'].max(),
        step=None,
        value=[merged_df['Year'].min(), merged_df['Year'].max()],
        marks={str(i):str(i) for i in merged_df['Year'].unique()},
        updatemode = 'mouseup')],style={'width': '80%','padding-left':'10%', 'padding-right':'10%'}
    ),
    
html.Div([
        dcc.Markdown(children=markdown_text_monthly_average),
      html.Div([dcc.Dropdown(
                id='graph-type-month-avg',
                options=[{'label': i, 'value': i} for i in ['Petrol','Diesel']],
                value='Petrol'
            ),
            
        ],
        style={'width': '10%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='city-column-month-avg',
                options=[{'label': i, 'value': i} for i in month_avg_cols],
                value='All',
                multi=True
            )
        ],style={'width': '20%', 'float': 'center','display': 'inline-block'}),
        
    ]),

    dcc.Graph(id='price-graphic-month-avg'),
    html.Div([dcc.RangeSlider(
        id='year-slider-month-avg',
        min=month_avg['year'].min(),
        max=month_avg['year'].max(),
        step=None,
        value=[month_avg['year'].min(), month_avg['year'].max()],
        marks={str(i):str(i) for i in month_avg['year'].unique()},
        updatemode = 'mouseup'
    )], style = {'width': '80%','padding-left':'10%', 'padding-right':'10%'}),


# html.Div([
#         dcc.Markdown(children=markdown_text_monthly_average_consumption),
#       html.Div([dcc.Dropdown(
#                 id='graph-type-month-avg-cons',
#                 options=[{'label': i, 'value': i} for i in ['Petrol','Diesel']],
#                 value='Petrol'
#             ),
            
#         ],
#         style={'width': '10%', 'display': 'inline-block'}),

#         html.Div([
#             dcc.Dropdown(
#                 id='city-column-month-avg-cons',
#                 options=[{'label': i, 'value': i} for i in month_avg_cons_cols],
#                 value='All',
#                 multi=True
#             )
#         ],style={'width': '20%', 'float': 'center','display': 'inline-block'}),
        
#     ]),

    # dcc.Graph(id='price-graphic-month-avg-cons'),
    # html.Div([dcc.RangeSlider(
    #     id='year-slider-month-avg-cons',
    #     min=month_avg_cons['year'].min(),
    #     max=month_avg_cons['year'].max(),
    #     step=None,
    #     value=[month_avg_cons['year'].min(), month_avg_cons['year'].max()],
    #     marks={str(i):str(i) for i in month_avg_cons['year'].unique()},
    #     updatemode = 'mouseup'
    # )], style = {'width': '80%','padding-left':'10%', 'padding-right':'10%'}),
    

    ])



@app.callback(
    Output('price-graphic', 'figure'),
    Input('graph-type', 'value'),
    Input('city-column', 'value'),
    Input('year-slider', 'value')
    )
def update_graph(graph_type_name, city_column_name,
                 year_value):
    year_range = [i for i in range(year_value[0], (year_value[1]+1))]
    dff = df[df['Year'].isin(year_range)]
    dff = dff[dff['Type']==graph_type_name]
    if 'All' in city_column_name:
        plot_cols = ['Mumbai', 'Delhi', 'Chennai', 'Kolkata']
    else:
        plot_cols = city_column_name
    pr_fig = go.Figure()
    pr_fig.add_trace(go.Line(x=dff['Date'],
                                    y = dff['Mean'],
                                    name = "Mean",showlegend=True))
    for i in plot_cols:
        pr_fig.add_trace(go.Line(x = dff['Date'],
                        y = dff[i],
                        name = i))
        
    pr_fig.update_xaxes(showspikes=True,showline=True, mirror=True,title="Time",title_font = dict(family = 'Overpass', size = 16))
    pr_fig.update_layout(template = 'none', 
    hoverlabel = dict(
        bgcolor="lightcyan",
        font_size=12,
        font_family="Overpass",
        namelength = -1,
    ),hovermode = 'x unified',
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
    borderwidth=1,
    itemclick = 'toggleothers',
    itemdoubleclick = 'toggle'
),title = "Daily retail sale price since June 16, 2017",
title_font = dict(family = 'Overpass', size = 20)
    )
    pr_fig.update_yaxes(showspikes = True,showline=True, mirror=True,title="Price(INR)",title_font = dict(family = 'Overpass', size = 16))
    return pr_fig


@app.callback(
    Output('price-graphic-pc', 'figure'),
    Input('graph-type-pc', 'value'),
    Input('city-column-pc', 'value'),
    Input('year-slider-pc', 'value')
    )
def update_graph(graph_type_name, city_column_name,
                 year_value):
    #print(year_value)
    year_range = [i for i in range(year_value[0], (year_value[1]+1))]
    dff = df[df['Year'].isin(year_range)]
    dff = dff[dff['Type']==graph_type_name]
    if 'All' in city_column_name:
        plot_cols = ['Mumbai_pc', 'Delhi_pc', 'Chennai_pc', 'Kolkata_pc']
    else:
        plot_cols = [i+"_pc" for i in city_column_name]
    pr_fig_pc = go.Figure()
    pr_fig_pc.add_trace(go.Line(x=dff['Date'],
                                    y = dff['Mean_pc'],
                                    name = "Mean",showlegend=True))
    for i in plot_cols:
        pr_fig_pc.add_trace(go.Line(x = dff['Date'],
                        y = dff[i],
                        name = i.replace("_pc","")))
        
    pr_fig_pc.update_xaxes(showspikes=True,title="Time",mirror=True,showline=True,title_font = dict(family = 'Overpass', size = 16))
    pr_fig_pc.update_layout(template = 'none', 
    hoverlabel = dict(
        bgcolor="lightcyan",
        font_size=12,
        font_family="Overpass",
        namelength = -1,
    ),hovermode = 'x unified',
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
    borderwidth=1,
    itemclick = 'toggleothers',
    itemdoubleclick = 'toggle'
),title = "Percent change in fuel prices",
title_font = dict(family = 'Overpass', size = 20)
    )
    
    pr_fig_pc.update_yaxes(showspikes = True,title = "Percent change",mirror=True,showline=True,title_font = dict(family = 'Overpass', size = 16))
    return pr_fig_pc



@app.callback(
    Output('price-graphic-int', 'figure'),
    Input('graph-type-int', 'value'),
    Input('city-column-int', 'value'),
    Input('year-slider-int', 'value')
    )
def update_graph(graph_type_name, city_column_name,
                 year_value):
    year_range = [i for i in range(year_value[0], (year_value[1]+1))]
    dff = merged_df[merged_df['Year'].isin(year_range)]
    dff = dff[dff['Type']==graph_type_name]
    if 'All' in city_column_name:
        plot_cols = ['Mumbai', 'Delhi', 'Chennai', 'Kolkata', 'Mean']
    else:
        plot_cols = [i for i in city_column_name]
    pr_fig_int = go.Figure()
    pr_fig_int.add_trace(go.Line(x = dff['Date'],
                                y = dff['rup_lit_crude'],
                                name = 'Crude oil (Rupees per litre)'))
    for i in plot_cols:
        pr_fig_int.add_trace(go.Line(x = dff['Date'],
                        y = dff[i],
                        name = i))
        
    pr_fig_int.update_xaxes(showspikes=True,mirror=True,showline=True,title = "Time",title_font = dict(family = 'Overpass', size = 16))
    pr_fig_int.update_layout(template = 'none', 
    hoverlabel = dict(
        bgcolor="lightcyan",
        font_size=12,
        font_family="Overpass",
        namelength = -1,
    ),hovermode = 'x unified',
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
    borderwidth=1,
    itemclick = 'toggleothers',
    itemdoubleclick = 'toggle'
),title = "Oil prices since June 16, 2017",
title_font = dict(family = 'Overpass', size = 20)
    )
    
    pr_fig_int.update_yaxes(showspikes = True,title = "Price (INR)",mirror=True,showline=True,title_font = dict(family = 'Overpass', size = 16))
    return pr_fig_int


@app.callback(
    Output('price-graphic-int-pc', 'figure'),
    Input('year-slider-int-pc', 'value')
    )
def update_graph(year_value):
    year_range = [i for i in range(year_value[0], (year_value[1]+1))]
    dff = merged_df[merged_df['Year'].isin(year_range)]
    pr_fig_pc_int = go.Figure()
    pr_fig_pc_int.add_trace(go.Line(x = dff.loc[dff['Type']=='Petrol']['Date'],
                                y = dff['rup_lit_crude_pc'],
                                name = 'Crude oil (Rupees per litre)'))

    pr_fig_pc_int.add_trace(go.Line(x = dff.loc[dff['Type']=='Petrol']['Date'],
                                y = dff.loc[dff['Type']=='Petrol']['Mean_pc'],
                                name = 'Petrol price'))

    pr_fig_pc_int.add_trace(go.Line(x = dff.loc[dff['Type']=='Diesel']['Date'],
                                y = dff.loc[dff['Type']=='Diesel']['Mean_pc'],
                                name = 'Diesel price'))
        
    pr_fig_pc_int.update_xaxes(showspikes=True, title= 'Time',mirror=True,showline=True)
    pr_fig_pc_int.update_layout(template = 'none', 
    hoverlabel = dict(
        bgcolor="lightcyan",
        font_size=12,
        font_family="Overpass",
        namelength = -1,
    ),hovermode = 'x unified',
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
    borderwidth=1,
    itemclick = 'toggleothers',
    itemdoubleclick = 'toggle'
),title = "Daily retail sale price since June 16, 2017",
title_font = dict(family = 'Overpass', size = 20)
    )
    pr_fig_pc_int.update_yaxes(showspikes = True,title = "Price (INR)",mirror=True,showline=True,title_font = dict(family = 'Overpass', size = 16))
    return pr_fig_pc_int


@app.callback(
    Output('price-graphic-month-avg', 'figure'),
    Input('graph-type-month-avg', 'value'),
    Input('city-column-month-avg', 'value'),
    Input('year-slider-month-avg', 'value')
    )
def update_graph(graph_type_name, city_column_name,
                 year_value):
    year_range = [i for i in range(year_value[0], (year_value[1]+1))]
    dff = month_avg[month_avg['year'].isin(year_range)]
    

    #handle graph type name
    dff = dff[dff['type']==graph_type_name]
    #handle city name

    #handle city options
    if "All" in city_column_name:
        plot_cols_mon_avg = ['Delhi', 'Mumbai', 'Chennai', 'Kolkata','Mean']
       
    else:
        plot_cols_mon_avg = [i for i in city_column_name]
        #plot_cols_mon_avg.append('price_rs_lit_crude')
        
    mon_av_fig = go.Figure()
    # mon_av_fig.add_trace(go.Line(x = dff['Date'],
    #                             y = dff['price_rs_lit_crude'],
    #                             name = 'Crude oil (Rupees per litre)',fill = 'tonexty'))
    
    for i in plot_cols_mon_avg:
        mon_av_fig.add_trace(go.Line(x = dff['Date'],
                        y = dff[i],
                        name = i))
    mon_av_fig.add_trace(go.Line(x = dff['Date'],
                                y = dff['price_rs_lit_crude'],
                                name = 'Crude oil (Rupees per litre)'))  
    mon_av_fig.update_xaxes(showspikes=True,mirror=True,showline=True,title = "Time",title_font = dict(family = 'Overpass', size = 16))
    mon_av_fig.update_layout(template = 'none', 
    hoverlabel = dict(
        bgcolor="lightcyan",
        font_size=12,
        font_family="Overpass",
        namelength = -1,
    ),hovermode = 'x unified',
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
    borderwidth=1,
    itemclick = 'toggleothers',
    itemdoubleclick = 'toggle'
),title = "Monthly average oil prices since June, 2017",
title_font = dict(family = 'Overpass', size = 20)
    )
    mon_av_fig.update_yaxes(showspikes = True,title = "Price (INR)",mirror=True,showline=True,title_font = dict(family = 'Overpass', size = 16))
    return mon_av_fig


# @app.callback(
#     Output('price-graphic-month-avg-cons', 'figure'),
#     Input('graph-type-month-avg-cons', 'value'),
#     Input('city-column-month-avg-cons', 'value'),
#     Input('year-slider-month-avg-cons', 'value')
#     )
# def update_graph(graph_type_name, city_column_name,
#                  year_value):
#     year_range = [i for i in range(year_value[0], (year_value[1]+1))]
#     dff = month_avg_cons[month_avg_cons['year'].isin(year_range)]
    

#     #handle graph type name
#     dff = dff[dff['type']==graph_type_name]
#     #handle city name

#     #handle city options
#     if "All" in city_column_name:
#         plot_cols_mon_avg = ['Delhi', 'Mumbai', 'Chennai', 'Kolkata','Mean']
       
#     else:
#         plot_cols_mon_avg = [i for i in city_column_name]
#         #plot_cols_mon_avg.append('price_rs_lit_crude')
        
#     mon_avg_cons_fig = go.Figure()
#     mon_avg_cons_fig.add_trace(go.Line(x = dff['Date'],
#                                 y = dff['price_rs_lit_crude'],
#                                 name = 'Crude oil (Rupees per litre)'))
#     mon_avg_cons_fig.add_trace(go.Line(x = dff['Date'],
#                                 y = dff['price_rs_lit_crude'],
#                                 name = 'Crude oil (Rupees per litre)'))
#     mon_avg_cons_fig.add_trace(go.Line(x = dff['Date'],
#                                 y = dff['average_cons'],
#                                 name = 'Average consumption'))
    

#     for i in plot_cols_mon_avg:
#         mon_avg_cons_fig.add_trace(go.Line(x = dff['Date'],
#                         y = dff[i],
#                         name = i))
        
#     mon_avg_cons_fig.update_xaxes(showspikes=True,mirror=True,showline=True)
#     mon_avg_cons_fig.update_layout(template = 'none', 
#     hoverlabel = dict(
#         bgcolor="lightcyan",
#         font_size=12,
#         font_family="Overpass",
#         namelength = -1,
#     ),hovermode = 'x unified'
#     )
#     mon_avg_cons_fig.update_yaxes(showspikes = True,mirror=True,showline=True)
#     return mon_avg_cons_fig



if __name__ == '__main__':
    app.run_server(debug=True)