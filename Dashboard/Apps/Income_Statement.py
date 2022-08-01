from dash import html, dash_table, Input, Output
from App import app
import pandas as pd
import yahoo_fin.stock_info as si
from datetime import date


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
    
    try:
        # Income statement
        table = si.get_income_statement(ticker)
        table = table[table.columns[::-1]]
        col_names = table.columns.astype(str)
        table = table.reset_index()
        table.columns = ['Breakdown'] + list(col_names)
        table['Breakdown'] = table['Breakdown'].str.replace( r"([A-Z])", r" \1").str.strip().str.title()

        # Melt data to fit table and adjust for future data
        table = pd.melt(
            table,
            id_vars = 'Breakdown', 
            value_vars = table.columns[1:5],
            var_name = 'date', 
            value_name = 'financial_values'
        )
        
        table['financial_values'] = table['financial_values'].fillna(0)
        table['financial_values'] = table['financial_values'].astype(int)
        table['financial_values'] = table.apply(lambda x: "{:,}".format(x['financial_values']), axis = 1)
        table['date'] = table['date'].str.split('-').str[0]

        # Pivot table
        table = table.pivot(
            index = 'Breakdown', 
            columns = 'date',
            values = 'financial_values'
        )

        # Rename columns to remove multi-index column names
        table = table.reset_index()

        table = table.rename(columns = {'Breakdown': 'Account'})
        
        # Reset index
        table = table.set_index(['Account'])

        # Reindex rows
        table = table.reindex([
            'Total Revenue',
            'Cost Of Revenue',
            'Gross Profit',
            'Other Operating Expenses',
            'Selling General Administrative',
            'Research Development',
            'Total Operating Expenses',    
            'Operating Income',
            'Interest Expense', 
            'Total Other Income Expense Net',
            'Income Before Tax',
            'Income Tax Expense',
            'Net Income From Continuing Ops',
            'Discontinued Operations',
            'Minority Interest',
            'Net Income',
            'Net Income Applicable To Common Shares',
            'Ebit',
            'Effect Of Accounting Charges',
            'Extraordinary Items',
            'Non Recurring',
            'Other Items'
        ])

        table = table.fillna(0)

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

    except:

        table = pd.DataFrame([{
            'Account': '-',
            str(date.today().year - 4): '-',
            str(date.today().year - 3): '-',
            str(date.today().year - 2): '-',
            str(date.today().year - 1): '-'
        }])
    
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

