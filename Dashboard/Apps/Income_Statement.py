from dash import html, dash_table, Input, Output
from App import app
import pandas as pd


# place_holder_df = pd.DataFrame([{'Account': '-', 'Year': '-'}])
# data = place_holder_df.to_dict('records')
# columns = [{'id': c, 'name': c} for c in place_holder_df.columns]

df = pd.read_csv('https://archive.org/download/us-financial-statements/US_Financial_Statements.csv')

layout = html.Div([
    
    # Table header
    html.Div([

        html.H2(
            'Income Statement',
            style = {
                'padding':10,
                'padding-top':10,
                'margin-top':50,
                'font-family':'Arial, Helvetica, sans-serif',
                # 'background':'#00008B',
                # 'color':'#FFFFFF',
                'textAlign':'left'
            }
        ),
        
        html.Div(id = 'income_statement')
    ]),
])

# Pull 
@app.callback(
    Output('income_statement','children'),
    Input('filtered_data', 'data')
)

def balance_sheet(jsonified_cleaned_data):
    
    # Get filtered data
    filtered_data = pd.read_json(jsonified_cleaned_data, orient = 'split')
    ticker = filtered_data['ticker'].unique()[0]
    
    # Filter for ticker
    table = df.copy()
    table = table.loc[
        (table['ticker'] == ticker) & 
        (table['financial_statement_type'] == 'Income Statement')
    ]
    
    # Pivot table
    table = table.pivot(
        index = ['financial_statement_type','financial_accounts','ticker'], 
        columns = ['date'],
        values = ['financial_values']
    )
    
    # Rename columns to remove multi-index column names
    table = table.reset_index()

    table.columns = [
        'financial_statement_type',
        'Account',
        'ticker',
        '2018',
        '2019',
        '2020',
        '2021'
    ]
    
    # Select columns
    table = table[[
        'Account',
        '2018',
        '2019',
        '2020',
        '2021'
    ]]
    
    # Reset index
    table = table.set_index(['Account'])

    # Reindex rows
    table = table.reindex([
        'Total Revenue',
        'Cost Of Revenue',
        'Gross Profit',
        '',
        'Other Operating Expenses',
        'Selling General Administrative',
        'Research Development',
        'Total Operating Expenses',    
        'Operating Income',
        '',
        'Interest Expense', 
        'Total Other Income Expense Net',
        '',
        'Income Before Tax',
        'Income Tax Expense',
        '',
        'Net Income From Continuing Ops',
        'Discontinued Operations',
        '',
        'Minority Interest',
        '',
        'Net Income',
        'Net Income Applicable To Common Shares',
        '',
        'Ebit',
        'Effect Of Accounting Charges',
        'Extraordinary Items',
        'Non Recurring',
        'Other Items'
    ])
    
    table = table.fillna('').reset_index()
    
    # Return table
    return html.Div([
        dash_table.DataTable(
            data = table.to_dict('records'),
            columns = [{'id': c, 'name': c} for c in table.columns],
            style_cell_conditional = [{'if': {'column_id': c},'textAlign': 'left'} for c in ['Account']],
            style_cell = {'font-family':'Arial, Helvetica, sans-serif'},
            style_as_list_view = True,
            style_header = {
                'font-family':'Arial, Helvetica, sans-serif',
                'font-size': 18,
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            }
        )
    ],
        
        style = {
            'padding-top': 10,
            'padding-left': 10,
            'padding-right': 15,
            'padding-bottom': 10,
        })

