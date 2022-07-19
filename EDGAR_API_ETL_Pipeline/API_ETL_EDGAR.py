from zipfile import ZipFile
import zipfile
import json
import re

import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_columns', None)
import numpy as np

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
                        df_stats_altered = df_stats_altered.loc[df_stats_altered['form'] == '10-K']
                        df_stats_altered = df_stats_altered.sort_values(by = ['fy'])

                        try:
                            df_stats_altered = df_stats_altered[df_stats_altered['frame'].isnull()]
                        except:
                            pass

                        df_stats_altered = df_stats_altered.drop_duplicates(subset = ['fy'], keep = 'last')

                        df_stats_altered = df_stats_altered.drop(
                            ['frame'],
                            axis = 1,
                            errors = 'ignore'
                        )

                        clean_df_list.append(df_stats_altered)

                    elif key_value == 'shares':
                        df_stats_altered = df_stats_altered['shares']
                        df_stats_altered = pd.DataFrame(df_stats_altered)
                        df_stats_altered['field'] = re.sub(r"(\w)([A-Z])", r"\1 \2", df_stats.columns[1])
                        df_stats_altered['description'] = account_description
                        df_stats_altered['company'] = company
                        df_stats_altered['cik'] = cik                    
                        df_stats_altered = df_stats_altered.loc[df_stats_altered['form'] == '10-K']
                        df_stats_altered = df_stats_altered.sort_values(by = ['fy'])

                        try:
                            df_stats_altered = df_stats_altered[df_stats_altered['frame'].isnull()]
                        except:
                            pass

                        df_stats_altered = df_stats_altered.drop_duplicates(subset = ['fy'], keep = 'last')

                        df_stats_altered = df_stats_altered.drop(
                            ['frame'],
                            axis = 1,
                            errors = 'ignore'
                        )

                        clean_df_list.append(df_stats_altered)

                    elif key_value == 'USD/shares':
                        df_stats_altered = df_stats_altered['USD/shares']
                        df_stats_altered = pd.DataFrame(df_stats_altered)
                        df_stats_altered['field'] = re.sub(r"(\w)([A-Z])", r"\1 \2", df_stats.columns[1])
                        df_stats_altered['description'] = account_description
                        df_stats_altered['company'] = company
                        df_stats_altered['cik'] = cik                    
                        df_stats_altered = df_stats_altered.loc[df_stats_altered['form'] == '10-K']
                        df_stats_altered = df_stats_altered.sort_values(by = ['fy'])

                        try:
                            df_stats_altered = df_stats_altered[df_stats_altered['frame'].isnull()]
                        except:
                            pass

                        df_stats_altered = df_stats_altered.drop_duplicates(subset = ['fy'], keep = 'last')

                        df_stats_altered = df_stats_altered.drop(
                            ['frame'],
                            axis = 1,
                            errors = 'ignore'
                        )

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
def process_edgar_data(edgar_df):
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
        'field',
        'description',
        'company', 
        'start'
    ]]
    
    # Fill empty values with np.nan
    edgar_df = edgar_df.fillna(np.nan)

    # Create empty ticker column
    edgar_df['ticker'] = np.nan
    
    print('Processed full data.')
    
    return edgar_df


# Processes companies table
#########################################################################
def process_companies_data(edgar_df):
    '''
    - Create companies tables
    '''
    companies_df = edgar_df[['cik','company','ticker']]
    companies_df = companies_df.drop_duplicates(subset = ['cik'], keep = 'first').reset_index(drop = True)
    
    print('Processed companies data.')

    return companies_df


# # Processes financial accounts table
# #########################################################################
# def process_financial_accounts_data(edgar_df):
#     '''
#     - Create financial accounts tables
#     '''
#     financial_accounts_df = edgar_df[['financial_accounts_id','field','description']]
#     financial_accounts_df = financial_accounts_df.drop_duplicates(subset = ['financial_accounts_id'], keep = 'first').reset_index(drop = True)
    
#     print('Processed financial_accounts data.')

#     return financial_accounts_df


# Processes company accounts table
#########################################################################
def process_company_financials_data(edgar_df):
    '''
    - Create company accounts tables
    '''
    company_financials_df = edgar_df[[
        'cik',
        'end',
        'val',
        'accn',
        'fy',
        'fp',
        'form',
        'filed',
        'start',
        'field',
        'description'
    ]]
    
    print('Processed company_financials data.')

    return company_financials_df


######################################################################################################################
# NEW BLOCK - Insert data into edgardb
######################################################################################################################

# Insert data line by line for conflict conditions
#########################################################################
def insert_companies_data(companies_df, conn, cur):
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

    
# # Insert data line by line for conflict conditions
# #########################################################################
# def insert_financial_accounts_data(financial_accounts_df, conn, cur):
#     '''
#     - Insert financial accounts data
#     '''
#     try:
#         for index, row in financial_accounts_df.iterrows():
#             cur.execute(financial_accounts_table_insert, list(row))
            
#             conn.commit()

#         print('Financial Accounts data inserted line-by-line into edgardb successfully 1')

#     except ps.Error as e:
#         print('\n Error:')
#         print(e)

#     print(' '.join(['Columns inserted:', str(financial_accounts_df.shape[1])]))
    

# Insering company financials
#########################################################################
def insert_company_financials_data(company_financials_df, conn, cur):
    '''
    - Inserts company financials data into the company_financials table in edgardb
    - This is a bulk import maximizing speed and memory to adjust for the large number of rows
    '''
    # Stream cleaned data in bulk to database
    try:
        # Drop table to reinsert in bulk
        # cur.execute(company_financials_table_drop_rows)
        # conn.commit()

        sio = StringIO()
        
        sio.write(company_financials_df.to_csv(
            index = None,
            header = None,
            sep = '|'
        ))
        
        sio.seek(0)

        cur.copy_from(
            file = sio,
            table = 'company_financials',
            columns = company_financials_df.columns,
            sep = '|'
            )
            
        conn.commit()

        print('Company Financials data inserted in bulk to eegardb successfully 1.')
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
            edgar_df = process_edgar_data(edgar_df = edgar_df)
            companies_df = process_companies_data(edgar_df = edgar_df)
            # financial_accounts_df = process_financial_accounts_data(edgar_df = edgar_df)
            company_financials_df = process_company_financials_data(edgar_df = edgar_df)
            
            # Insert data in edgardb
            insert_companies_data(
                companies_df = companies_df, 
                conn = conn, 
                cur = cur
            )
            
            # insert_financial_accounts_data(
            #     financial_accounts_df = financial_accounts_df, 
            #     conn = conn, 
            #     cur = cur
            # )
            
            insert_company_financials_data(
               company_financials_df = company_financials_df, 
               conn = conn, 
               cur = cur
            )
            
        # Cleaned data NOT to concat
        elif len(final_clean_df) == 1:
            edgar_df = final_clean_df[0].reset_index(drop = True)
            
            # Process data
            edgar_df = process_edgar_data(edgar_df = edgar_df)
            companies_df = process_companies_data(edgar_df = edgar_df)
            # financial_accounts_df = process_financial_accounts_data(edgar_df = edgar_df)
            company_financials_df = process_company_financials_data(edgar_df = edgar_df)
            
            # Insert data in edgardb
            insert_companies_data(
                companies_df = companies_df, 
                conn = conn, 
                cur = cur
            )
            
            # insert_financial_accounts_data(
            #     financial_accounts_df = financial_accounts_df, 
            #     conn = conn, 
            #     cur = cur
            # )
            
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
            edgar_df = process_edgar_data(edgar_df = edgar_df)
            companies_df = process_companies_data(edgar_df = edgar_df)
            # financial_accounts_df = process_financial_accounts_data(edgar_df = edgar_df)
            company_financials_df = process_company_financials_data(edgar_df = edgar_df)
            
            # Insert data in edgardb
            insert_companies_data(
                companies_df = companies_df, 
                conn = conn, 
                cur = cur
            )
            
            # insert_financial_accounts_data(
            #     financial_accounts_df = financial_accounts_df, 
            #     conn = conn, 
            #     cur = cur
            # )
            
            insert_company_financials_data(
               company_financials_df = company_financials_df, 
               conn = conn, 
               cur = cur
            )
            
        # Cleaned data NOT to concat
        elif len(final_clean_df) == 1:
            edgar_df = final_clean_df[0].reset_index(drop = True)
            
            # Process data
            edgar_df = process_edgar_data(edgar_df = edgar_df)
            companies_df = process_companies_data(edgar_df = edgar_df)
            # financial_accounts_df = process_financial_accounts_data(edgar_df = edgar_df)
            company_financials_df = process_company_financials_data(edgar_df = edgar_df)
            
            # Insert data in edgardb
            insert_companies_data(
                companies_df = companies_df, 
                conn = conn, 
                cur = cur
            )
            
            # insert_financial_accounts_data(
            #     financial_accounts_df = financial_accounts_df, 
            #     conn = conn, 
            #     cur = cur
            # )
            
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
    # Get number of json company stats files
    file_len = get_files_length(
        zip_file = zip_file
    )
    
    # Connect to database
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

    
    # Parse and cleaning json files in chunks
    run_edgar_chunks(
        file_num = file_len,
        chunk_size = 10,
        zip_file = zip_file,
        conn = conn, 
        cur = cur
    )
    
    print('*******************************************************************************')
    print('Adding Tickers')
    print('*******************************************************************************') 

    # Add tickers
    # Get view
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

    # Convert view to pandas data frame
    previous_df = pd.DataFrame(previous_df, columns = previous_columns)
    
    # Drop empy ticker column to merge full ticker column
    previous_df = previous_df.drop(
        ['ticker'],
        axis = 1,
        errors = 'ignore'
    )
    
    # Tickers data
    tickers_df = pd.read_json(ticker_file)
    tickers_df = tickers_df.T
    tickers_df = tickers_df.rename(columns = {'cik_str': 'cik'})
    
    # Merge tickers
    acc_stats_df = previous_df.merge(
        tickers_df[['cik', 'ticker']], 
        on = 'cik',
        how = 'left'
    )
    
    # Export final data
    # Insert data in edgardb
    insert_companies_data(
        companies_df = acc_stats_df, 
        conn = conn, 
        cur = cur
    )
    
    # Close database connection
    cur.close()
    conn.close()
    

    print('Tickers added')
    print('Program complete')

        
if __name__ == '__main__':
    run_edgar_etl_pipeline(
        zip_file = 'companyfacts.zip', 
        ticker_file = 'company_tickers.json'
    )   
