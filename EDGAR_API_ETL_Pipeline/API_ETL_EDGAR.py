from zipfile import ZipFile
import zipfile
import json
import re

import pandas as pd
import numpy as np
from random import random

# For bulk data import
from io import StringIO
import psycopg2 as ps
from SQL_Queries_EDGAR import *

import warnings
warnings.filterwarnings('ignore')


######################################################################################################################
# NEW BLOCK - Get Files and File length
######################################################################################################################

# API Site: https://www.sec.gov/edgar/sec-api-documentation
def get_files_length(zip_file):
    '''
    - Get number of JSON files
    '''
    # Create a ZipFile Object and load sample.zip in it
    with ZipFile(zip_file, 'r') as zipObj:
        # Get list of files names in zip
        file_len = len(zipObj.namelist())
        
    return file_len


# API Site: https://www.sec.gov/edgar/sec-api-documentation
def get_zipped_files(zip_file, start_index, end_index):
    '''
    - Get list and length of selected JSON files by index
    '''
    # Create a ZipFile Object and load sample.zip in it
    with ZipFile(zip_file, 'r') as zipObj:
        # Get list of files names in zip
        listOfiles = zipObj.namelist()[start_index : end_index]
        file_len = len(listOfiles)
        print(' '.join (["Total files:", str(file_len)]))
        
    return listOfiles, file_len


######################################################################################################################
# NEW BLOCK - Parse and Retrieve All EDGAR Data
######################################################################################################################

def parse_edgar_json(zip_file, files_list):
    '''
    - Get a list of EDGAR data frames uncleaned
    '''
    zf = zipfile.ZipFile(zip_file) 
    file_index = 0
    df_list = []

    for file in files_list:
        try:
            with zf.open(files_list[file_index], 'r') as f:
                data = json.load(f)
                
                print(' '.join (["File:", str(file_index + 1)]))
                print(file)

                entity = data['entityName']
                
                # Clean CIK number
                cik = str(file).replace('.json','')
                cik = cik.replace('CIK','')
                cik = cik.lstrip('0')      
                
                print(' '.join(['Retrieved company name:', entity]))

                try:
                    data = data['facts']['us-gaap']
                    df = pd.DataFrame(data)
                    df = df.reset_index()
                    df = df.rename(columns = {'index': 'Types'})
                    df['Type'] = df['Types'] + '_' + entity
                    # Shift column 'Name' to first position
                    first_column = df.pop('Type')

                    # Insert column using insert(position,column_name,
                    # First_column) function
                    df.insert(0, 'Type', first_column)
                    
                    # Append a new row with specified columns and values
                    df = df.append(
                        {
                            'Type': entity,
                            'Types': 'company'
                        }, 
                        ignore_index = True
                    )
                    
                    df = df.append(
                        {
                            'Type' : cik,
                            'Types': 'cik'                            
                        }, 
                        ignore_index = True
                    )

                    df_list.append(df)
                    print('Retrieved stats')

                except:
                    pass
                
        except:
            pass
            
        file_index += 1
            
    return df_list


######################################################################################################################
# NEW BLOCK - Clean Retrived EDGAR Data
######################################################################################################################

def clean_edgar_data(df_list):
    '''
    - Clean full list of EDGAR data frame merge (union) on axis 0 to be used in the plotly & Dash dashboard
    '''
    try:
        df =  pd.concat(df_list, axis = 0)
        # Field column
        list_fields = df.columns[2:]

        # Stats cell
        df_units = df.loc[df['Types'] == 'units']
        list_units = df_units['Type'].to_list()

        # Company
        df_company = df[df['Types'] == 'company']
        list_company = df_company['Type'].to_list()

        # Field column description
        df_description = df[df['Types'] == 'description']
        list_description = df_description['Type'].to_list()

        # CIK
        df_cik = df[df['Types'] == 'cik']
        list_cik = df_cik['Type'].to_list()

        clean_df_list = []

        # Clean EDGAR data into a clean and machine legible data frame
        for unit, company, description, cik in zip(list_units, list_company, list_description, list_cik):
            print(' '.join(['Company:', company]))
            print(' '.join(['CIK:', cik]))
            print(' '.join(['Unit:', unit]))

            for field in list_fields:
                # Get stats
                df_stats = df[['Type', field]]
                df_stats_type = df_stats.loc[df_stats['Type'] == unit]
                df_stats_altered = df_stats_type.iloc[0][field]

                # Get account description
                df_description = df[['Type', field]]
                df_description = df_description.loc[df_description['Type'] == description]
                account_description = df_description.iloc[0][field]

                try:
                    key_value = list(df_stats_altered.keys())[0]

                    if key_value == 'USD':
                        df_stats_altered = df_stats_altered['USD']
                        df_stats_altered = pd.DataFrame(df_stats_altered)
                        df_stats_altered['field'] = re.sub(r"(\w)([A-Z])", r"\1 \2", df_stats.columns[1])
                        df_stats_altered['description'] = account_description
                        df_stats_altered['company'] = company
                        df_stats_altered['cik'] = cik
                        
                        # Get annual data
                        df_stats_altered = df_stats_altered.dropna(subset = ['frame'])
                        df_stats_altered = df_stats_altered[~df_stats_altered['frame'].str.contains("Q")]
                        df_stats_altered['frame'] = df_stats_altered['frame'].str.replace('CY', '')

                        clean_df_list.append(df_stats_altered)

                    elif key_value == 'shares':
                        df_stats_altered = df_stats_altered['shares']
                        df_stats_altered = pd.DataFrame(df_stats_altered)
                        df_stats_altered['field'] = re.sub(r"(\w)([A-Z])", r"\1 \2", df_stats.columns[1])
                        df_stats_altered['description'] = account_description
                        df_stats_altered['company'] = company
                        df_stats_altered['cik'] = cik                    
                        
                        # Get annual data
                        df_stats_altered = df_stats_altered.dropna(subset = ['frame'])
                        df_stats_altered = df_stats_altered[~df_stats_altered['frame'].str.contains("Q")]
                        df_stats_altered['frame'] = df_stats_altered['frame'].str.replace('CY', '')

                        clean_df_list.append(df_stats_altered)

                    elif key_value == 'USD/shares':
                        df_stats_altered = df_stats_altered['USD/shares']
                        df_stats_altered = pd.DataFrame(df_stats_altered)
                        df_stats_altered['field'] = re.sub(r"(\w)([A-Z])", r"\1 \2", df_stats.columns[1])
                        df_stats_altered['description'] = account_description
                        df_stats_altered['company'] = company
                        df_stats_altered['cik'] = cik                    
                        
                        # Get annual data
                        df_stats_altered = df_stats_altered.dropna(subset = ['frame'])
                        df_stats_altered = df_stats_altered[~df_stats_altered['frame'].str.contains("Q")]
                        df_stats_altered['frame'] = df_stats_altered['frame'].str.replace('CY', '')

                        clean_df_list.append(df_stats_altered)

                except:
                    pass
                
    # No data so return an empty list           
    except:
        clean_df_list = []
        pass
        
    return clean_df_list


######################################################################################################################
# NEW BLOCK - Process data for etl
######################################################################################################################

# Processes full data
#########################################################################
def process_edgar_data(edgar_df, set_ids, id_prefix):
    '''
    - Processes data to insert into PostgreSQL
    - Adds ticker column
    '''
    # rename columns to match sql table schemas
    edgar_df = edgar_df[[
        'cik', 
        'end', 
        'val', 
        'accn', 
        'fy',
        'fp', 
        'form',
        'filed', 
        'frame',
        'field',
        'description',
        'company', 
        'start'
    ]]
    
    # Fill empty values with np.nan
    edgar_df = edgar_df.fillna(np.nan)

    # Create empty ticker column
    edgar_df['ticker'] = np.nan
    
    if set_ids == False:
        # Create ids for field and description add a prefix to account for chunking nulling the unique grouping effect
        edgar_df['financial_acc_id'] = 0
        edgar_df['financial_acc_id'] = id_prefix + edgar_df['financial_acc_id']

        edgar_df['financial_acc_descriptions_id'] = 0
        edgar_df['financial_acc_descriptions_id'] = id_prefix + edgar_df['financial_acc_descriptions_id']
        
    elif set_ids == True:
        # Reset ids
        edgar_df['financial_acc_id'] = edgar_df.groupby(['cik','field','description']).ngroup()
        edgar_df['financial_acc_descriptions_id'] = edgar_df.groupby(['cik','field','description']).ngroup()
    
    # Determine data types
    edgar_df['cik'] = edgar_df['cik'].astype('int')
    edgar_df['end'] = edgar_df['end'].astype('object')
    edgar_df['val'] = edgar_df['val'].astype('float')
    edgar_df['accn'] = edgar_df['accn'].astype('object')
    edgar_df['fy'] = edgar_df['fy'].astype('object')
    edgar_df['fp'] = edgar_df['fp'].astype('object')
    edgar_df['form'] = edgar_df['form'].astype('object')
    edgar_df['filed'] = edgar_df['filed'].astype('object')
    edgar_df['frame'] = edgar_df['frame'].astype('int')
    edgar_df['field'] = edgar_df['field'].astype('object')    
    edgar_df['description'] = edgar_df['description'].astype('object')     
    edgar_df['company'] = edgar_df['company'].astype('object')
    edgar_df['start'] = edgar_df['start'].astype('object')
    
    # Remove all '|' characters from strings
    edgar_df['field'] = edgar_df['field'].str.replace('|','')   
    edgar_df['field'] = edgar_df['field'].str.replace("\\","") 
    edgar_df['description'] = edgar_df['description'].str.replace('|','')  
    edgar_df['description'] = edgar_df['description'].str.replace("\\","") 
    edgar_df['company'] = edgar_df['company'].str.replace('|','')
    edgar_df['company'] = edgar_df['company'].str.replace("\\","")
    
    print('Processed full data.')
    
    return edgar_df


# Processes companies table
#########################################################################
def process_companies_data(edgar_df, remove_duplicates):
    '''
    - Create companies tables
    '''
    companies_df = edgar_df[['cik','company','ticker']]
    
    if remove_duplicates == True:
        companies_df = companies_df.drop_duplicates(subset = ['cik'], keep = 'first').reset_index(drop = True)
        
    elif remove_duplicates == False:
        companies_df = companies_df
    
    print('Processed companies data.')

    return companies_df


# Processes financial accounts table
#########################################################################
def process_financial_acc_data(edgar_df, remove_duplicates):
    '''
    - Create financial accounts table
    '''
    financial_acc_df = edgar_df[['financial_acc_id','field']]
    
    if remove_duplicates == True:
        financial_acc_df = financial_acc_df.drop_duplicates(subset = ['financial_acc_id'], keep = 'first').reset_index(drop = True)
        
    elif remove_duplicates == False:
        financial_acc_df = financial_acc_df
    
    print('Processed financial_accounts data.')

    return financial_acc_df


# Processes financial accounts descriptions table
#########################################################################
def process_financial_acc_descriptions_data(edgar_df, remove_duplicates):
    '''
    - Create financial accounts table
    '''
    financial_acc_descriptions_df = edgar_df[['financial_acc_descriptions_id','description']]
    
    if remove_duplicates == True:
        financial_acc_descriptions_df = financial_acc_descriptions_df.drop_duplicates(subset = ['financial_acc_descriptions_id'], keep = 'first').reset_index(drop = True)
        
    elif remove_duplicates == False:
        financial_acc_descriptions_df = financial_acc_descriptions_df
    
    print('Processed financial_accounts_descriptions data.')

    return financial_acc_descriptions_df


# Processes company accounts table
#########################################################################
def process_company_financials_data(edgar_df):
    '''
    - Create company accounts tables
    '''
    company_financials_df = edgar_df[[
        'cik',
        'financial_acc_id',
        'financial_acc_descriptions_id',
        'end',
        'val',
        'accn',
        'fy',
        'fp',
        'form',
        'filed',
        'start',
        'frame'
    ]]
    
    print('Processed company_financials data.')

    return company_financials_df


######################################################################################################################
# NEW BLOCK - Insert data into edgardb
######################################################################################################################

# Insert companies
#########################################################################
def insert_companies_data(companies_df, conn, cur):
    '''
    - Inserts data into the companies table in edgardb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(companies_df.to_csv(
            index = None,
            header = None,
            sep = '\t'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'companies',
            columns = companies_df.columns,
            sep = '\t'
            )
            
        conn.commit()

        print('Companies data inserted in bulk to egardb successfully 1.')
        print(' '.join(['Rows inserted:', str(companies_df.shape[0])]))

    except ps.Error as e:
        print('Insert Companies data error:')
        print(e)

# Insert companies data with replacement on cik conflict for ticker additions
def insert_companies_data_tickers(companies_df, conn, cur):
    '''
    - Insert companies data
    '''
    try:
        for index, row in companies_df.iterrows():
            cur.execute(companies_table_insert, list(row))
            
            conn.commit()

        print('Companies data inserted line-by-line into edgardb successfully 1')

    except ps.Error as e:
        print('\n Error:')
        print(e)

    print(' '.join(['Columns inserted:', str(companies_df.shape[1])]))

    
# Insert financial accounts
#########################################################################
def insert_financial_acc_data(financial_acc_df, conn, cur):
    '''
    - Inserts data into the financial_accounts table in edgardb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(financial_acc_df.to_csv(
            index = None,
            header = None,
            sep = '\t'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'financial_accounts',
            columns = financial_acc_df.columns,
            sep = '\t'
            )
            
        conn.commit()

        print('Financial Accounts data inserted in bulk to egardb successfully 1.')
        print(' '.join(['Rows inserted:', str(financial_acc_df.shape[0])]))

    except ps.Error as e:
        print('Insert Financial Accounts data error:')
        print(e)
    
    
# Insert financial accounts descriptions
#########################################################################
def insert_financial_acc_descriptions_data(financial_acc_descriptions_df, conn, cur):
    '''
    - Inserts data into the financial_accounts_descriptions table in edgardb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(financial_acc_descriptions_df.to_csv(
            index = None,
            header = None,
            sep = '\t'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'financial_accounts_descriptions',
            columns = financial_acc_descriptions_df.columns,
            sep = '\t'
            )
            
        conn.commit()

        print('Financials Accounts Descriptions data inserted in bulk to egardb successfully 1.')
        print(' '.join(['Rows inserted:', str(financial_acc_descriptions_df.shape[0])]))

    except ps.Error as e:
        print('Insert Financials Accounts Descriptions data error:')
        print(e)
    

# Insering company financials
#########################################################################
def insert_company_financials_data(company_financials_df, conn, cur):
    '''
    - Inserts data into the company_financials table in edgardb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Stream cleaned data in bulk to database
    try:
        sio = StringIO()
        
        sio.write(company_financials_df.to_csv(
            index = None,
            header = None,
            sep = '\t'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'company_financials',
            columns = company_financials_df.columns,
            sep = '\t'
            )
            
        conn.commit()

        print('Company Financials data inserted in bulk to egardb successfully 1.')
        print(' '.join(['Rows inserted:', str(company_financials_df.shape[0])]))

    except ps.Error as e:
        print('Insert Company Financials data error:')
        print(e)


######################################################################################################################
# NEW BLOCK - Run EDGAR parsing and cleaning in chunks
######################################################################################################################

def run_edgar_chunks(file_num, chunk_size, zip_file, conn, cur):
    '''
    - Run the EDGAR API in chunks to allow for efficient data limits and saves the final data frame
    '''
    print('*******************************************************************************')
    print('Got File Logistics')
    print('*******************************************************************************')   
    
    file_number_quotient = int(file_num / chunk_size)
    print(' '.join(['Quotient:', str(file_number_quotient)]))
    
    file_number_product = file_number_quotient * chunk_size
    print(' '.join(['Product:', str(file_number_product)]))
    
    file_number_remainder = file_num - file_number_product
    print(' '.join(['Remainder:', str(file_number_remainder)]))
    
    chunk_index_start = 0
    chunk_index_end = chunk_size
    
    while chunk_index_end <= file_number_product:
        print('*******************************************************************************')
        print('Getting Files')
        print('*******************************************************************************')        
        
        files_list, file_len = get_zipped_files(
            zip_file = zip_file, 
            start_index = chunk_index_start, 
            end_index = chunk_index_end
        )
        
        print('*******************************************************************************')
        print('Getting First Data Frames')
        print('*******************************************************************************')          
        
        df_list = parse_edgar_json(
            zip_file = zip_file, 
            files_list = files_list
        )
        
        print('*******************************************************************************')
        print('Getting Final Data Frame')
        print('*******************************************************************************')             
        
        final_clean_df = clean_edgar_data(
            df_list = df_list
        )
        
        # Cleaned data to concat
        if len(final_clean_df) > 1:
            edgar_df = pd.concat(final_clean_df, axis = 0).reset_index(drop = True)
            
            # Process data
            edgar_df = process_edgar_data(
                edgar_df = edgar_df,
                set_ids = False,
                id_prefix = 0
            )
            
            companies_df = process_companies_data(edgar_df = edgar_df, remove_duplicates = True)
            financial_acc_df = process_financial_acc_data(edgar_df = edgar_df, remove_duplicates = False)
            financial_acc_descriptions_df = process_financial_acc_descriptions_data(edgar_df = edgar_df, remove_duplicates = False)
            company_financials_df = process_company_financials_data(edgar_df = edgar_df)
            
            # Insert data in edgardb
            # Companies
            insert_companies_data(
                companies_df = companies_df, 
                conn = conn, 
                cur = cur
            )
            
            # Financial accounts
            insert_financial_acc_data(
                financial_acc_df = financial_acc_df, 
                conn = conn, 
                cur = cur
            )
            
            # Financial account descriptions
            insert_financial_acc_descriptions_data(
                financial_acc_descriptions_df = financial_acc_descriptions_df, 
                conn = conn, 
                cur = cur
            )
            
            # Company financials
            insert_company_financials_data(
               company_financials_df = company_financials_df, 
               conn = conn, 
               cur = cur
            )
            
        # Cleaned data NOT to concat
        elif len(final_clean_df) == 1:
            edgar_df = final_clean_df[0].reset_index(drop = True)
            
            # Process data
            edgar_df = process_edgar_data(
                edgar_df = edgar_df,
                set_ids = False,
                id_prefix = 0
            )
            
            companies_df = process_companies_data(edgar_df = edgar_df, remove_duplicates = True)
            financial_acc_df = process_financial_acc_data(edgar_df = edgar_df, remove_duplicates = False)
            financial_acc_descriptions_df = process_financial_acc_descriptions_data(edgar_df = edgar_df, remove_duplicates = False)
            company_financials_df = process_company_financials_data(edgar_df = edgar_df)
            
            # Insert data in edgardb
            # Companies
            insert_companies_data(
                companies_df = companies_df, 
                conn = conn, 
                cur = cur
            )
            
            # Financial accounts
            insert_financial_acc_data(
                financial_acc_df = financial_acc_df, 
                conn = conn, 
                cur = cur
            )
            
            # Financial account descriptions
            insert_financial_acc_descriptions_data(
                financial_acc_descriptions_df = financial_acc_descriptions_df, 
                conn = conn, 
                cur = cur
            )
            
            # Company financials
            insert_company_financials_data(
               company_financials_df = company_financials_df, 
               conn = conn, 
               cur = cur
            )
            
        # No cleaned data
        else:
            print('No data to add for this chunk')
            pass
        
        print(' '.join(['Index start:', str(chunk_index_start)]))
        print(' '.join(['Index end:', str(chunk_index_end)]))
        
        chunk_index_start += chunk_size
        chunk_index_end += chunk_size
        
    if chunk_index_end > file_number_product:
        chunk_index_start = chunk_index_start
        chunk_index_end = file_num
        
        print('*******************************************************************************')
        print('Getting Last Loop Index')
        print('*******************************************************************************')        
        
        print(' '.join(['Last loop start', str(chunk_index_start)]))
        print(' '.join(['Last loop end', str(chunk_index_end)]))
        
        print('*******************************************************************************')
        print('Getting Files')
        print('*******************************************************************************')         

        files_list, file_len = get_zipped_files(
            zip_file = zip_file, 
            start_index = chunk_index_start, 
            end_index = chunk_index_end
        )
        
        print('*******************************************************************************')
        print('Getting First Data Frames')
        print('*******************************************************************************')         

        df_list = parse_edgar_json(
            zip_file = zip_file, 
            files_list = files_list
        )
        
        print('*******************************************************************************')
        print('Getting Final Data Frame')
        print('*******************************************************************************')          

        final_clean_df = clean_edgar_data(
            df_list = df_list
        )
        
        # Cleaned data to concat
        if len(final_clean_df) > 1:
            edgar_df = pd.concat(final_clean_df, axis = 0).reset_index(drop = True)
            
            # Process data
            edgar_df = process_edgar_data(
                edgar_df = edgar_df,
                set_ids = False,
                id_prefix = 0
            )
            
            companies_df = process_companies_data(edgar_df = edgar_df, remove_duplicates = True)
            financial_acc_df = process_financial_acc_data(edgar_df = edgar_df, remove_duplicates = False)
            financial_acc_descriptions_df = process_financial_acc_descriptions_data(edgar_df = edgar_df, remove_duplicates = False)
            company_financials_df = process_company_financials_data(edgar_df = edgar_df)
            
            # Insert data in edgardb
            # Companies
            insert_companies_data(
                companies_df = companies_df, 
                conn = conn, 
                cur = cur
            )
            
            # Financial accounts
            insert_financial_acc_data(
                financial_acc_df = financial_acc_df, 
                conn = conn, 
                cur = cur
            )
            
            # Financial account descriptions
            insert_financial_acc_descriptions_data(
                financial_acc_descriptions_df = financial_acc_descriptions_df, 
                conn = conn, 
                cur = cur
            )
            
            # Company financials
            insert_company_financials_data(
               company_financials_df = company_financials_df, 
               conn = conn, 
               cur = cur
            )
            
        # Cleaned data NOT to concat
        elif len(final_clean_df) == 1:
            edgar_df = final_clean_df[0].reset_index(drop = True)
            
            # Process data
            edgar_df = process_edgar_data(
                edgar_df = edgar_df,
                set_ids = False,
                id_prefix = 0
            )
            
            companies_df = process_companies_data(edgar_df = edgar_df, remove_duplicates = True)
            financial_acc_df = process_financial_acc_data(edgar_df = edgar_df, remove_duplicates = False)
            financial_acc_descriptions_df = process_financial_acc_descriptions_data(edgar_df = edgar_df, remove_duplicates = False)
            company_financials_df = process_company_financials_data(edgar_df = edgar_df)
            
            # Insert data in edgardb
            # Companies
            insert_companies_data(
                companies_df = companies_df, 
                conn = conn, 
                cur = cur
            )
            
            # Financial accounts
            insert_financial_acc_data(
                financial_acc_df = financial_acc_df, 
                conn = conn, 
                cur = cur
            )
            
            # Financial account descriptions
            insert_financial_acc_descriptions_data(
                financial_acc_descriptions_df = financial_acc_descriptions_df, 
                conn = conn, 
                cur = cur
            )
            
            # Company financials
            insert_company_financials_data(
               company_financials_df = company_financials_df, 
               conn = conn, 
               cur = cur
            )
               
        # No cleaned data
        else:
            print('No data to add for this chunk')
            pass
        
        print(' '.join(['File chunk size', str(chunk_size), 'files']))
        print(' '.join(['File Count: ', str(chunk_index_end)]))
    
    
######################################################################################################################
# NEW BLOCK - Run EDGAR ETL pipeline
######################################################################################################################

def run_edgar_etl_pipeline(zip_file, ticker_file):
    '''
    - Runs edgar etl pipeline
    - Adds ticker data
    '''
    # Connect to database
    #########################################################################
    try:
        conn = ps.connect('''
        
            host=localhost
            dbname=edgardb
            user=postgres
            password=iEchu133
            
        ''')
        
        cur = conn.cursor()

        print('Successfully connected to edgardb')

    except ps.Error as e:
        print('\n Database Error:')
        print(e)
        
    # Clear table data
    #########################################################################
    try:
        cur.execute(companies_table_drop_rows)
        cur.execute(financial_acc_table_drop_rows)
        cur.execute(financial_acc_descriptions_table_drop_rows)
        cur.execute(company_financials_table_drop_rows)
        conn.commit()
        
        print('Cleared table data')
        
    except ps.Error as e:
        print('\n Table Reset Error:')
        print(e)
    
    
    # Parse EDGAR API
    #########################################################################
    # Get number of json company stats files
    file_len = get_files_length(
        zip_file = zip_file
    )
    
    # Parse and cleaning json files in chunks
    run_edgar_chunks(
        file_num = file_len,
        chunk_size = 10,
        zip_file = zip_file,
        conn = conn, 
        cur = cur
    )
    
    print('*******************************************************************************')
    print('Adding Tickers and Resetting IDs')
    print('*******************************************************************************') 
    
    # Add tickers
    #########################################################################
    # Get companies table
    query = '''
    
        SELECT *
        FROM companies;
    
    '''

    cur.execute(query)
    previous_df = cur.fetchall()

    previous_columns = [
        'cik', 
        'company', 
        'ticker'
    ]

    # Convert companies table to pandas data frame
    previous_df = pd.DataFrame(previous_df, columns = previous_columns)
    
    # Drop empy ticker column to merge full ticker column
    previous_df = previous_df.drop(
        ['ticker'],
        axis = 1,
        errors = 'ignore'
    )
    
    # Tickers data
    # http://rankandfiled.com/#/data/tickers
    tickers_df = pd.read_csv(ticker_file, sep = '|')
    
    # Merge tickers
    acc_stats_df = previous_df.merge(
        tickers_df[['cik', 'ticker']], 
        on = 'cik',
        how = 'left'
    )
    
    # Export final data
    # Insert data in edgardb
    insert_companies_data_tickers(
        companies_df = acc_stats_df, 
        conn = conn, 
        cur = cur
    )
    
    # Remove duplicates and set ids for financial accounts and descriptions
    #########################################################################
    # Get companies table
    query = '''
    
        SELECT *
        FROM edgar_view_pre;
    
    '''

    cur.execute(query)
    edgar_view_pre_df = cur.fetchall()

    edgar_view_pre_columns = [
        'cik',
        'company',
        'ticker',
        'end',
        'accn',
        'fp',
        'form',
        'filed',
        'start',
        'val',
        'fy',
        'frame',
        'financial_acc_id',
        'field',
        'financial_acc_descriptions_id',
        'description'
    ]

    # Convert companies table to pandas data frame
    edgar_view_pre_df = pd.DataFrame(edgar_view_pre_df, columns = edgar_view_pre_columns)
    
    # Process data
    edgar_view_pre_df = process_edgar_data(
        edgar_df = edgar_view_pre_df,
        set_ids = True,
        id_prefix = 0
    )

    financial_acc_df = process_financial_acc_data(edgar_df = edgar_view_pre_df, remove_duplicates = True)
    financial_acc_descriptions_df = process_financial_acc_descriptions_data(edgar_df = edgar_view_pre_df, remove_duplicates = True)
    company_financials_df = process_company_financials_data(edgar_df = edgar_view_pre_df)
    

    # Insert data in edgardb
    try:
        cur.execute(financial_acc_table_drop_rows)
        cur.execute(financial_acc_descriptions_table_drop_rows)
        cur.execute(company_financials_table_drop_rows)
        conn.commit()
        
        print('Cleared table data')
        
    except ps.Error as e:
        print('\n Table Reset Error:')
        print(e)
        
    # Financial accounts
    insert_financial_acc_data(
        financial_acc_df = financial_acc_df, 
        conn = conn, 
        cur = cur
    )

    # Financial account descriptions
    insert_financial_acc_descriptions_data(
        financial_acc_descriptions_df = financial_acc_descriptions_df, 
        conn = conn, 
        cur = cur
    )

    # Company financials
    insert_company_financials_data(
       company_financials_df = company_financials_df, 
       conn = conn, 
       cur = cur
    ) 
    
    # Close database connection
    cur.close()
    conn.close()
    
    
    print('IDs reset')
    print('Tickers added')
    print('Program complete')

        
if __name__ == '__main__':
    run_edgar_etl_pipeline(
        zip_file = r'C:\Users\jbenvenuto\Desktop\GitHub_Projects\companyfacts.zip', 
        ticker_file = r'C:\Users\jbenvenuto\Desktop\GitHub_Projects\company_tickers.csv'
    )   

    