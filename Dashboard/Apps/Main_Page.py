# Import packages
# from dash_labs.plugins.pages import register_page
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

from App import app

import pathlib
import re

import numpy as np
import numpy_financial as npf

import pandas as pd

from bs4 import BeautifulSoup
import requests


######################################################################################################################
# NEW BLOCK - Pre app setup
######################################################################################################################

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../Data").resolve()

df = pd.read_csv(DATA_PATH.joinpath('US_GAAP_ACC_Numbers.csv'))


# Create starting list of company names
company = df[['company']]
company.columns = ['1']
company = company['1'].unique()

company_list = []
for comp in company:
    string = str(comp)
    company_list.append(string)
    
company = company_list
company.sort()
company_search_options1 = [{'label': comp, 'value': comp} for comp in company]


# Create starting list of financial statement accounts applicable to current set value
accounts = df.loc[(df['company'] == 'Apple Inc.')]
accounts = accounts[['field']]
accounts.columns = ['2']
accounts = accounts['2'].unique()

account_list = []
for account in accounts:
    string = str(account)
    account_list.append(string)
    
accounts = account_list
accounts.sort()
accounts_search_options2 = [{'label': account, 'value': account} for account in accounts]
value = accounts_search_options2[0]
value = value['value']


######################################################################################################################
# NEW BLOCK - App layout
######################################################################################################################

# App layout
layout = html.Div([

    # Dynamic header by company
    html.Div([

        html.H2(
            id = 'header',
            style = {
                'padding-top': 50,
                'padding':10,
                'margin':0,
                'font-family':'Arial, Helvetica, sans-serif',
                'textAlign':'center'
            }
        )
    ]),

    # Compnay dropdown menu
    html.Div([

        dbc.Row([

            dbc.Col(

                html.H5(
                    'Choose a Company',
                    style = {'textAlign':'center'}
                )
            ),
            
            dbc.Col(

                html.H5(
                    'Choose an Account',
                    style = {'textAlign':'center'}
                )
            )
        ]),
        
        dbc.Row([

            dbc.Col(

                dcc.Dropdown(
                    id = 'company',
                    options = company_search_options1,
                    value = 'Apple Inc.',
                    style = {
                        'border-color': 'black',
                        'font-size':'90%'
                    },
                    persistence = True
                )
            ),
            
            # Account dropdown menu
            dbc.Col(
                dcc.Dropdown(
                    id = 'account',
                    optionHeight = 55,
                    options = accounts_search_options2,
                    value = value,
                    style = {
                        'border-color': 'black',
                        'font-size':'90%'
                    },
                    persistence = True
                )
            )
        ])
    ],
        
        style = {
            'font-family':'Arial, Helvetica, sans-serif',
            'padding-top':10,
            'padding-right':'5%',
            'padding-left':'5%',
            'textAlign':'left'
        }
    ),
    
    # Live market price for company stock
    html.Div([

        html.H6(
            'Market Price:',
            style = {
                'display':'inline-block',
                'padding-left':20,
                'padding-top':10
            }
        ),
        
        html.H6(
            id = 'price',
            style = {
                'display':'inline-block',
                'padding-left':10
            }
        ),
        
        # Live market price to earnings of company stock
        html.H6(
            'Price To Earnings:',
            style = {
                'display':'inline-block',
                'padding-left':40,
                'padding-top':10
            }
        ),
        
        html.H6(
            id = 'pe',
            style = {
                'display':'inline-block',
                'padding-left':10
            }
        ),
        
        # Current earnings per share of company stock in $
        html.H6(
            'TTM Earnings Per Share:',
            style = {
                'display':'inline-block',
                'padding-left':40,
                'padding-top':10
            }
        ),
        
        html.H6(
            id = 'eps',
            style = {
                'display':'inline-block',
                'padding-left':10
            }
        ),
        
        # Current earnings per share of company stock %
        html.H6(
            'TTM Earnings Per Share:',
            style = {
                'display':'inline-block',
                'padding-left':40,
                'padding-top':10
            }
        ),
        
        html.H6(
            id = 'eps%',
            style = {
                'display':'inline-block',
                'padding-left':10
            }
        )
    ],
        
        style = {
            'font-family':'Arial, Helvetica, sans-serif',
            'padding-top':30,
            'textAlign':'center'
        }
    ),
    
    # Divider
    html.Hr(
        style = {
            'padding-bottom' : 20,
            'borderColor': 'black',
            'width' : '90%'
        }
    ),
    
    # Historical data for chosen field
    html.Div([

        dbc.Row([

            dbc.Col(

                dbc.Card(

                    dcc.Graph(id = 'scat1'), 
                    body = True, 
                    color = "dark", 
                    outline = True,
                    style = {'height':'37.5vh'}
                ),
                
                width = {
                    "size": 8,
                    "order": 1
                }
            ),
            
            # Calculator for compound rate of return
            dbc.Col(

                dbc.Card(

                    html.Div([

                        html.H5(
                            'Compound Rate of Return Calculator',
                            style = {
                                'padding-bottom': 10,
                                'padding-top': 10,
                                'font-family':'Arial, Helvetica, sans-serif'
                            }
                        ),
                        
                        # Input1
                        dbc.Row([

                            dbc.Input(
                                id = "input1",
                                placeholder = "Present Value, e.g., 1000",
                                type = "number",
                                persistence = True
                            )
                        ],
                            style = {
                                'padding-bottom': 5,
                                'padding-left': 10,
                                'padding-right': 10
                            }
                        ),
                        
                        # Input2
                        dbc.Row([

                            dbc.Input(
                                id = "input2",
                                placeholder = "Future Value, e.g., 2000",
                                type = "number",
                                persistence = True
                            )
                        ],
                            
                            style = {
                                'padding-bottom': 5,
                                'padding-left': 10,
                                'padding-right': 10
                            }
                        ),
                        
                        # Input3
                        dbc.Row([

                            dbc.Input(
                                id = "input3",
                                placeholder = "Years, e.g., 10",
                                type = "number",
                                persistence = True
                            )
                        ],
                            
                            style = {
                                'padding-bottom': 5,
                                'padding-left': 10,
                                'padding-right': 10
                            }
                        ),
                        
                        # Submit button
                        dbc.Row([

                            dbc.Button(
                                'Submit',
                                id = 'submit-val',
                                style = {'font-family':'Arial, Helvetica, sans-serif'}
                            ), 
                        ], 
                            className = 'd-grid gap-2 d-md-block',
                            style = {
                                'padding-top': 10,
                                'padding-left': 10,
                                'padding-right': 10
                            }
                        ),
                        
                        # Output
                        dbc.Row([

                            html.Label(
                                'Compounded Rate of Return:'
                            ),
                            html.Div(
                                id = 'output',
                                style = {
                                    'padding-left': 10
                                }
                            )
                        ],
                            
                            style = {
                                'padding-top': 10,
                                'padding-left': 10,
                                'padding-right': 10
                            }
                        )
                    ]),
                    
                    body = True,
                    color = "dark",
                    outline = True
                ),
                
                width = {
                    "size": 4,
                    "order": 2
                }
            )
        ])
    ],
        style = {
            'padding-left': 20,
            'padding-right': 20,
            'padding-top': 20,
            'padding-bottom': 30
        }
    ),
    
    # Account summary
    html.Div([

        html.H2(
            'Account Summary',
            style = {
                'padding':10,
                'padding-top':10,
                'margin':0,
                'font-family':'Arial, Helvetica, sans-serif',
                'background':'#00008B',
                'color':'#FFFFFF',
                'textAlign':'center'
            }
        ),
        
        html.Div(
            id = 'account_summary',
            style = {
                'padding':30,
                'font-family':'Arial, Helvetica, sans-serif',
                'line-height':30,
                'textAlign':'center',
                'fontSize':20
            }
        )
    ]),
    
    # Company summary
    html.Div([

        html.H2(
            'Company Summary',
            style = {
                'padding':10,
                'padding-top':10,
                'margin':0,
                'font-family':'Arial, Helvetica, sans-serif',
                'background':'#00008B',
                'color':'#FFFFFF',
                'textAlign':'center'
            }
        ),
        
        html.Div(
            id = 'company_summary',
            style = {
                'padding':30,
                'font-family':'Arial, Helvetica, sans-serif',
                'line-height':30,
                'textAlign':'center',
                'fontSize':20
            }
        )
    ]),
],
    style = {
        'margin':0
    }
)


######################################################################################################################
# NEW BLOCK - App callbacks
######################################################################################################################

# App function for dropdown menu
@app.callback(
    Output('account','options'),
    Output('account','value'),
    Input('company','value')
)

def field_dropdown(company):

    # Account per company
    accounts = df.copy()
    accounts = accounts.loc[(accounts['company'] == company)]
    accounts = accounts['field'].unique()

    new_accounts = []
    for account in accounts:
        string = str(account)
        new_accounts.append(string)
        
    accounts = new_accounts
    accounts.sort()
    accounts_search_options2 = [{'label': account, 'value': account} for account in accounts]
    value = accounts_search_options2[0]
    value = value['value']
    
    return accounts_search_options2, value
        

# Header update function
@app.callback(
    Output('header','children'),
    Input('company','value')
)

def name(company):
    
    header =  f"{company}"

    return header


# Graphics funtion
@app.callback(
    Output('scat1','figure'),
    Input('company','value'),
    Input('account','value')
)

def graphs(company, account):
    
    account_vis = df.copy()
    account_vis = account_vis.loc[
        (account_vis['company'] == company) & 
        (account_vis['field'] == account)
    ]
    
    account_vis = account_vis.reset_index(drop = True)
    
    account_vis['fy'] = account_vis['fy'].astype(int)
    account_vis['fy'] = account_vis['fy'].astype(str)
    X = account_vis['fy']
    y = round(account_vis['val'], 2)

    # Make vis dynamic to show point with only 1 data point and not line
    if len(y) <= 1:
        mode = 'lines+markers'

    else:
        mode = 'lines'
        
    # Create vis
    data1 = go.Figure(
        data = go.Scatter(
            x = X,
            y = y,
            mode = mode,
            marker = {
                'size':12,'line':{
                    'width':2,
                    'color':'DarkSlateGrey'
                },
                'color':'#00008B'
            },
            name = 'Shares Outstanding'
        ),

        layout = go.Layout(
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            font = {'color': '#111111'},
            height = 260
        )
    )

    # Set title
    data1.update_layout(
        title = str(company) + "'s <br>" + str(account) + ' Over Years',
        title_font_family = 'Arial, Helvetica, sans-serif',
        title_font_size = 16, 
        title_font_color = 'Black', 
        title_x = 0.5
    )

    return data1


# Graphics funtion
@app.callback(
    Output('account_summary','children'),
    Input('company','value'),
    Input('account','value')
)

def graphs(company, account):
    
    account_summary = df.copy()
    account_summary = account_summary.loc[
        (account_summary['company'] == company) & 
        (account_summary['field'] == account)
    ]
    
    account_summary = account_summary.reset_index(drop = True)
    account_summary = account_summary['description'].unique()[0]
    
    return account_summary


# Compound rate of return function
@app.callback(
    Output('output', 'children'),
    Input('submit-val', 'n_clicks'),
    State('input1', 'value'),
    State('input2', 'value'),
    State('input3', 'value')
)

def compute(n_clicks, input1, input2, input3):
    
    # Set default input values
    if input1 == None:
        input1 = 1
    if input2 == None:
        input2 = 1
    if input3 == None:
        input3 = 1
    
    # Compound rate of return solution
    solution = npf.rate(
        nper = float(input3), 
        pmt = 0, 
        pv = float(input1) * -1, 
        fv = float(input2)
    )
    
    solution = round(solution, 2) * 100

    return '{}%'.format(solution)


# Live stock data function
@app.callback(
    Output('price','children'),
    Output('pe','children'),
    Output('eps','children'),
    Output('eps%','children'),
    Output('company_summary','children'),
    Input('company','value')
    )

def stock_data(company):

    ticker_df = df.copy()
    ticker_df = ticker_df.loc[ticker_df['company'] == company]
    ticker_df = ticker_df.reset_index(drop = True)
    ticker = ticker_df.loc[0, 'ticker']

    # Establish web-scraper
    url = f'https://www.marketwatch.com/investing/stock/{ticker}/profile'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Scrape live stock prices
    ###########################################################################
    price = soup.select('.intraday__data > h2')
    price = [x.get_text().strip() for x in price]
    price = price[0]
    price = re.sub('[^a-zA-Z0-9.-]+', ' ', price)
    price = price.replace(" ", "")

    # Debug
    if price == 'N/A':
        price = '-'
    else:
        price = price

    # Scarpe live pe stock data
    ###########################################################################
    pe = soup.select('.group > .element > table > tbody > tr > td')
    pe = [x.get_text().strip() for x in pe]
    pe = pe[1]

    # Debug
    if pe == 'N/A':
        pe = '-'
    else:
        pe = pe

    # Debug
    try:
        eps = round(float(price) / float(pe), 2)
    except (ZeroDivisionError, ValueError):
        eps = '-'

    # Debug
    try:
        eps_percent = round(float(eps) / float(price), 2) * 100
    except (ZeroDivisionError, ValueError):
        eps_percent = '-'

    # Scrape company summary
    ###########################################################################
    summary = soup.select('.column > div > p')
    summary = [x.get_text().strip() for x in summary]
    summary = summary[0]

    # Debug
    if summary == '':
        summary = '-'
    else:
        summary = summary

    return f'${price}', pe, f'${eps}', f'{eps_percent}%', summary
    