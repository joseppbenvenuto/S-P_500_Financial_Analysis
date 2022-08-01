from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

import pandas as pd

# Connect to main app.py file
from App import app
from App import server

# Connect to your app pages
from Apps import Main_Page, Balance_Sheet, Income_Statement, Cash_Flow_Statement, Guru_Page, Instructions


######################################################################################################################
# NEW BLOCK - Pre app setup
######################################################################################################################

# # get relative data folder
# PATH = pathlib.Path(__file__).parent
# DATA_PATH = PATH.joinpath("../Data").resolve()
# df = pd.read_csv(DATA_PATH.joinpath('US_GAAP_ACC_Numbers.csv'))

# Import data
company_financials_df = pd.read_csv('https://archive.org/download/company-financials/Company_Financials.csv')
company_df = pd.read_csv('https://archive.org/download/companies_2022/Companies.csv')
financial_accounts_df = pd.read_csv('https://archive.org/download/financial-accounts/Financial_Accounts.csv')
financial_accounts_descriptions_df = pd.read_csv('https://archive.org/download/financial-accounts-descriptions/Financial_Accounts_Descriptions.csv')

df = company_financials_df.merge(
    company_df, 
    on = 'cik', 
    how = 'left'
)

df = df.merge(
    financial_accounts_df, 
    on = 'financial_acc_id', 
    how = 'left'
)

df = df.merge(
    financial_accounts_descriptions_df, 
    on = 'financial_acc_descriptions_id', 
    how = 'left'
)

df = df.drop(
    [
        'financial_acc_id',
        'financial_acc_descriptions_id',
        'company_financials_id', 
        'id_x', 
        'id_y'
    ],
    axis = 1,
    errors = 'ignore'
)

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

app.layout = html.Div([

    # Header by company
    html.Div([

        html.H2(
            'Financial Trends & Accounting for US Companies',
            style = {
                'padding':10,
                'margin':0,
                'font-family':'Arial, Helvetica, sans-serif',
                'background':'#00008B',
                'color':'#FFFFFF',
                'textAlign':'center'
            }
        )
    ]),
    
    dcc.Location(
        id = 'url', 
        refresh = False
    ),

    html.Div([

        dcc.Link(

            dbc.Button(
                'Click for Financial Visulization', 
                style = {
                    'font-family':'Arial, Helvetica, sans-serif', 
                    'margin-left':'110px', 
                    'margin-top':'18px', 
                    'margin-bottom':'5px'
                }
            ),
            href = '/apps/Main_Page', 
            refresh = False
        ),
        
        dcc.Link(
            
            dbc.Button(
                'Click for Balance Sheet',
                style = {
                    'font-family':'Arial, Helvetica, sans-serif', 
                    'margin-left':'15px', 
                    'margin-top':'18px', 
                    'margin-bottom':'5px'
                }
            ), 
            
            href = '/apps/Balance_Sheet', 
            refresh = False
        ),
        
        dcc.Link(
            
            dbc.Button(
                'Click for Income Statement',
                style = {
                    'font-family':'Arial, Helvetica, sans-serif', 
                    'margin-left':'15px', 
                    'margin-top':'18px', 
                    'margin-bottom':'5px'
                }
            ), 
            
            href = '/apps/Income_Statement', 
            refresh = False
        ),
        
        dcc.Link(
            
            dbc.Button(
                'Click for Cash-Flow Statement',
                style = {
                    'font-family':'Arial, Helvetica, sans-serif', 
                    'margin-left':'15px', 
                    'margin-top':'18px', 
                    'margin-bottom':'5px'
                }
            ), 
            
            href = '/apps/Cash_Flow_Statement', 
            refresh = False
        ),
        
        dcc.Link(
            
            dbc.Button(
                'Click for Guru Educational Videos',
                style = {
                    'font-family':'Arial, Helvetica, sans-serif', 
                    'margin-left':'15px', 
                    'margin-top':'18px', 
                    'margin-bottom':'5px'
                }
            ), 
            
            href = '/apps/Guru_Page', 
            refresh = False
        ),
        
        dcc.Link(

            dbc.Button(
                'Click for Application Instructions',
                style = {
                    'font-family':'Arial, Helvetica, sans-serif', 
                    'margin-left':'15px', 
                    'margin-top':'18px', 
                    'margin-bottom':'5px'
                }
            ), 
            href = '/apps/Instructions', 
            refresh = False
        ),
    
    ], 
        className = 'd-grid gap-2 d-md-block'
    
    ),    
    
    # Dynamic header by company
    html.Div([
        
        html.H2(
            id = 'header',
            style = {
                'padding-top': 40,
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
                # Company dropdown menu
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
    
    html.Div(
        id = 'page-content', 
        children = []
    ),
    
    # Stores filtered data
    dcc.Store(id = 'filtered_data', storage_type = 'session'),
    
    # Stores ticker data
    dcc.Store(id = 'ticker', storage_type = 'session')
])


######################################################################################################################
# NEW BLOCK - App callbacks
######################################################################################################################

# Multi-page functionality
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def display_page(pathname):
    if pathname == '/apps/Main_Page':
        return Main_Page.layout
    
    if pathname == '/apps/Balance_Sheet':
        return Balance_Sheet.layout
    
    if pathname == '/apps/Income_Statement':
        return Income_Statement.layout

    if pathname == '/apps/Cash_Flow_Statement':
        return Cash_Flow_Statement.layout
    
    if pathname == '/apps/Guru_Page':
        return Guru_Page.layout

    if pathname == '/apps/Instructions':
        return Instructions.layout
    
    else:
        return Main_Page.layout


# App function for dropdown menu and header
@app.callback(
    Output('account','options'),
    Output('account','value'),
    Output('header','children'),
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
    
    # Header
    header =  f"{company}"
    
    return accounts_search_options2, value, header


# Filter data to be used across the app
@app.callback(
    Output('filtered_data', 'data'),
    Output('ticker', 'data'),
    Input('company','value'),
    Input('account','value')
)

def filter_data(company, account):
    # Filter data
    filtered_data = df.copy()
    filtered_data = filtered_data.loc[
        (filtered_data['company'] == company) & 
        (filtered_data['field'] == account)
    ].reset_index(drop = True)
    
    ticker = filtered_data['ticker'].unique()[0]
    
    return filtered_data.to_json(date_format = 'iso', orient = 'split'), ticker


if __name__ == '__main__':
    app.run_server(debug = False)

    