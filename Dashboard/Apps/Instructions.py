from dash import html


layout = html.Div([
    
    # Instructions
    html.Div([

        html.H2(
            'Instructions',
            style = {
#                 'padding':10,
                'padding-top':10,
                'margin-top':50,
                'font-family':'Arial, Helvetica, sans-serif',
                # 'background':'#00008B',
                # 'color':'#FFFFFF',
                'textAlign':'center'
            }
        ),
        
        html.Div(

            html.P([
                "The dashboard provides data for 6,472 American publicly traded companies. \
                 The purpose of the dashboard is to help the user observe multi year company financial data\
                 regarding the balance sheet, income, and cash-flow statements. The user has the choice to choose\
                 accounts from each statement type and the the ten-year trend for the selected account will be displayed\
                 as a line chart.",
                 html.Br(),
                 html.Br(),
                "Additionally, the dashboard provides live price, price to earnings, earnings per share, account summary\
                 and company summary data."
            ]),
            
            style = {
                'padding-top':40,
                'padding-left':70,
                'padding-right':70,
                'font-family':'Arial, Helvetica, sans-serif',
                'line-height':30,
                'textAlign':'center',
                'fontSize':20
            }
        )
    ]),
])

