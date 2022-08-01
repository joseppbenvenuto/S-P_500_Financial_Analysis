from dash import html, dash_table, Input, Output
from App import app
import pandas as pd
import yahoo_fin.stock_info as si
from datetime import date


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
    
    try:
        # Cash-Flow statement
        table = si.get_cash_flow(ticker)
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
            'Net Income',
            'Depreciation',
            'Change To Account Receivables',
            'Change To Inventory',
            'Change To Operating Activities',
            'Total Cash From Operating Activities',
            'Investments',
            'Capital Expenditures',
            'Other Cashflows From Investing Activities',
            'Total Cashflows From Investing Activities',
            'Net Borrowings',
            'Dividends Paid'
            'Other Cashflows From Financing Activities',
            'Total Cash From Financing Activities',
            'Change In Cash',
            'Change To Netincome',
            'Efffect Of ExchangeRate'
        ])

        table = table.fillna(0)

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
            try:
                totalCashFromOperatingActivities = int(table.iloc[5][col].replace(',',''))
            except:
                totalCashFromOperatingActivities = int(table.iloc[5][col])

            try:
                capitalExpenditures = int(table.iloc[8][col].replace(',',''))
            except:
                capitalExpenditures = int(table.iloc[8][col])

            fcf = totalCashFromOperatingActivities + capitalExpenditures

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

