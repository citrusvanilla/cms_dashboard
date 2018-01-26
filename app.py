from __future__ import division

import json
import math

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import statsmodels.api as sm

# Read in data.
data_file = 'data.csv'
raw_data = pd.read_csv('data.csv')

# Format datetime and extract year and month separately.
raw_data['Date of Contact'] = pd.to_datetime(raw_data['Date of Contact'],
                                             format='%Y-%m-%d')
raw_data['month'] = raw_data['Date of Contact'].dt.month
raw_data['year'] = raw_data['Date of Contact'].dt.year

# Instantiate a Dash object.
app = dash.Dash()
server = app.server

# Main Dash layout.
app.layout = html.Div(children=[

    # Title.
    html.H1(children='Historical and Future CRM Explorer',
            className='twelve columns',
            style={'text-align': 'center'}),

    # Subtitle.
    html.Div([
        html.Div([
            html.P('This app will allow you to explore historical client '
                   'contact data for all historical months, or months aggregated '
                   'across all available years.  Data may be filtered by customer '
                   'manager, or by individual client.  Short-term forecast has '
                   'been modeled with a simple cross-month ordinary-least-squares (OLS) '
                   'regression that accounts for seasonality and long-term trends.'),
            html.P('This app was built with Dash- a Python framework built on '
                   'top of Plotly.js, React, and Flask, and is deployed on Heroku. '),
            html.P('Source code can be found at '
                   'github.com/citrusvanilla/cms_dashboard.')
            ],
                 style={'margin': 'auto', 'width': '90%'},
        )
    ], className="row"),

    # Separator.
    html.Hr(),
    
    # Filters.
    html.Div([

        # Left Column.
        html.Div([

            # Dropdown 1 - Team Member
            html.Div([
                html.Label('Choose an Account Manager:'),
                dcc.Dropdown(
                    id='account-manager',
                    options=[{'label': '-All Managers', 'value': 'All Managers'}] + \
                            [{'label': x, 'value': x} for x in sorted(raw_data['Account manager'].unique())],
                    value='All Managers'
                ),
            ], style={'margin-bottom': '10'}),

            # Dropdown 2 - Client
            html.Div([
                html.Label('Choose a Client:'),
                dcc.Dropdown(
                    id='client',
                    options=[{'label': '-All Clients', 'value': 'All Clients'}] + \
                            [{'label': x, 'value': x} for x in sorted(raw_data['Client Name'].unique())],
                    value='All Clients'
                )
            ])
        ], className="six columns"),

        # Right Column.
        html.Div([

            # Radio Button 1 - Time View
            html.Div([
                html.Label('Choose a Monthly View:'),
                dcc.RadioItems(
                    id='time-view',
                    options=[
                        {'label': 'Historical Months and Forecasted Months', 'value': 'allhmwf'},
                        {'label': 'Historical Months Only', 'value': 'allhm'},
                        {'label': 'Historical Months Aggregated Across Years', 'value': 'agghm'}
                    ],
                    value='allhmwf'
                )
            ], style={'margin-bottom': '10'}),

            # Radio Button 2 - Reporting Statistic.
            html.Div([
                html.Label('Choose a Reporting Statistic:'),
                dcc.RadioItems(
                    id='reporting-statistic',
                    options=[
                        {'label': 'Total Contacts Made', 'value': 'tc'},
                        {'label': 'Unique Clients Contacted', 'value': 'ucc'},
                        {'label': 'Percentage of All Clients Contacted', 'value': 'pacc'}
                    ],
                    value='tc'
                )
            ])
        ], className="six columns")

    ], className="row", style={'margin': '20'}),

    # Separator.
    html.Hr(),

    html.Div([

        html.Div([
            
            # Main Bar Chart.
            dcc.Graph(id='main-graph')],
            className="twelve columns"
        )
    ], className="row", style={'height':'200px'})
])

# Callback 1 - User inputs.
@app.callback(
    dash.dependencies.Output('main-graph', 'figure'),
    [dash.dependencies.Input('account-manager', 'value'),
     dash.dependencies.Input('client', 'value'),
     dash.dependencies.Input('time-view', 'value'),
     dash.dependencies.Input('reporting-statistic', 'value')])
def update_main_graph(selected_account_manager, selected_client,
                      selected_time_view, selected_reporting_statistic):

    # New view.
    data = raw_data

    # Time view.
    if selected_time_view == "allhm" or selected_time_view == "allhmwf":
        groups = ['year', 'month']
    elif selected_time_view == "agghm":
        groups = ['month']

    # Subset Account Manager.
    if selected_account_manager != "All Managers":
        data = data[data['Account manager'] == selected_account_manager]

    # Subset Client.
    if selected_client != "All Clients":
        data = data[data['Client Name'] == selected_client]

    # Reporting Statistic.
    if selected_reporting_statistic == "tc":
        results = data.groupby(groups)['Client Name'].count().reset_index()
        y = results['Client Name']
    elif selected_reporting_statistic == "ucc":
        results = data.groupby(groups)['Client Name'].nunique().reset_index()
        y = results['Client Name']
    elif selected_reporting_statistic == "pacc":
        results = data.groupby(groups)['Client Name'].nunique().reset_index()
        y = results['Client Name'] / raw_data['Client Name'].nunique()

    # Forecast.
    if selected_time_view == "allhmwf":

        X2 = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        X3 = [2017, 2017, 2017, 2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018]
        Y2 = []

        for i in X2:

            Y_f = results[results.month==i]['Client Name'].tolist()
            X_f = range(len(Y_f))
            X_f = sm.add_constant(X_f)
            model = sm.OLS(Y_f,X_f).fit()

            if selected_reporting_statistic == "pacc":
                pred = (model.params[1]*len(Y_f) + model.params[0]) / \
                       raw_data['Client Name'].nunique()
            else:
                pred = int(model.params[1]*len(Y_f) + model.params[0])

            Y2.append(pred)


    # X values as strings.
    look_up = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul',
               8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    results['month'] = results['month'].apply(lambda x: look_up[x])

    # Get X-axis values.
    if selected_time_view == "agghm":
        X = results[groups[0]].astype(str)
    elif selected_time_view == "allhm":
        X = results[groups[1]].astype(str) + ", " + results[groups[0]].astype(str)
    elif selected_time_view == "allhmwf":
        X2 = [look_up[i] for i in X2]
        X = results[groups[1]].astype(str) + ", " + results[groups[0]].astype(str)
        X = X.tolist()
        X = X + [m+", "+n for m,n in zip(map(str, X2),map(str, X3))]
        y = y.tolist() + Y2

    return {
            'data': [go.Bar(x=X,
                            y=y,
                            text=y,
                            marker=dict(
                                    color=(['rgba(30,144,255,0.8)'] * 48) + 
                                           (['rgba(222,45,38,0.8)'] * 12)
                                        )
                            )
                    ],
            'layout': go.Layout(xaxis={'type': 'category'},
                                margin={'l': '30',
                                        'r': '10',
                                        't': '10',
                                        'b': '80'}),
            }

# External Style Sheet.
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# Main.
if __name__ == '__main__':
    app.run_server(debug=True)

