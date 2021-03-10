"""
oil price data source: https://www.ppac.gov.in/WriteReadData/userfiles/file/PP_9_a_DailyPriceMSHSD_Metro.pdf
"""

import pandas as pd
import numpy as np
import tabula
import requests
import plotly.express as px
import plotly.graph_objects as go
import time
from pandas.tseries.offsets import MonthEnd
import re
import xmltodict



def process_table(table_df):
    print("processing the downloaded PDF from PPAC website.")
    cols = ['Date', 'Delhi_Petrol', 'Mumbai_Petrol', 'Chennai_Petrol', 'Kolkata_Petrol',
    'Date_D', 'Delhi_Diesel', 'Mumbai_Diesel','Chennai_Diesel', 'Kolkata_Diesel']
    table_df.columns = cols
    table_df.drop(table_df.index[[0,3]],inplace=True)
    table_df.drop('Date_D',axis=1,inplace=True)
    table_df.dropna(how='any',inplace=True)
    table_df = table_df.astype(str)
    table_df = table_df.apply(lambda x: x.str.replace(" ", ""))
    table_df[['Delhi_Petrol', 'Mumbai_Petrol', 'Chennai_Petrol', 'Kolkata_Petrol', 'Delhi_Diesel', 'Mumbai_Diesel','Chennai_Diesel', 'Kolkata_Diesel']] = table_df[['Delhi_Petrol', 'Mumbai_Petrol', 'Chennai_Petrol', 'Kolkata_Petrol', 'Delhi_Diesel', 'Mumbai_Diesel','Chennai_Diesel', 'Kolkata_Diesel']].astype(float)
    table_df['Date'] = pd.to_datetime(table_df['Date'])
    table_petrol = table_df[['Date','Delhi_Petrol', 'Mumbai_Petrol', 'Chennai_Petrol','Kolkata_Petrol']]
    table_diesel = table_df[['Date','Delhi_Diesel', 'Mumbai_Diesel','Chennai_Diesel', 'Kolkata_Diesel']]
    new_cols = [i.replace("_Petrol", "") for i in list(table_petrol.columns)]
    table_petrol.columns = new_cols
    table_diesel.columns = new_cols
    return table_petrol, table_diesel

def get_international_exchange_rates(start_date,end_date):
    print("sending request for international exchange rates.")
    exchange_dates_url = "https://api.exchangeratesapi.io/history?"
    params = {"start_at": start_date, "end_at":end_date, "base":"USD", "symbols":"INR"}
    try:
        req = requests.get(exchange_dates_url,params=params)
    except Exception as e:
        print(e)
        print("request failed. using the saved data.")
        dollar_exchange_rates = pd.read_csv("dollar_exhange_rates.csv")
        dollar_exchange_rates['Date'] = pd.to_datetime(dollar_exchange_rates)
        dollar_exchange_rates.set_index('Date').sort_index(ascending=False)
        return dollar_exchange_rates
    else:
        print("request successful. processing the data.")
        dollar_exchange_rates = pd.DataFrame(req.json()['rates']).T.reset_index()
        dollar_exchange_rates['index'] = pd.to_datetime(dollar_exchange_rates['index'])
        dollar_exchange_rates.set_index('index').sort_index(ascending=False)
        dollar_exchange_rates.to_csv("dollar_exhange_rates.csv")
        return dollar_exchange_rates


# def merge_data(dollar_exchange_rates, international_oil_prices, oil_price_data):
#     print("merging the international oil price data, international exchange rate data and domestic oil price data.")
#     trim_int = international_oil_prices.loc[international_oil_prices.index.isin(oil_price_data.index)].dropna()
#     oil_price_data = oil_price_data.merge(trim_int, left_index=True, right_index=True).sort_index(ascending=False)
#     oil_price_data = oil_price_data.merge(dollar_exchange_rates, left_index=True, right_index=True).sort_index(ascending=False)
#     oil_price_data['INR'] = oil_price_data['INR'].round(2)
#     oil_price_data['INR_pc'] = (((oil_price_data['INR'] - oil_price_data['INR'].iloc[-1])/oil_price_data['INR'].iloc[-1])*100).round(2)
#     oil_price_data['rup_lit_crude'] = (oil_price_data['Price'] / 159) * oil_price_data['INR']
#     oil_price_data['int_pc'] = (((oil_price_data['Price'] - oil_price_data['Price'].iloc[-1])/oil_price_data['Price'].iloc[-1])*100).round(2)
#     oil_price_data['rup_lit_crude_pc'] = (((oil_price_data['rup_lit_crude'] - oil_price_data['rup_lit_crude'].iloc[-1])/oil_price_data['rup_lit_crude'].iloc[-1])*100).round(2)
#     return oil_price_data


def download_ppac():
    print("sending request for domestic oil price data from PPAC website.")
    ppac_url = r"https://www.ppac.gov.in/WriteReadData/userfiles/file/PP_9_a_DailyPriceMSHSD_Metro.pdf"
    try:
        req = requests.get(ppac_url)
    except Exception as e:
        print(e)
        print("Request unsuccessful. The saved file will be used.")
    else:

        with open('DATA/price_data.pdf', 'wb') as file:
            file.write(req.content)
        print('file saved successfully.')

def prepare_downloaded_file():
    print("preparing downloaded file for analysis.")
    oil_prices = 'DATA/price_data.pdf'
    tables = tabula.read_pdf(oil_prices, pages="all")
    proc_dfs = [process_table(i) for i in tables]
    petrol_df = pd.concat(i[0] for i in proc_dfs)
    diesel_df = pd.concat(i[1] for i in proc_dfs)
    print(f"Success. Length of Petrol prices {len(petrol_df)}------ diesel prices {len(diesel_df)}")
    petrol_df['mean_price'] = (petrol_df['Delhi']+petrol_df['Mumbai']+petrol_df['Chennai']+petrol_df['Kolkata'])/4
    diesel_df['mean_price'] = (diesel_df['Delhi']+diesel_df['Mumbai']+diesel_df['Chennai']+diesel_df['Kolkata'])/4
    print("Adding percent change columns")
    for i in petrol_df.columns[1:]:
        petrol_df[f'{i}_pc'] = (((petrol_df[i] - petrol_df[i].iloc[-1])/petrol_df[i].iloc[-1]) * 100).round(2)
   
    for i in diesel_df.columns[1:]:
        diesel_df[f'{i}_pc'] = (((diesel_df[i] - diesel_df[i].iloc[-1])/diesel_df[i].iloc[-1]) * 100).round(2)
    petrol_df.set_index("Date",inplace=True)
    diesel_df.set_index("Date",inplace=True)
    return petrol_df, diesel_df


def prep_consumption_df(consumption_df,year):
    consumption_df.reset_index(inplace=True)
    consumption_df.dropna(how='any',inplace=True)
    consumption_df.drop('index',axis=1,inplace=True)
    #print(consumption_df)
    cols = ['products', 'April','May','June','July','August','September','October','November','December','January','February','March','Total']
    consumption_df.drop(consumption_df.index[0],inplace=True)
    consumption_df.columns = cols
    consumption_df = consumption_df.loc[(consumption_df['products']=='MS')|(consumption_df['products']=='HSD')].reset_index().drop(['index','Total'],axis=1)
    melt_df = pd.melt(consumption_df, id_vars = 'products',var_name='month',value_name='average_cons')
    melt_df.sort_values('products',inplace=True)
    melt_df = melt_df.reset_index().drop('index',axis=1)
    melt_df['year'] = year
    melt_df['year'] = melt_df['year'].apply(lambda x: x.split('-')[0]).astype(int)
    melt_df['year'] = np.where((melt_df['month'].isin(['January','February','March'])),melt_df['year']+1,melt_df['year'])
    melt_df['average_cons'] = melt_df['average_cons'].astype(float).round(2)
    return melt_df


def prep_consumption_df_present(consumption_df,year):
    consumption_df.reset_index().drop('index',inplace=True,axis=1)
    consumption_df.drop(consumption_df.index[range(0,6)],inplace=True)
    consumption_df.reset_index(inplace=True)
    consumption_df.drop('index',axis=1,inplace=True)
    print(consumption_df)
    consumption_df.drop(consumption_df.index[range(14,20)],inplace=True)
    consumption_df.reset_index(inplace=True)
    consumption_df.drop('index',axis=1,inplace=True)
    #print(consumption_df)
    cols = ['products', 'April','May','June','July','August','September','October','November','December','January','February','March','Total']
    consumption_df.drop(consumption_df.index[0],inplace=True)
    consumption_df.columns = cols
    consumption_df = consumption_df.loc[(consumption_df['products']=='MS')|(consumption_df['products']=='HSD')].reset_index().drop(['index','Total'],axis=1)
    melt_df = pd.melt(consumption_df, id_vars = 'products',var_name='month',value_name='average_cons')
    melt_df.sort_values('products',inplace=True)
    melt_df = melt_df.reset_index().drop('index',axis=1)
    melt_df['year'] = year
    melt_df['year'] = melt_df['year'].apply(lambda x: x.split('-')[0]).astype(int)
    melt_df['year'] = np.where((melt_df['month'].isin(['January','February','March'])),melt_df['year']+1,melt_df['year'])
    melt_df['average_cons'] = melt_df['average_cons'].astype(float).round(2)
    return melt_df




def prep_historical_crude(hist_crude_df,year):
    cols = ['year', 'April','May','June','July','August','September','October','November','December','January','February','March','Average','Ratio']
    hist_crude_df = hist_crude_df.dropna(how='any').reset_index().drop('index',axis=1)
    hist_crude_df.columns = cols
    hist_crude_df.drop(hist_crude_df.index[0],inplace=True)
    hist_crude_df.drop(['Average','Ratio'],axis=1,inplace=True)
    melt_df = pd.melt(hist_crude_df, id_vars = 'year',var_name='month',value_name='import_bbl_usd')
    melt_df['year'] = melt_df['year'].apply(lambda x: x.split('-')[0]).astype(int)
    melt_df['year'] = np.where((melt_df['month'].isin(['January','February','March'])),melt_df['year']+1,melt_df['year'])
    melt_df['import_bbl_usd'] = melt_df['import_bbl_usd'].astype(float).round(2)
    melt_df = melt_df.loc[melt_df['year']>=year].sort_values(['year','month']).reset_index().drop('index',axis=1)
    return melt_df

def prep_current_crude(current_crude_df):
    current_crude_df.drop(current_crude_df.index[[i for i in range(0,12)]],inplace=True)
    current_crude_df.reset_index(inplace=True)
    current_crude_df.drop('index',inplace=True,axis=1)
    current_crude_df.drop(current_crude_df.index[[2,3,4]],inplace=True)
    cols = ['year', 'April','May','June','July','August','September','October','November','December','January','February','March']
    current_crude_df.columns = cols
    current_crude_df.drop(current_crude_df.index[0],inplace=True)
    melt_df = pd.melt(current_crude_df, id_vars = 'year',var_name='month',value_name='import_bbl_usd')
    melt_df['year'] = melt_df['year'].apply(lambda x: x.split('-')[0]).astype(int)
    melt_df['year'] = np.where((melt_df['month'].isin(['January','February','March'])),melt_df['year']+1,melt_df['year'])
    melt_df.dropna(inplace=True,how='any')
    melt_df['import_bbl_usd'] = melt_df['import_bbl_usd'].astype(float).round(2)
    return melt_df

def prep_historical_import(historical_import_df, year):
    cols = ['product', 'April','May','June','July','August','September','October','November','December','January','February','March','Total']
    print(historical_import_df)
    historical_import_df.dropna(how='all',inplace=True,axis=1)
    historical_import_df.columns = cols
    historical_import_df = historical_import_df.dropna(how='any').reset_index().drop('index',axis=1)
    historical_import_df = historical_import_df.loc[historical_import_df['product'].str.contains('import oil|ms|hsd|total',flags=re.I)].reset_index()
    historical_import_df.drop('index',axis=1,inplace=True)
    historical_import_df = historical_import_df[:4]
    historical_import_df = historical_import_df.melt(id_vars='product',var_name='month',value_name='import_rs_cr')
    historical_import_df['sheetname'] = year
    historical_import_df['year'] = historical_import_df['sheetname'].str.extract("(\d+)").astype(int)
    historical_import_df['year'] = np.where((historical_import_df['month'].isin(['January','February','March'])),historical_import_df['year']+1,historical_import_df['year'])
    historical_import_df.drop('sheetname',axis=1,inplace=True)
    return historical_import_df


def get_opec_crude(dmin):
    opec_url = "https://www.opec.org/basket/basketDayArchives.xml"
    req = requests.get(opec_url)
    xml_dict = xmltodict.parse(req.content)
    opec_df = pd.DataFrame(xml_dict['Basket']['BasketList'],columns=['Date','Price'])
    opec_df['Date'] = pd.to_datetime(opec_df["Date"])
    return opec_df.loc[opec_df['Date']>=dmin]
    



#Downloading the PDF file from PPAC website, saving the file and returning the final dataframes.
# if __name__ == "__main__"
download_ppac()
petrol_df, diesel_df = prepare_downloaded_file()
# int_oil_prices = pd.read_csv(r'oil-prices-master\oil-prices-master\data\brent-daily.csv')
# print(f'loaded international oil prices. Length {len(int_oil_prices)}')
# int_oil_prices["Date"] = pd.to_datetime(int_oil_prices['Date'])
# int_oil_prices.set_index("Date",inplace=True)
# Saving the merged petrol and diesel data
petrol_df['Type'], diesel_df['Type'] = 'Petrol', 'Diesel'
merged_price_data = pd.concat([petrol_df, diesel_df])
merged_price_data.to_csv('price_df_merged.csv')
#Getting the international exchange rates.
start_date = str(petrol_df.index.min())[:10]
end_date = str(petrol_df.index.max())[:10]
dollar_exchange_rates = get_international_exchange_rates(start_date, end_date)
dollar_exchange_rates.set_index('index',inplace=True)
month_avg_dol = dollar_exchange_rates.resample('M').mean()
month_avg_dol['month'] = month_avg_dol.index.month_name()
month_avg_dol['year'] = month_avg_dol.index.year

#creating merged dataframes for international section analysis.
# petrol_df_merged = merge_data(dollar_exchange_rates, int_oil_prices, petrol_df)
# diesel_df_merged = merge_data(dollar_exchange_rates, int_oil_prices, diesel_df)
#loading the monthly average crude prices dataset
consumption_dict = pd.read_excel("DATA/consumption_historical_original.xls", sheet_name=["2017-18","2018-19","2019-20"])
consumption_hist = pd.concat([prep_consumption_df(df,year) for year,df in consumption_dict.items()]).reset_index()
consumption_hist.drop('index',axis=1,inplace=True)
consumption_present = pd.read_excel("DATA/PT_consumption.xls")
consumption_present = prep_consumption_df_present(consumption_present,"2020-21")
consumption_data = pd.concat([consumption_present,consumption_hist]).reset_index().drop('index',axis=1)
consumption_data['merge_col'] = consumption_data['year'].astype(str) + " " +consumption_data['month']
consumption_data['type'] = np.where((consumption_data['products']=='MS'),'Petrol','Diesel')

#1 metric ton = 1210 liters for diesel
#1 metric ton Petrol (MS) =  1411 litres of diesel [http://petroleum.nic.in/sites/default/files/readyrecknor_Oct14.pdf]



#Handling the historical crude and current crude files. Returns a dataframe with total imports in price_rs_billion_lit
crude_import_bbl = pd.read_excel("DATA/historical_crude_bbl.xls")
crude_import_bbl = prep_historical_crude(crude_import_bbl,2017)
current_crude_bbl = pd.read_excel("DATA/current_crude_bbl.xls")
current_crude_bbl = prep_current_crude(current_crude_bbl)
month_avg_dol['merge_col'] = month_avg_dol['year'].astype(str) + " " +month_avg_dol['month']
crude_bbl = pd.concat([crude_import_bbl, current_crude_bbl]).reset_index().drop('index',axis=1)
crude_bbl['merge_col'] = crude_bbl['year'].astype(str) + " " +crude_bbl['month']
crude_bbl = crude_bbl.merge(month_avg_dol)
crude_bbl['INR'] = crude_bbl['INR'].round(2)
crude_bbl['price_rs_lit_crude'] = crude_bbl['import_bbl_usd'] * crude_bbl['INR'] / 159 #calculating price in Rs per litre from dollars per barrel


#Handling the historical and current crude import data
req_sheets = ['PT_Import_Val_Rs 2019-20', 'PT_Import_Val_2018-19', 'PT_Import_Val_2017-18']
crude_import = pd.read_excel('DATA/import_historical_original.xls',sheet_name=req_sheets)
crude_import = pd.concat([prep_historical_import(i,filename) for filename,i in crude_import.items()]).reset_index()
crude_import.drop('index',axis=1,inplace=True)



#Calculating monthly average prices for petrol and diesel

petrol_monthly_average = petrol_df.resample('M').mean()
to_drop = [i for i in petrol_monthly_average if 'pc' in i]
petrol_monthly_average.drop(to_drop, inplace=True,axis=1)
petrol_monthly_average['month'] = petrol_monthly_average.index.month_name()
petrol_monthly_average['year'] = petrol_monthly_average.index.year
petrol_monthly_average['merge_col'] = petrol_monthly_average['year'].astype(str) + " " + petrol_monthly_average['month']
petrol_monthly_average = petrol_monthly_average.merge(crude_bbl)
petrol_monthly_average['type'] = 'Petrol'
petrol_monthly_average['Date'] = pd.to_datetime(petrol_monthly_average['merge_col'])+MonthEnd(1)



diesel_monthly_average = diesel_df.resample('M').mean()
to_drop = [i for i in diesel_monthly_average if 'pc' in i]
diesel_monthly_average.drop(to_drop, inplace=True,axis=1)
diesel_monthly_average['month'] = diesel_monthly_average.index.month_name()
diesel_monthly_average['year'] = diesel_monthly_average.index.year
diesel_monthly_average['merge_col'] = diesel_monthly_average['year'].astype(str) + " " + diesel_monthly_average['month']
diesel_monthly_average = diesel_monthly_average.merge(crude_bbl)
diesel_monthly_average['type'] = 'Diesel'
diesel_monthly_average['Date'] = pd.to_datetime(diesel_monthly_average['merge_col'])+MonthEnd(1)


#creating merge_col to merge with the monthly average crude oil import price data
merged_monthly_average = pd.concat([petrol_monthly_average,diesel_monthly_average]).reset_index().drop('index',axis=1)
merged_monthly_average.to_csv("DATA/merged_monthly_average.csv")

#merging the monthly average price data and consumption data

monthly_avg_cons = consumption_data.merge(merged_monthly_average)
monthly_avg_cons.to_csv("DATA/month_avg_cons.csv")

#Plotting graphs
##sample plotly graphs which form the base for the app
##Commenting this out - beyond the scope of this file

# cols_to_plot = ['Delhi', 'Mumbai', 'Chennai', 'Kolkata','mean_price']
# pr_fig = go.Figure()
# for i in cols_to_plot:
    
#     pr_fig.add_trace(go.Line(x = petrol_df.index,
#             y = petrol_df[i],
#                             name=i))
# for i in cols_to_plot:
#         pr_fig.add_trace(go.Line(x = diesel_df.index,
#             y = diesel_df[i],
#                             name=i,visible=False))
# pr_fig.update_layout(dict(xaxis=dict(rangeselector=dict(
#         buttons=list([
#             dict(count=1, label="1m", step="month", stepmode="backward"),
#             dict(count=6, label="6m", step="month", stepmode="backward"),
#             dict(count=1, label="YTD", step="year", stepmode="todate"),
#             dict(count=1, label="1y", step="year", stepmode="backward"),
#             dict(step="all")
#         ]))
# ,
#         rangeslider=dict(
#             visible=True
#         ),
#         type="date",
#     ),
#     hovermode = 'x unified',
#     dragmode = 'zoom',
#     hoverlabel = dict(
#         bgcolor="lightcyan",
#         font_size=12,
#         font_family="Overpass",
#         namelength = -1,
#     ),
#     yaxis = dict(showspikes=True),
#     updatemenus=[go.layout.Updatemenu(
#         type="buttons",
#         active=0,
#         buttons=list(
#             [dict(label = 'Petrol',
#                 method = 'update',
#                 args = [{'visible': [True, True,True,True,True,False,False,False,False,False]},
#                         {'title': 'Petrol Prices',
#                         'showlegend':True}]),
#             dict(label = 'Diesel',
#                 method = 'update',
#                 args = [{'visible': [False,False,False,False,False,True,True,True,True,True]}, # the index of True aligns with the indices of plot traces
#                         {'title': 'Diesel Prices',
#                         'showlegend':True}])
#             ])
#         )
#     ]
    
#     )
# )
# pr_fig.show()
# #domestic percent change
# cols_to_plot = ['Delhi_pc', 'Mumbai_pc', 'Chennai_pc', 'Kolkata_pc','mean_price_pc']
# pc_fig = go.Figure()
# for i in cols_to_plot:
#     pc_fig.add_trace(go.Line(x = petrol_df.index,
#                             y = petrol_df[i],
#                             name=i.replace("_pc","")+r" % change petrol"))
# for i in cols_to_plot:
#     pc_fig.add_trace(go.Line(x = diesel_df.index,
#                             y = diesel_df[i],
#                             name=i.replace("_pc","")+r" % change diesel",visible=False))
# pc_fig.update_layout(dict(xaxis=dict(rangeselector=dict(
#         buttons=list([
#             dict(count=1, label="1m", step="month", stepmode="backward"),
#             dict(count=6, label="6m", step="month", stepmode="backward"),
#             dict(count=1, label="YTD", step="year", stepmode="todate"),
#             dict(count=1, label="1y", step="year", stepmode="backward"),
#             dict(step="all")
#         ]))
# ,
#         rangeslider=dict(
#             visible=True
#         ),
#         type="date",
#     ),
#     hovermode = 'x unified',
#     dragmode = 'zoom',
#     hoverlabel = dict(
#         bgcolor="lightcyan",
#         font_size=12,
#         font_family="Overpass",
#         namelength = -1,
#     ),
#     yaxis = dict(showspikes=True),
#     updatemenus=[go.layout.Updatemenu(
#         type="buttons",
#         active=1,
#         buttons=list(
#             [dict(label = 'All',
#                 method = 'update',
#                 args = [{'visible': [True, True,True,True,True,True,True,True,True,True]},
#                         {'title': 'All Prices',
#                         'showlegend':True}]),
#             dict(label = 'Petrol',
#                 method = 'update',
#                 args = [{'visible': [True, True,True,True,True,False,False,False,False,False]},
#                         {'title': 'Petrol Prices',
#                         'showlegend':True}]),
#             dict(label = 'Diesel',
#                 method = 'update',
#                 args = [{'visible': [False,False,False,False,False,True,True,True,True,True]}, # the index of True aligns with the indices of plot traces
#                         {'title': 'Diesel Prices',
#                         'showlegend':True}])
#             ])
#         )
#     ]
    
#     )
# )
# pc_fig.show()
# #comparison with international crude oil price (converted to INR/dollar_lit)
# cols_to_plot = ['Delhi','Mumbai','Chennai','Kolkata','rup_lit_crude','mean_price']
# pc_fig_int_comp = go.Figure()
# for i in cols_to_plot:
#     pc_fig_int_comp.add_trace(go.Line(x = petrol_df_merged.index,
#                             y = petrol_df_merged[i],
#                             name=i.replace("_pc","")))
# for i in cols_to_plot:
#     pc_fig_int_comp.add_trace(go.Line(x = diesel_df_merged.index,
#                             y = diesel_df_merged[i],
#                             name=i.replace("_pc",""),visible=False))
# pc_fig_int_comp.update_layout(dict(xaxis=dict(rangeselector=dict(
#         buttons=list([
#             dict(count=1, label="1m", step="month", stepmode="backward"),
#             dict(count=6, label="6m", step="month", stepmode="backward"),
#             dict(count=1, label="YTD", step="year", stepmode="todate"),
#             dict(count=1, label="1y", step="year", stepmode="backward"),
#             dict(step="all")
#         ]))
# ,
#         rangeslider=dict(
#             visible=True
#         ),
#         type="date",
#     ),
#     hovermode = 'x unified',
#     dragmode = 'zoom',
#     hoverlabel = dict(
#         bgcolor="lightcyan",
#         font_size=12,
#         font_family="Overpass",
#         namelength = -1,
#     ),
#     yaxis = dict(showspikes=True),
#     updatemenus=[go.layout.Updatemenu(
#         type="buttons",
#         active=1,
#         buttons=list(
#             [dict(label = 'Petrol',
#                 method = 'update',
#                 args = [{'visible': [True, True,True,True,True,True,False,False,False,False,False,False]},
#                         {'title': 'Petrol Prices',
#                         'showlegend':True}]),
#             dict(label = 'Diesel',
#                 method = 'update',
#                 args = [{'visible': [False,False,False,False,False,False,True,True,True,True,True,True]}, # the index of True aligns with the indices of plot traces
#                         {'title': 'Diesel Prices',
#                         'showlegend':True}])
#             ])
#         )
#     ]
    
#     )
# )
# pc_fig_int_comp.show()
# #comparison with international percent change in price of oil
# cols_to_plot = ['Delhi_pc', 'Mumbai_pc', 'Chennai_pc', 'Kolkata_pc','mean_price_pc']
# pc_fig_int = go.Figure()
# for i in cols_to_plot:
#     pc_fig_int.add_trace(go.Line(x = petrol_df_merged.index,
#                             y = petrol_df_merged[i],
#                             name=i.replace("_pc","")+r" % change petrol"))
# for i in cols_to_plot:
#     pc_fig_int.add_trace(go.Line(x = diesel_df_merged.index,
#                             y = diesel_df_merged[i],
#                             name=i.replace("_pc","")+r" % change diesel",visible=False))
# pc_fig_int.update_layout(dict(xaxis=dict(rangeselector=dict(
#         buttons=list([
#             dict(count=1, label="1m", step="month", stepmode="backward"),
#             dict(count=6, label="6m", step="month", stepmode="backward"),
#             dict(count=1, label="YTD", step="year", stepmode="todate"),
#             dict(count=1, label="1y", step="year", stepmode="backward"),
#             dict(step="all")
#         ]))
# ,
#         rangeslider=dict(
#             visible=True
#         ),
#         type="date",
#     ),
#     hovermode = 'x unified',
#     dragmode = 'zoom',
#     hoverlabel = dict(
#         bgcolor="lightcyan",
#         font_size=12,
#         font_family="Overpass",
#         namelength = -1,
#     ),
#     yaxis = dict(showspikes=True),
#     updatemenus=[go.layout.Updatemenu(
#         type="buttons",
#         active=1,
#         buttons=list(
#             [dict(label = 'All',
#                 method = 'update',
#                 args = [{'visible': [True, True,True,True,True,True,True,True,True,True,True,True]},
#                         {'title': 'All Prices',
#                         'showlegend':True}]),
#             dict(label = 'Petrol',
#                 method = 'update',
#                 args = [{'visible': [True, True,True,True,True,True,False,False,False,False,False,False]},
#                         {'title': 'Petrol Prices',
#                         'showlegend':True}]),
#             dict(label = 'Diesel',
#                 method = 'update',
#                 args = [{'visible': [False,False,False,False,False,False,True,True,True,True,True,True]}, # the index of True aligns with the indices of plot traces
#                         {'title': 'Diesel Prices',
#                         'showlegend':True}])
#             ])
#         )
#     ]
    
#     )
# )
# pc_fig_int.show()

#     #how do international crude oil prices move with the exchange rate and mean price in India?

#     pc_int = go.Figure()
#     pc_int.add_trace(go.Line(x = petrol_df_merged.index,
#                                 y = petrol_df_merged["mean_price_pc"],
#                                 name=r" % change petrol"))
#     pc_int.add_trace(go.Line(x = diesel_df_merged.index,
#                                 y = diesel_df_merged["mean_price_pc"],
#                                 name=r" % change diesel oil price"))
#     pc_int.add_trace(go.Line(x = petrol_df_merged.index,
#                                 y = petrol_df_merged["INR_pc"],
#                                 name=r" % change INR exchange rate"))
#     pc_int.add_trace(go.Line(x = petrol_df_merged.index,
#                                 y = petrol_df_merged["rup_lit_crude"],
#                                 name=r" % change crude oil price per litre"))
#     pc_int.add_trace(go.Line(x = petrol_df_merged.index,
#                                 y = petrol_df_merged["int_pc"],
#                                 name=r" % change international oil price"))



#     pc_int.update_layout(dict(xaxis=dict(rangeselector=dict(
#             buttons=list([
#                 dict(count=1, label="1m", step="month", stepmode="backward"),
#                 dict(count=6, label="6m", step="month", stepmode="backward"),
#                 dict(count=1, label="YTD", step="year", stepmode="todate"),
#                 dict(count=1, label="1y", step="year", stepmode="backward"),
#                 dict(step="all")
#             ]))
#     ,
#             rangeslider=dict(
#                 visible=True
#             ),
#             type="date",
#         ),
#         hovermode = 'x unified',
#         dragmode = 'zoom',
#         hoverlabel = dict(
#             bgcolor="lightcyan",
#             font_size=12,
#             font_family="Overpass",
#             namelength = -1,


#         ),
#         yaxis = dict(showspikes=True),
#         )
#     )
#     pc_int.show()



