from API_Financial_Statements import parse_financial_api
from ETL_Financial_Statements import etl

import sys


def main():
    '''
    - Run both API for company financial statements and ETL pipeline
    '''
###########################################################################################################################################
# NEW BLOCK - Module 1 API for company financial statements data
###########################################################################################################################################

    print('''
    Module 1:
    Wrangles data from https://site.financialmodelingprep.com/developer/docs
    ''')

    yesChoice = ['yes','y']
    noChoice = ['no','n']

    input_1 = input("Would you like to run Module 1? ['yes','y'] or ['no','n'] ")
    input_1 = input_1.lower()

    if input_1 in yesChoice:
        try:
            '''
            - Warnagle and store company financial statements data to data storage directories via CSV
            '''
            parse_financial_api()
            input("Press enter to continue to Module 2 or Ctrl C to end the program")
        except Exception as e:
            print(e)
            input("Please check the noted error above and decide to press enter and continue to Module 2 or Ctrl C to end the program")

    elif input_1 in noChoice:
        print('You have skipped Module 1')
        pass

    else:
        input('You have entered an incorrect response, please press enter to end the program')
        sys.exit()


###########################################################################################################################################
# NEW BLOCK - ETL Module
###########################################################################################################################################

    print('''
    Module 2:
    Runs the ETL pipline to store the company financial statements data in PostgreSQL database (financialdb)
    ''')

    input_2 = input("Would you like to run the ETL Module? ['yes','y'] or ['no','n']")
    input_2 = input_2.lower()

    if input_2 in yesChoice:
        try:
            '''
            - Run ETL pipeline to financialdb
            '''
            etl()
            input("ETL Module complete, please press enter or Ctrl C to end the program")
        except Exception as e:
            print(e)
            input("Please check the noted error above")

    elif input_2 in noChoice:
        print('You have skipped the ETL Module')
        print('Program complete')
        pass

    else:
        input('You have entered an incorrect response, please press enter to end the program')
        sys.exit()
        
        
if __name__ == "__main__":
    main()