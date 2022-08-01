import pandas as pd
import psycopg2 as ps

def edgar_view_csv():
    # Connect to database
    ############################################################
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
    
    # Companies
    ############################################################
    try:
        # Query companies
        query = '''

            SELECT *
            FROM companies;

        '''

        cur.execute(query)
        companies_df = cur.fetchall()

        companies_columns = [
            'cik',
            'company',
            'ticker',
        ]


        # Convert view to pandas data frame
        companies_df = pd.DataFrame(companies_df, columns = companies_columns)
        
        print('Companies.csv created')

    except Exception as e:
        print('CSV error:')
        print(e)
        
    # Export data
    companies_df.to_csv(
        'Companies.csv', 
        index = False, 
        encoding = 'utf8'
    )
     
    # Company Financials
    ############################################################
    try:
        # Query companies_financials
        query = '''

            SELECT *
            FROM company_financials;

        '''

        cur.execute(query)
        companies_financials_df = cur.fetchall()

        companies_financials_columns = [
            'company_financials_id',
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
            'frame',
        ]


        # Convert view to pandas data frame
        companies_financials_df = pd.DataFrame(companies_financials_df, columns = companies_financials_columns)

        companies_financials_df = companies_financials_df[[
            'company_financials_id',
            'cik',
            'financial_acc_id',
            'financial_acc_descriptions_id',
            'val',
            'frame'
        ]]

        # Change data type to int64 from float64
        companies_financials_df['val'] = companies_financials_df['val'].astype('int64')
        
        print('Company_Financials.csv created')
        
    except Exception as e:
        print('CSV error:')
        print(e)
        
    # Export data
    companies_financials_df.to_csv(
        'Company_Financials.csv', 
        index = False, 
        encoding = 'utf8'
    )  
        
    # Financial Accounts
    ############################################################
    try:   
        # Query financial_accounts
        query = '''

            SELECT *
            FROM financial_accounts;

        '''

        cur.execute(query)
        financial_accounts_df = cur.fetchall()

        financial_accounts_columns = [
            'id',
            'financial_acc_id',
            'field'
        ]

        # Convert view to pandas data frame
        financial_accounts_df = pd.DataFrame(financial_accounts_df, columns = financial_accounts_columns)
        
        print('Financial_Accounts.csv created')
        
    except Exception as e:
        print('CSV error:')
        print(e)
        
    # Export data
    financial_accounts_df.to_csv(
        'Financial_Accounts.csv', 
        index = False, 
        encoding = 'utf8'
    )  
    
    # Financial Accounts Descriptions
    ############################################################
    try:   
        # Query financial_accounts_descriptions
        query = '''

            SELECT *
            FROM financial_accounts_descriptions;

        '''

        cur.execute(query)
        financial_acc_desriptions_df = cur.fetchall()

        financial_acc_desriptions_columns = [
            'id',
            'financial_acc_descriptions_id',
            'description'
        ]


        # Convert view to pandas data frame
        financial_acc_desriptions_df = pd.DataFrame(financial_acc_desriptions_df, columns = financial_acc_desriptions_columns)
        
        print('Financial Accounts Descriptions.csv created')
        
    except Exception as e:
        print('CSV error:')
        print(e)
        
    # Export data
    financial_acc_desriptions_df.to_csv(
        'Financial_Accounts_Descriptions.csv', 
        index = False, 
        encoding = 'utf8'
    ) 

    
if __name__ == '__main__':
    edgar_view_csv()
    
    