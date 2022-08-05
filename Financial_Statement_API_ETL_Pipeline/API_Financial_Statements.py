import pandas  as pd
from urllib.request import urlopen
import certifi
import json
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


######################################################################################################################
# NEW BLOCK - Get financial data functions
######################################################################################################################

# https://site.financialmodelingprep.com/developer/docs/#Company-Financial-Statements
# Your API Key : 5975c43ac7d48e3ceeee1063fa8e3c30

# Get balance sheet
def get_balance_sheet_data(ticker, key):
    """
    - Gets 5 years of balance sheet data per ticker
    """
    url = (f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={key}")
    response = urlopen(url, cafile = certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

# get income statement
def get_income_statement_data(ticker, key):
    """
    - Gets 5 years of income statement data per ticker
    """
    url = (f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?apikey={key}")
    response = urlopen(url, cafile = certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

# Get cash-flow statement
def get_cash_flow_statement_data(ticker, key):
    """
    - Gets 5 years of cash-flow statement data per ticker
    """
    url = (f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={key}")
    response = urlopen(url, cafile = certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)


######################################################################################################################
# NEW BLOCK - Run data wrangling pipeline
######################################################################################################################

def parse_financial_api():
    """
    - Runs API pipeline
    - Transforms data
    - Exports data to data directory as a CSV
    """
    # Import S&P 500 Index companies
    #####################################################################################################
    tickers_df = pd.read_csv(
        r"C:\Users\jbenvenuto\Desktop\GitHub_Projects\S&P500_Index_Companies.csv",
        sep = ',',
        encoding = 'unicode_escape'
    )

    # Convert tickers to list
    tickers = tickers_df['ticker'].tolist()[0:2]
    companies = tickers_df['company'].tolist()[0:2]
    key = '5975c43ac7d48e3ceeee1063fa8e3c30'
    
    
    # Wrangle API
    #####################################################################################################    
    # Store parsed data
    balance_sheet_df_list = []
    income_statement_df_list = []
    cash_flow_statement_df_list = []

    for ticker, company in zip(tickers, companies):
        # Get balance sheet
        ###########################################
        balance_sheet = get_balance_sheet_data(
            ticker = ticker, 
            key = key
        )

        # Append df
        balance_sheet = pd.DataFrame(balance_sheet)
        
        balance_sheet = balance_sheet.drop(
            ['link','finalLink'], 
            axis = 1,
            errors = 'ignore'
        )
        
        balance_sheet['financialStatement'] = 'Balance Sheet'
        balance_sheet['company'] = company
        balance_sheet_df_list.append(balance_sheet)
        
        print(' '.join(['Completed balance sheet', str(ticker)]))

        # get income statement
        ###########################################
        income_statement = get_income_statement_data(
            ticker = ticker, 
            key = key
        )

        # Append df
        income_statement = pd.DataFrame(income_statement)
        
        income_statement = income_statement.drop(
            ['link','finalLink'], 
            axis = 1,
            errors = 'ignore'
        )
        
        income_statement['financialStatement'] = 'Income Statement'
        income_statement['company'] = company
        income_statement_df_list.append(income_statement)
        
        print(' '.join(['Completed income statement', str(ticker)]))

        # Get cash-flow statement
        ###########################################
        cash_flow_statement = get_cash_flow_statement_data(
            ticker = ticker, 
            key = key
        )

        # Append df
        cash_flow_statement = pd.DataFrame(cash_flow_statement)
        
        cash_flow_statement = cash_flow_statement.drop(
            ['link','finalLink'], 
            axis = 1,
            errors = 'ignore'
        )
            
        cash_flow_statement['financialStatement'] = 'Cash-Flow Statement'
        cash_flow_statement['company'] = company
        cash_flow_statement_df_list.append(cash_flow_statement)
        
        print(' '.join(['Completed cash-flow statement', str(ticker)]))

        
    # Concat all data per list
    ##################################################################################################### 
    balance_sheet_df = pd.concat(balance_sheet_df_list, axis = 0)
    income_statement_df = pd.concat(income_statement_df_list, axis = 0)
    cash_flow_statement_df = pd.concat(cash_flow_statement_df_list, axis = 0)
    
    
    # Unpivot data to long form
    ##################################################################################################### 
    # Balance sheet
    balance_sheet_df = pd.melt(
                balance_sheet_df,
                
                id_vars = [
                    'date',
                    'symbol',
                    'reportedCurrency',
                    'cik',
                    'fillingDate',
                    'acceptedDate',
                    'calendarYear',
                    'period',
                    'financialStatement',
                    'company'
                ], 
                
                value_vars = balance_sheet_df.columns[7:-1],
                var_name = 'financialAccounts', 
                value_name = 'financialValues'
            )

    # adjust account string to proper
    balance_sheet_df['financialAccounts'] = balance_sheet_df['financialAccounts'].str.replace( r"([A-Z])", r" \1").str.strip().str.title()
    
    # Income statement
    income_statement_df = pd.melt(
                income_statement_df,
                
                id_vars = [
                    'date',
                    'symbol',
                    'reportedCurrency',
                    'cik',
                    'fillingDate',
                    'acceptedDate',
                    'calendarYear',
                    'period',
                    'financialStatement',
                    'company'
                ], 
                
                value_vars = income_statement_df.columns[7:-1],
                var_name = 'financialAccounts', 
                value_name = 'financialValues'
            )

    # adjust account string to proper
    income_statement_df['financialAccounts'] = income_statement_df['financialAccounts'].str.replace( r"([A-Z])", r" \1").str.strip().str.title()
    
    # Cash-flow statement
    cash_flow_statement_df = pd.melt(
                cash_flow_statement_df,
                
                id_vars = [
                    'date',
                    'symbol',
                    'reportedCurrency',
                    'cik',
                    'fillingDate',
                    'acceptedDate',
                    'calendarYear',
                    'period',
                    'financialStatement',
                    'company'
                ], 
                
                value_vars = cash_flow_statement_df.columns[7:-1],
                var_name = 'financialAccounts', 
                value_name = 'financialValues'
            )

    # adjust account string to proper
    cash_flow_statement_df['financialAccounts'] = cash_flow_statement_df['financialAccounts'].str.replace( r"([A-Z])", r" \1").str.strip().str.title()
    
    # Concat all data to one data frame
    #####################################################################################################     
    df = pd.concat([balance_sheet_df, income_statement_df], axis = 0)
    df = pd.concat([df, cash_flow_statement_df], axis = 0)
    
    # rename columns
    df .columns = [
        'date', 
        'ticker', 
        'reported_currency', 
        'cik', 
        'filling_date',
        'accepted_date', 
        'calendar_year', 
        'period', 
        'financial_statement',
        'company',
        'financial_accounts',
        'financial_values'
    ]
    
    # reorder columns to match view
    df = df[[
        'cik',
        'company',
        'ticker',
        'financial_accounts',
        'financial_statement',
        'date',
        'filling_date',
        'accepted_date',
        'calendar_year',
        'financial_values'
    ]]
    

    # Export data
    ##################################################################################################### 
    df.to_csv(
        'Data/Financial_Statement_Data.csv', 
        index = False, 
        encoding = 'utf8'
    )  
    
    print('Program complete')

if __name__ == '__main__':
    parse_financial_api()
    
    