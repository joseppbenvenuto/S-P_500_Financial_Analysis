import pandas as pd
import psycopg2 as ps

def yahoo_view_csv():
    # Connect to database
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

    try:
        # Query view from edgardb
        query = '''

            SELECT *
            FROM yahoo_view;

        '''

        cur.execute(query)
        yahoo_df = cur.fetchall()

        yahoo_columns = [
            'financial_statement_type',
            'financial_accounts',
            'date',
            'financial_values',
            'ticker'
        ]

        # Convert view to pandas data frame
        yahoo_df = pd.DataFrame(yahoo_df, columns = yahoo_columns)
        
        # Export data
        yahoo_df.to_csv(
            'US_Financial_Statements.csv', 
            index = False, 
            encoding = 'utf8'
        )
        
        print('US_Financial_Statements.csv created')
        
    except Exception as e:
        print('CSV error:')
        print(e)
    
    
if __name__ == '__main__':
    yahoo_view_csv()