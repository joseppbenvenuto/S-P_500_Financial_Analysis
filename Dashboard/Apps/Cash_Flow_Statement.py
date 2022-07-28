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
            'Cash-Flow Statement',
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
        
        html.Div(id = 'cash_flow_statement')
    ]),
])

# Pull 
@app.callback(
    Output('cash_flow_statement','children'),
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
        (table['financial_statement_type'] == 'Cash-Flow Statement')
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
        'Net Income',
        'Depreciation',
        'Change To Account Receivables',
        'Change To Inventory',
        'Change To Operating Activities',
        'Total Cash From Operating Activities',
        '',
        'Investments',
        'Capital Expenditures',
        'Other Cashflows From Investing Activities',
        'Total Cashflows From Investing Activities',
        '',
        'Net Borrowings',
        'Dividends Paid'
        'Other Cashflows From Financing Activities',
        'Total Cash From Financing Activities',
        '',
        'Change In Cash',
        'Change To Netincome',
        'Efffect Of ExchangeRate'
    ])

    table = table.fillna('').reset_index()

    fcf_list = []
    for col in table.columns[1:]:
        totalCashFromOperatingActivities = int(table.iloc[5][col].replace(',',''))
        capitalExpenditures = int(table.iloc[8][col].replace(',',''))

        fcf = int(table.iloc[5][col].replace(',','')) + int(table.iloc[8][col].replace(',',''))

        fcf_dict = {
            'Account': 'Free Cash Flow',
            'Col': col,
            'Value': fcf
        }

        fcf_list.append(fcf_dict)

    fcf_df = pd.DataFrame(fcf_list)  

    fcf_df['Value'] = fcf_df.apply(lambda x: "{:,}".format(x['Value']), axis = 1)
    fcf_df = fcf_df.reset_index()

    fcf_df = fcf_df.pivot(
        index = ['index'], 
        columns = ['Col'],
        values = ['Value']
    )

    fcf_df = fcf_df.droplevel(level = 0, axis = 1)
    fcf_df = fcf_df.apply(lambda x: pd.Series(x.dropna().values))
    fcf_df['Account'] = 'Free Cash Flow'
    fcf_df = fcf_df[list([fcf_df.columns[-1]]) + list(fcf_df.columns[:-1])]

    table = pd.concat([table, fcf_df], axis = 0)
    
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

