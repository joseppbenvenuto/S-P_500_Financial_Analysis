import pandas as pd
import numpy as np
import yahoo_fin.stock_info as si
import re
import base64
import psycopg2 as ps
from io import StringIO
import warnings
warnings.filterwarnings("ignore")


######################################################################################################################
# NEW BLOCK - Insert yahoo data to yahoodb
######################################################################################################################

# Insering balance sheet data
#########################################################################
def insert_balance_sheet_data(balance_sheet, conn, cur):
    '''
    - Inserts balance sheet data into the balance_sheet table in yahoodb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(balance_sheet.to_csv(
            index = None,
            header = None,
            sep = '|'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'balance_sheet',
            columns = balance_sheet.columns,
            sep = '|'
            )
            
        conn.commit()

        print('Balance Sheet data inserted in bulk to yahoodb successfully 1.')
        print(' '.join(['Rows inserted:', str(balance_sheet.shape[0])]))

    except ps.Error as e:
        print('Insert Balance Sheet data error:')
        print(e)

        
# Insering income statement data
#########################################################################
def insert_income_statement_data(income_statement, conn, cur):
    '''
    - Inserts income statement data into the income_statement table in yahoodb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(income_statement.to_csv(
            index = None,
            header = None,
            sep = '|'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'income_statement',
            columns = income_statement.columns,
            sep = '|'
            )
            
        conn.commit()

        print('Income Statement data inserted in bulk to yahoodb successfully 1.')
        print(' '.join(['Rows inserted:', str(income_statement.shape[0])]))

    except ps.Error as e:
        print('Insert Income Statement data error:')
        print(e)

        
# Insering cash-flow statement data
#########################################################################
def insert_cash_flow_statement_data(cash_flow_statement, conn, cur):
    '''
    - Inserts income statement data into the income_statement table in yahoodb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(cash_flow_statement.to_csv(
            index = None,
            header = None,
            sep = '|'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'cash_flow_statement',
            columns = cash_flow_statement.columns,
            sep = '|'
            )
            
        conn.commit()

        print('Cash-Flow Statement data inserted in bulk to yahoodb successfully 1.')
        print(' '.join(['Rows inserted:', str(cash_flow_statement.shape[0])]))

    except ps.Error as e:
        print('Insert Cash-Flow Statement data error:')
        print(e)


######################################################################################################################
# NEW BLOCK - Get Yahoo Finance data through API
######################################################################################################################

def get_yahoo_financial_statements(ticker_file, conn, cur):
    '''
    - Gets company financial data and inserts them into their yahoodb tables
    '''
    # Get tickers
    tickers_df = pd.read_csv(ticker_file, sep = '|')
    tickers_list = list(tickers_df['ticker'].unique())
    
    # Print length of company list
    print(' '.join(['Number of companies in loop:', str(len(tickers_list))]))
    
    count = 0
    for ticker in tickers_list:
        # Print number of passed companies
        count += 1
        print(' '.join(['Company count:', str(count)]))
        
        # Get yahoo finance data
        try:
            # Balance Sheet
            #########################################################################
            balance_sheet = si.get_balance_sheet(ticker)
            balance_sheet = balance_sheet[balance_sheet.columns[::-1]]
            col_names = balance_sheet.columns.astype(str)
            balance_sheet = balance_sheet.reset_index()
            balance_sheet.columns = ['Breakdown'] + list(col_names)
            balance_sheet['Breakdown'] = balance_sheet['Breakdown'].str.replace( r"([A-Z])", r" \1").str.strip().str.title()
            balance_sheet = balance_sheet.fillna(0)                
            balance_sheet['financial_statement_type'] = 'Balance Sheet'
            balance_sheet['ticker'] = ticker
            
            # Melt data to fit table and adjust for future data
            balance_sheet = pd.melt(
                balance_sheet,
                
                id_vars = [
                    'Breakdown', 
                    'financial_statement_type',
                    'ticker'
                ], 
                
                value_vars = balance_sheet.columns[1:5],
                var_name = 'date', 
                value_name = 'financial_values'
            )

            balance_sheet.columns = [
                'financial_accounts',
                'financial_statement_type',
                'ticker', 
                'date',
                'financial_values'
            ]

            # Reorder columns
            balance_sheet = balance_sheet[[
                'financial_statement_type',
                'financial_accounts',
                'date',
                'financial_values',
                'ticker'
            ]]
            
            balance_sheet['financial_values'] = balance_sheet['financial_values'].astype(int)
            balance_sheet['financial_values'] = balance_sheet.apply(lambda x: "{:,}".format(x['financial_values']), axis = 1)
            balance_sheet['date'] = balance_sheet['date'].str.split('-').str[0]
            
            # Insert balance sheet data to table
            insert_balance_sheet_data(
                balance_sheet = balance_sheet, 
                conn = conn, 
                cur = cur
            )
            
            print(' '.join(['Inserted balance sheet data for', str(ticker)]))

            
            # Income Statement
            #########################################################################
            income_statement = si.get_income_statement(ticker)
            income_statement = income_statement[income_statement.columns[::-1]]
            col_names = income_statement.columns.astype(str)
            income_statement = income_statement.reset_index()
            income_statement.columns = ['Breakdown'] + list(col_names)
            income_statement['Breakdown'] = income_statement['Breakdown'].str.replace( r"([A-Z])", r" \1").str.strip().str.title()
            income_statement = income_statement.fillna(0)
            income_statement['financial_statement_type'] = 'Income Statement'
            income_statement['ticker'] = ticker
            
            # Melt data to fit table and adjust for future data
            income_statement = pd.melt(
                income_statement,
                
                id_vars = [
                    'Breakdown',
                    'financial_statement_type', 
                    'ticker'
                ], 
                
                value_vars = income_statement.columns[1:5],
                var_name = 'date', 
                value_name = 'financial_values'
            )
    
            income_statement.columns = [
                'financial_accounts',
                'financial_statement_type',
                'ticker', 
                'date',
                'financial_values'
            ]

            # Reorder columns
            income_statement = income_statement[[
                'financial_statement_type',
                'financial_accounts',
                'date',
                'financial_values',
                'ticker'
            ]]
            
            income_statement['financial_values'] = income_statement['financial_values'].astype(int)
            income_statement['financial_values'] = income_statement.apply(lambda x: "{:,}".format(x['financial_values']), axis = 1)
            income_statement['date'] = income_statement['date'].str.split('-').str[0]
            
            # Insert income statement data to table
            insert_income_statement_data(
                income_statement = income_statement, 
                conn = conn, 
                cur = cur
            )
            
            print(' '.join(['Inserted income statement data for', str(ticker)]))

            
            # Cash-Flow Statement
            #########################################################################
            cash_flow_statement = si.get_cash_flow(ticker)
            cash_flow_statement = cash_flow_statement[cash_flow_statement.columns[::-1]]
            col_names = cash_flow_statement.columns.astype(str)
            cash_flow_statement = cash_flow_statement.reset_index()
            cash_flow_statement.columns = ['Breakdown'] + list(col_names)
            cash_flow_statement['Breakdown'] = cash_flow_statement['Breakdown'].str.replace( r"([A-Z])", r" \1").str.strip().str.title()
            cash_flow_statement = cash_flow_statement.fillna(0)
            cash_flow_statement['financial_statement_type'] = 'Cash-Flow Statement'
            cash_flow_statement['ticker'] = ticker 
            
            # Melt data to fit table and adjust for future data
            cash_flow_statement = pd.melt(
                cash_flow_statement,
                
                id_vars = [
                    'Breakdown', 
                    'financial_statement_type', 
                    'ticker'
                ], 
                
                value_vars = cash_flow_statement.columns[1:5],
                var_name = 'date', 
                value_name = 'financial_values'
            )
    
            cash_flow_statement.columns = [
                'financial_accounts',
                'financial_statement_type',
                'ticker', 
                'date',
                'financial_values'
            ]

            # Reorder columns
            cash_flow_statement = cash_flow_statement[[
                'financial_statement_type',
                'financial_accounts',
                'date',
                'financial_values',
                'ticker'
            ]]
            
            cash_flow_statement['financial_values'] = cash_flow_statement['financial_values'].astype(int)
            cash_flow_statement['financial_values'] = cash_flow_statement.apply(lambda x: "{:,}".format(x['financial_values']), axis = 1)
            cash_flow_statement['date'] = cash_flow_statement['date'].str.split('-').str[0]
            
            # Insert cash-flow statement data to table
            insert_cash_flow_statement_data(
                cash_flow_statement = cash_flow_statement, 
                conn = conn, 
                cur = cur
            )
            
            print(' '.join(['Inserted cash-flow statement data for', str(ticker)]))
            
        except:
            pass

        
######################################################################################################################
# NEW BLOCK - Run yahoo finance etl pipeline
######################################################################################################################

# Run etl pipline
def run_yahoo_finance_etl_pipeline():
    '''
    - Runs yahoo finance etl pipeline
    '''
    # Connect to database
    #########################################################################
    try:
        conn = ps.connect('''

            host=localhost
            dbname=yahoodb
            user=postgres
            password=iEchu133

        ''')

        cur = conn.cursor()

        print('Successfully connected to yahoodb')

    except ps.Error as e:
        print('\n Database Error:')
        print(e)


    # Get and insert yahoo finance data   
    #########################################################################
    get_yahoo_financial_statements(
        ticker_file = r'C:\Users\jbenvenuto\Desktop\GitHub_Projects\company_tickers.csv', 
        conn = conn, 
        cur = cur
    )
    
    print('Program complete')


if __name__ == '__main__':
    run_yahoo_finance_etl_pipeline()