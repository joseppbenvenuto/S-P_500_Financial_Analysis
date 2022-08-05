import pandas as pd
import numpy as np

from io import StringIO
import psycopg2 as ps
from SQL_Queries_Financial_Statements import *

import warnings
warnings.filterwarnings("ignore", category = DeprecationWarning) 

import os
import glob
import shutil
import datetime


######################################################################################################################
# NEW BLOCK - Preprocess data
######################################################################################################################

def process_financial_statement_data(df, cur):
    '''
    - Processes data to insert into PostgreSQL
    - Give unique ids to split data into second normal form
    - Create separate tables
    '''
    # Concat old old data with new from financial_statement_view
    # Query financial_statement_view
    query = '''

        SELECT *
        FROM financial_statement_view;

    '''

    cur.execute(query)
    financial_statement_view_df = cur.fetchall()

    financial_statement_view_columns = [
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
    ]


    # Convert view to pandas data frame
    financial_statement_view_df = pd.DataFrame(financial_statement_view_df, columns = financial_statement_view_columns)
    df = pd.concat([df, financial_statement_view_df], axis = 0)
    df = df.drop_duplicates(keep = 'first').reset_index(drop = True)
    
    
    # Create ids
    df['company_id'] = df.groupby(['ticker','company']).ngroup()
    df['financial_accounts_id'] = df.groupby(['financial_accounts']).ngroup()
    df['financial_statement_id'] = df.groupby(['financial_statement']).ngroup()
    df['time_id'] = df.groupby(['date','filling_date','accepted_date','calendar_year']).ngroup()
    
    
    # Create tables
    fact_df = df.drop(
        
        [
            'ticker',
            'company',
            'cik',
            'financial_accounts',
            'financial_statement',
            'date',
            'filling_date',
            'accepted_date',
            'calendar_year',
            'reported_currency',
            'period'
        ], 
        
        axis = 1, 
        errors = 'ignore'
    )
    
    fact_df['financial_values'] = fact_df['financial_values'].astype(np.int64)
    print(' '.join(['Processed', str('company_financials')]))
    
    companies_df = df[['company_id','ticker','company','cik']]
    companies_df = companies_df.drop_duplicates(keep = 'first').reset_index(drop = True)
    print(' '.join(['Processed', str('companies')]))
    
    financialAccounts_df = df[['financial_accounts_id','financial_accounts']]
    financialAccounts_df = financialAccounts_df.drop_duplicates(keep = 'first').reset_index(drop = True)
    print(' '.join(['Processed', str('financial_accounts')]))
    
    financialStatement_df = df[['financial_statement_id','financial_statement']]
    financialStatement_df = financialStatement_df.drop_duplicates(keep = 'first').reset_index(drop = True)
    print(' '.join(['Processed', str('financial_statements')]))
    
    time_df = df[['time_id','date','filling_date','accepted_date','calendar_year']]
    time_df = time_df.drop_duplicates(keep = 'first').reset_index(drop = True)
    print(' '.join(['Processed', str('time')]))
    
    
    print('Processed full data')
    
    return companies_df, financialAccounts_df, financialStatement_df, fact_df, time_df


######################################################################################################################
# NEW BLOCK - Insert data into financialdb
######################################################################################################################

# Insert companies
#########################################################################
def insert_companies_data(companies_df, conn, cur):
    '''
    - Inserts data into the companies table in financialdb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Drop all date in current table
    cur.execute(companies_table_drop_rows)  
    conn.commit()
    
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(companies_df.to_csv(
            index = None,
            header = None,
            sep = '|'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'companies',
            columns = companies_df.columns,
            sep = '|'
            )
            
        conn.commit()

        print('Companies data inserted in bulk to financialdb successfully 1.')
        print(' '.join(['Rows inserted:', str(companies_df.shape[0])]))

    except ps.Error as e:
        print('Insert Companies data error:')
        print(e)
        
        
# Insert financial_accounts
#########################################################################
def insert_financial_accounts_data(financialAccounts_df, conn, cur):
    '''
    - Inserts data into the companies table in financialdb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Drop all date in current table
    cur.execute(financial_acc_table_drop_rows)  
    conn.commit()
    
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(financialAccounts_df.to_csv(
            index = None,
            header = None,
            sep = '|'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'financial_accounts',
            columns = financialAccounts_df.columns,
            sep = '|'
            )
            
        conn.commit()

        print('Financial Accounts data inserted in bulk to financialdb successfully 1.')
        print(' '.join(['Rows inserted:', str(financialAccounts_df.shape[0])]))

    except ps.Error as e:
        print('Insert Financial Accounts data error:')
        print(e)
 

 # Insert financial_statements
#########################################################################
def insert_financial_statements_data(financialStatement_df, conn, cur):
    '''
    - Inserts data into the companies table in financialdb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Drop all date in current table
    cur.execute(financial_statement_table_drop_rows)  
    conn.commit()
    
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(financialStatement_df.to_csv(
            index = None,
            header = None,
            sep = '|'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'financial_statements',
            columns = financialStatement_df.columns,
            sep = '|'
            )
            
        conn.commit()

        print('Financial Satatements data inserted in bulk to financialdb successfully 1.')
        print(' '.join(['Rows inserted:', str(financialStatement_df.shape[0])]))

    except ps.Error as e:
        print('Insert Financial Satatements data error:')
        print(e)    
        
        
# Insert company_financials
#########################################################################
def insert_company_financials_data(fact_df, conn, cur):
    '''
    - Inserts data into the companies table in financialdb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Drop all date in current table
    cur.execute(company_financials_table_drop_rows)  
    conn.commit()
    
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(fact_df.to_csv(
            index = None,
            header = None,
            sep = '|'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'company_financials',
            columns = fact_df.columns,
            sep = '|'
            )
            
        conn.commit()

        print('Company Financials data inserted in bulk to financialdb successfully 1.')
        print(' '.join(['Rows inserted:', str(fact_df.shape[0])]))

    except ps.Error as e:
        print('Insert Company Financials data error:')
        print(e)  
        
# Insert time
#########################################################################
def insert_times_data(time_df, conn, cur):
    '''
    - Inserts data into the companies table in financialdb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Drop all date in current table
    cur.execute(time_table_drop_rows)  
    conn.commit()
    
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(time_df.to_csv(
            index = None,
            header = None,
            sep = '|'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'time',
            columns = time_df.columns,
            sep = '|'
            )
            
        conn.commit()

        print('Time data inserted in bulk to financialdb successfully 1.')
        print(' '.join(['Rows inserted:', str(time_df.shape[0])]))

    except ps.Error as e:
        print('Insert Time data error:')
        print(e) 
        
        
######################################################################################################################
# NEW BLOCK - Run etl pipeline
######################################################################################################################

# Runs etl pipeline
def etl():
    """
    - Runs ETL pipeline
    - Transforms data
    - Inserts data into propper financialdb tables
    - Relocates processed CSV to storage folder
    """
    # Import api data
    #########################################################################    
    df = pd.read_csv('Data/Financial_Statement_Data.csv')
    
    
    # Connect to financialdb
    #########################################################################
    try:
        conn = ps.connect('''
        
            host=localhost
            dbname=financialdb
            user=postgres
            password=iEchu133
            
        ''')
        
        cur = conn.cursor()

        print('Successfully connected to financialdb')

    except ps.Error as e:
        print('\n Database Error:')
        print(e)
    
    
    # Preprocess and transforms data
    #########################################################################
    companies_df, financialAccounts_df, financialStatement_df, fact_df, time_df = process_financial_statement_data(df = df, cur = cur)
    
    
    # Insert data to financialdb
    #########################################################################
    # Insert company data
    insert_companies_data(
        companies_df = companies_df, 
        conn = conn, 
        cur = cur
    )
    
    # insert financial account data
    insert_financial_accounts_data(
        financialAccounts_df = financialAccounts_df, 
        conn = conn, 
        cur = cur
    )
    
    # Insert financial statements data
    insert_financial_statements_data(
        financialStatement_df = financialStatement_df, 
        conn = conn, 
        cur = cur
    )
    
    # Insert company financials data
    insert_company_financials_data(
        fact_df = fact_df, 
        conn = conn, 
        cur = cur
    )
    
    # insert time data
    insert_times_data(
        time_df = time_df, 
        conn = conn, 
        cur = cur
    )
    
    
    # Create export directory for all combined files
    #########################################################################
    try:
        # Import path
        print('Loading...')
        import_path = r'C:\**\S-P_500_Financial_Analysis\Financial_Statement_API_ETL_Pipeline\Data'
        import_path = glob.glob(import_path, recursive = True)
        import_path = import_path[0]
        
        # Get date
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Create folder with date as name
        os.makedirs(import_path + '\\' + date)

        # Get all files from import path that are CSV
        allfiles = os.listdir(import_path + '\\')
        allfiles = [file_name for file_name in allfiles if file_name.endswith('.csv')]

        for file in allfiles:
            shutil.move(import_path + '\\' + file, import_path + '\\' + date + '\\' + file)
            print(' '.join(['Stored data', str(file), 'to folder', str(date)]))

    except:
        pass
    
    
    print('Program complete')
    
    
if __name__ == '__main__':
    etl()
    
    