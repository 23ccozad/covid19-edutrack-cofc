'''---------------------------------------------------------------------------------------------------------------------
  File Name:   app.py
  End Result:  Produces a webpage showing various COVID-19 data on graphs for use at College of Charleston
  Outline:     1) Instantiate Objects for RGB Colors Used In Interface
               2) Set Up Dash Webpage and Detect Mobile Devices
               3) Collect and format current COVID-19 data for Charleston County, South Carolina, etc.
               4) Create shape and text objects to denote semesters and class modes on graph based on intervals.csv
               5) Draw figure and graph with selected COVID-19 data
               6) Create an HTML layout for graph, numbers, and buttons to change the graph
               7) Callbacks to change the graphs upon user's button click
  Author:      Connor Cozad (23ccozad@gmail.com)
  Created:     July 29, 2020
---------------------------------------------------------------------------------------------------------------------'''


import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from flask import request
import re
import pandas as pd
import datetime
import color  # Local file: color.py
import covid_data  # Local file: covid_data.py


##### 1) Instantiate Objects for RGB Colors Used In Interface ----------------------------------------------------------
# Note: All of the colors in this app.py file use these color objects. However, there are also other HTML elements
# colors that are set in style.css, which do not use these color objects. For example, if you change the RGB values for
# DARK_BLUE here which is the color used for South Carolina data and graphs, you will also want to make the same change
# to the background property of #sc-title in style.css to maintain consistency.

TEAL = color.Color(19, 146, 156)        # Color used for Downtown Charleston
BLUE_GREEN = color.Color(5, 102, 87)    # Color used for Charleston County
DARK_BLUE = color.Color(0, 51, 102)     # Color used for South Carolina
WHITE = color.Color(255, 255, 255)
OFF_WHITE = color.Color(248, 248, 248)
LIGHT_GRAY = color.Color(211, 211, 211)
DARK_GRAY = color.Color(85, 85, 85)
DIM_GRAY = color.Color(41, 41, 41)
BLACK = color.Color(0, 0, 0)
TRANSPARENT = color.Color(0, 0, 0, 0)



##### 2) Set Up Dash Webpage and Detect Mobile Devices -----------------------------------------------------------------

# Load Google Analytics on page load
external_scripts = ['https://www.googletagmanager.com/gtag/js?id=UA-174296614-1']

# Initalize the Dash app and provide webpage title
app = dash.Dash(__name__, external_scripts=external_scripts)
server = app.server
app.title = 'COVID-19 EduTrack @ CofC'

# Determine whether the user is viewing the webpage on a mobile device
is_mobile = None
@server.before_request
def before_request():
    agent = request.headers.get('User_Agent')
    mobile_string = '(?i)android|fennec|iemobile|iphone|opera (?:mini|mobi)|mobile'
    re_mobile = re.compile(mobile_string)
    global is_mobile
    is_mobile = len(re_mobile.findall(agent)) > 0



##### 3) Collect and format current COVID-19 data for Charleston County, South Carolina, etc. --------------------------

# Create objects to retrieve and manipulate data by geographic location
south_carolina = covid_data.StateData('South Carolina')
charleston_county = covid_data.CountyData('Charleston', 'South Carolina')
downtown_charleston = covid_data.ZIPCodeGroupData([29401, 29424, 29425, 29403, 29409])

# Read intervals.csv, which contains info about start and end dates of different semesters and class mode intervals
# Class mode options are 'in-person', 'hybrid', and 'virtual'
class_mode_intervals = pd.read_csv('assets/intervals.csv')
class_mode_intervals['Start_Date'] = pd.to_datetime(class_mode_intervals['Start_Date'])
class_mode_intervals['End_Date'] = pd.to_datetime(class_mode_intervals['End_Date'])



##### 4) Create shape and text objects to denote semesters and class modes on graph based on intervals.csv -------------

# Lists to hold the shape and text objects that will be added to the graph to denote each class mode
class_mode_shapes = []
class_mode_labels = []

# Read through each row in the CSV and create the shape (a light gray background) and text labels to plot on the graph
# to denote each class mode
for row in class_mode_intervals.itertuples():
    label = row[2]
    start_date = row[3]
    end_date = row[4]
    class_mode_shapes.append(dict(
        fillcolor=LIGHT_GRAY.color_to_str(alpha=0.2),
        line={'width': 0},
        type='rect',
        x0=start_date,
        x1=end_date,
        xref='x',
        y0=0,
        y1=1.0,
        yref='paper'
    ))
    class_mode_labels.append(dict(
        x=start_date + (end_date - start_date) / 2,
        showarrow=False,
        y=1.0,
        ax=0,
        text=label,
        xref='x',
        yanchor='top',
        yref='paper'
    ))

# Lists to hold the shape and text objects that will be added to the graph to denote each semester
semester_shapes=[]
semester_labels=[]

# Read through each row in the CSV and create the shape (a dark gray rectangle near the top of the graph) and text
# labels to plot on the graph to denote each semester
for semester in class_mode_intervals['Semester'].unique():
    all_intervals_in_semester = class_mode_intervals.loc[class_mode_intervals['Semester'] == semester]
    start_date = all_intervals_in_semester['Start_Date'].min()
    end_date = all_intervals_in_semester['End_Date'].max()
    semester_shapes.append(dict(
        fillcolor=LIGHT_GRAY.color_to_str(alpha=0.5),
        line={'width': 0},
        type='rect',
        x0=start_date,
        x1=end_date,
        xref='x',
        y0=1.0,
        y1=1.1,
        yref='paper'
    ))
    semester_labels.append(dict(
        x=start_date + (end_date - start_date) / 2,
        showarrow=False,
        y=1.05,
        ax=0,
        text=semester,
        xref='x',
        yanchor='middle',
        yref='paper'
    ))



##### 5) Draw figure and graph with selected COVID-19 data -------------------------------------------------------------

# Build a bar graph object with the given data and color
def create_bar_graph(x, y, color, location):
    return go.Bar(
        x=x,
        y=y,
        marker=dict(color=color.color_to_str(alpha=0.4), line_width=0),
        hovertemplate=
        '<span style="font-size: 20px; font-weight: 900; color: ' + color + '">%{y:,}</span>' +
        '<span style="font-size: 12px; font-weight: 500; color: ' + DARK_GRAY + '"> cases</span>' +
        '<span style="color: gray"><br>%{x}' +
        '<br>' + location + '</span>' +
        '<extra></extra>'
    )

# Build a line graph object with the given data and color
def create_line_graph(x, y, color):
    return go.Scatter(
        x=x,
        y=y,
        line=dict(color=color, width=2),
        hoverinfo='none'
    )

# Change settings for displaying the rangeslider based on the device viewing the webpage
# The rangeslider does not work on mobile devices, so it is set to be not visible in that case
def configure_rangeslider():
    if not is_mobile:
        return dict(
            visible=True,
            bgcolor=LIGHT_GRAY.color_to_str(alpha=0.2),
            range=[datetime.datetime(2020, 1, 8), datetime.datetime(2020, 12, 14)]
        )
    else:
        return dict(visible=False)

# Each time a user clicks a button to show a different graph, this function draws the appropriate graph on the figure
def generate_fig(show_downtown_cases=False, show_county_cases=False, show_county_deaths=False, show_sc_cases=False,
                 show_sc_deaths=False):

    # Create figure on which to draw graphs
    fig = go.Figure(
        layout=go.Layout(
            margin=go.layout.Margin(l=50, r=50, b=20, t=50),
            paper_bgcolor=TRANSPARENT,
            plot_bgcolor=TRANSPARENT,
            xaxis=dict(
                ticks='outside',
                tickcolor=WHITE,
                ticklen=5,
                tickfont=dict(
                    color=DIM_GRAY
                ),
                rangeslider=configure_rangeslider(),
                type='date',
                range=[datetime.datetime(2020, 4, 30), datetime.datetime(2020, 12, 14)]
            ),
            yaxis=dict(
                ticks='outside',
                tickcolor=WHITE,
                ticklen=5,
                tickfont=dict(
                    color=DIM_GRAY
                ),
                rangemode='tozero',
            ),
            hoverlabel=dict(
                bgcolor=WHITE,
                bordercolor=OFF_WHITE,
                font_size=10,
                font_family='Open Sans',
                font_color=BLACK
            ),
            autosize=True,
            dragmode=False,
            font_family='Open Sans',
            font_color=DIM_GRAY,
            spikedistance=1000,
            hovermode='x',
            shapes=class_mode_shapes + semester_shapes,
            annotations=class_mode_labels + semester_labels,
            showlegend=False,
            transition_duration=1000,
            transition_easing='exp-in-out',
        )
    )

    # Draw a bar graph of daily cases and a line graph of 7-day moving average of daily cases for Downtown Charleston
    if show_downtown_cases:
        fig.add_trace(create_bar_graph(
            x=downtown_charleston.get_daily_cases().index,
            y=downtown_charleston.get_daily_cases().clip(lower=0).values,
            color=TEAL,
            location='Downtown Charleston'
        ))

        fig.add_trace(create_line_graph(
            x=downtown_charleston.get_daily_cases_moving_avg(days=7).index,
            y=downtown_charleston.get_daily_cases_moving_avg(days=7).values,
            color=TEAL,
        ))

    # Draw a bar graph of daily cases and a line graph of 7-day moving average of daily cases for Charleston County
    if show_county_cases:
        fig.add_trace(create_bar_graph(
            x=charleston_county.get_daily_cases().index,
            y=charleston_county.get_daily_cases().clip(lower=0).values,
            color=BLUE_GREEN,
            location='Charleston County'
        ))

        fig.add_trace(create_line_graph(
            x=charleston_county.get_daily_cases_moving_avg(days=7).index,
            y=charleston_county.get_daily_cases_moving_avg(days=7).values,
            color=BLUE_GREEN,
        ))

    # Draw a bar graph of daily deaths and a line graph of 7-day moving average of daily deaths for Charleston County
    if show_county_deaths:
        fig.add_trace(create_bar_graph(
            x=charleston_county.get_daily_deaths().index,
            y=charleston_county.get_daily_deaths().clip(lower=0).values,
            color=BLUE_GREEN,
            location='Charleston County'
        ))

        fig.add_trace(create_line_graph(
            x=charleston_county.get_daily_deaths_moving_avg(days=7).index,
            y=charleston_county.get_daily_deaths_moving_avg(days=7).values,
            color=BLUE_GREEN
        ))

    # Draw a bar graph of daily cases and a line graph of 7-day moving average of daily cases for South Carolina
    if show_sc_cases:
        fig.add_trace(create_bar_graph(
            x=south_carolina.get_daily_cases().index,
            y=south_carolina.get_daily_cases().clip(lower=0).values,
            color=DARK_BLUE,
            location='South Carolina'
        ))

        fig.add_trace(create_line_graph(
            x=south_carolina.get_daily_cases_moving_avg(days=7).index,
            y=south_carolina.get_daily_cases_moving_avg(days=7).values,
            color=DARK_BLUE
        ))

    # Draw a bar graph of daily deaths and a line graph of 7-day moving average of daily deaths for South Carolina
    if show_sc_deaths:
        fig.add_trace(create_bar_graph(
            x=south_carolina.get_daily_deaths().index,
            y=south_carolina.get_daily_deaths().clip(lower=0).values,
            color=DARK_BLUE,
            location='South Carolina'
        ))

        fig.add_trace(create_line_graph(
            x=south_carolina.get_daily_deaths_moving_avg(days=7).index,
            y=south_carolina.get_daily_deaths_moving_avg(days=7).values,
            color=DARK_BLUE
        ))

    return fig



##### 6) Create an HTML layout for graph, numbers, and buttons to change the graph -------------------------------------

app.layout = html.Div([

    # Allow webpage to scale based on screen size
    html.Meta(
        name='viewport',
        content='width=device-width, initial-scale=1.0'
    ),

    # Provide Open Sans font
    html.Link(
        href='https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700;800&display=swap',
        rel='stylesheet'
    ),

    # Header bar containing logo
    html.Div([
        html.Img(src='assets/horizontal_logo_for_light_background.png', id='logo'),
        html.P('at College of Charleston', id='title')
    ], id='header'),

    # Body of webpage
    html.Div([

        # Container for graph portion of webpage
        html.Div([
            html.H2(id='graph-title', className='card-title'),
            dcc.Graph(
                id='graph',
                figure=generate_fig(),
                config={
                    'displayModeBar': False,
                    'showTips': False,
                    'responsive': True,
                    'autosizable': True,
                    'doubleClick': not is_mobile,
                }
            )
        ], id='graph-container', className='dashboard-card'),

        # Container for column of 'cards' shown to right of graph (or below graph on smaller screens)
        html.Div([

            # Card containing numbers and buttons for viewing data in Charleston County
            html.Div([
                html.H2('Charleston County', id='county-title', className='card-title'),
                html.Div([
                    html.P('{:,}'.format(charleston_county.get_total_cases()), className='number'),
                    html.P('Confirmed Cases', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-chs-cases')
                ], className='card-half'),
                html.Div([
                    html.P('{:,}'.format(charleston_county.get_total_deaths()), className='number'),
                    html.P('Reported Deaths', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-chs-deaths')
                ], className='card-half')
            ], className='dashboard-card sidebar-card remove-top-margin'),

            # Cards containing numbers and buttons for viewing data in South Carolina
            html.Div([
                html.H2('South Carolina', id='sc-title', className='card-title'),
                html.Div([
                    html.P('{:,}'.format(south_carolina.get_total_cases()), className='number'),
                    html.P('Confirmed Cases', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-sc-cases')
                ], className='card-half'),
                html.Div([
                    html.P('{:,}'.format(south_carolina.get_total_deaths()), className='number'),
                    html.P('Reported Deaths', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-sc-deaths')
                ], className='card-half'),
            ], className='dashboard-card sidebar-card'),

            # Card containing numbers and buttons for viewing data in Downtown Charleston
            html.Div([
                html.H2('Downtown Charleston', id='downtown-title', className='card-title'),
                html.Div([
                    html.P('{:,}'.format(downtown_charleston.get_total_cases()), className='number'),
                    html.P('Confirmed Cases', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-downtown-cases')
                ], className='card-full'),
            ], className='dashboard-card sidebar-card'),

            # Button linked to CofC's Back on the Bricks plan
            html.A([
                html.Div([
                    html.P('CofC Back on the Bricks Plan', className='link-card-text')
                ], className='dashboard-card sidebar-card link-card')
            ], href='https://cofc.edu/back-on-the-bricks/', target='_blank', className='no-underline'),

            # Button linked to COVID-19 information from SC DHEC
            html.A([
                html.Div([
                    html.P('SC DHEC COVID-19 Information', className='link-card-text')
                ], className='dashboard-card sidebar-card link-card remove-bottom-margin')
            ], href='https://www.scdhec.gov/infectious-diseases/viruses/coronavirus-disease-2019-covid-19',
            target='_blank', className='no-underline'),

        ], id='sidebar')

    ], id='body'),

    # Footer bar at bottom of webpage, containing links to 'About the Developer' and 'Disclaimer & Privacy Policy'
    html.Div([
        html.P('About the Developer', className='footer-items left-footer', id='open-about'),
        html.P('Disclaimer & Privacy Policy', className='footer-items right-footer', id='open-disclaimer')
    ], id='footer'),

    # Show this popup box when user clicks on 'About the Developer' in the footer bar
    html.Div([
        html.Div([
            html.H2('About the Developer', className='popup-title'),
            html.P('×', className='popup-close', id='close-about')
        ], className='popup-heading'),
        html.P([
            'This dashboard was developed by Connor Cozad, an undergraduate studying data science at the College of Charleston. Feel free to reach out via ',
            html.A('LinkedIn', href='https://www.linkedin.com/in/connor-cozad', target='_blank'),
            ' or by email at 23ccozad@gmail.com.',
            html.Br(),
            html.Br(),
            'Copyright © 2020 Connor Cozad'
        ],
        className='popup-body')
    ], id='popup-left', className='popup-box', style={'display': 'none'}),

    # Show this popup box when user clicks on 'Disclaimer & Privacy Policy' in the footer bar
    html.Div([
        html.Div([
            html.H2('Disclaimer & Privacy Policy', className='popup-title'),
            html.P('×', className='popup-close', id='close-disclaimer')
        ], className='popup-heading'),
        html.P([
            'This webpage is not affiliated with the College of Charleston (CofC), the City of Charleston, Charleston County, the State of South Carolina, or the South Carolina Department of Health and Environmental Control. Links to external websites do not indicate an affiliation.',
            html.Br(), html.Br(),
            'Data presented on this webpage is provided by ',
            html.A('JHU CSSE COVID-19 Data', href='https://github.com/CSSEGISandData/COVID-19', target='_blank'),
            ' and ',
            html.A('SC DHEC COVID-19 Open Data', href='https://scdhec-covid-19-open-data-sc-dhec.hub.arcgis.com/', target='_blank'),
            '. The developer of this webpage is not liable nor responsible for the accuracy of this data, nor any decisions made based on the presentation of this data.',
            html.Br(), html.Br(),
            'This website uses Google Analytics scripts and cookies to collect information about users and how they interact with this website. This information includes the user’s IP address. The collected information allows the developer to make improvements to this website. The developer does not share this information with third parties. Users may click the following link to learn more about ',
            html.A('Google Analytics Terms of Service.', href='https://marketingplatform.google.com/about/analytics/terms/us/', target='_blank'),
            ' Users may use this browser tool to choose to ',
            html.A('opt-out of Google Analytics.', href='https://tools.google.com/dlpage/gaoptout?hl=en', target='_blank'),
            ' Users may also use the instructions at the following link to ',
            html.A('disable cookies in their browser', href='https://www.avast.com/c-enable-disable-cookies', target='_blank'),
            '. For more information about the privacy policy, contact the developer by email at 23ccozad@gmail.com.'
        ], className='popup-body'),
    ], id='popup-right', className='popup-box', style={'display': 'none'})
])



##### 7) Callbacks to change the graphs upon user's button click -------------------------------------------------------

# The on_click() function is called anytime one of the HTML elements in the input list is clicked
# All of the HTML elements in the output list are assigned new values based on which input was triggered
@app.callback(
    [
        dash.dependencies.Output('graph', 'figure'),
        dash.dependencies.Output('graph-title', 'children'),
        dash.dependencies.Output('graph-title', 'id'),
        dash.dependencies.Output('show-downtown-cases', 'className'),
        dash.dependencies.Output('show-sc-deaths', 'className'),
        dash.dependencies.Output('show-sc-cases', 'className'),
        dash.dependencies.Output('show-chs-deaths', 'className'),
        dash.dependencies.Output('show-chs-cases', 'className'),
    ], [
        dash.dependencies.Input('show-downtown-cases', 'n_clicks'),
        dash.dependencies.Input('show-sc-deaths', 'n_clicks'),
        dash.dependencies.Input('show-sc-cases', 'n_clicks'),
        dash.dependencies.Input('show-chs-deaths', 'n_clicks'),
        dash.dependencies.Input('show-chs-cases', 'n_clicks'),
    ]
)

# This function is called whenever one of the above input objects is triggered by a mouse click
def on_click(btn1, btn2, btn3, btn4, btn5):

    # Determine the ID of the button that was clicked
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    # The HTML classes to assign to buttons.
    # The buttons that were not clicked are assigned the normal_class. The button that was clicked is assigned selected_class
    selected_class = 'toggle-graph-button selected-graph-button'
    normal_class = 'toggle-graph-button'

    # Based on which button was clicked, the following changes occur in the interface:
    # 1) fig: A new figure is created, showing the graph the user requested by clicking the button
    # 2) title: Change the title of the graph
    # 3) Change the background color of the title of the graph by changing the title's ID. Colors are unique to each
    #    location (Charleston County, South Carolina, etc.). The colors associated are changed assigning the element a
    #    new ID, which can be seen in style.css
    # 4) Change the style of the button that was clicked to show that it has been selected. This is done by changing the
    #    button's class to 'selected_class'. All other buttons are given the appearance that they were not selected by
    #    being assigned 'normal_class'. These classes can be viewed in style.css
    # Note: The order of items in return statement align with order of items in list of outputs at beginning of callback
    if 'show-downtown-cases' in changed_id:
        fig = generate_fig(show_downtown_cases=True)
        title = 'Daily Confirmed Cases in Downtown Charleston'
        return fig, title, 'downtown-title', selected_class, normal_class, normal_class, normal_class, normal_class
    elif 'show-chs-cases' in changed_id:
        fig = generate_fig(show_county_cases=True)
        title = 'Daily Confirmed Cases in Charleston County'
        return fig, title, 'county-title', normal_class, normal_class, normal_class, normal_class, selected_class
    elif 'show-chs-deaths' in changed_id:
        fig = generate_fig(show_county_deaths=True)
        title = 'Daily Deaths in Charleston County'
        return fig, title, 'county-title', normal_class, normal_class, normal_class, selected_class, normal_class
    elif 'show-sc-cases' in changed_id:
        fig = generate_fig(show_sc_cases=True)
        title = 'Daily Confirmed Cases in South Carolina'
        return fig, title, 'sc-title', normal_class, normal_class, selected_class, normal_class, normal_class
    elif 'show-sc-deaths' in changed_id:
        fig = generate_fig(show_sc_deaths=True)
        title = 'Daily Deaths in South Carolina'
        return fig, title, 'sc-title', normal_class, selected_class, normal_class, normal_class, normal_class

# Show the disclaimer and privacy policy popup shown when 'Disclaimer & Privacy Policy' is clicked
# Also, close the popup when the X button is clicked
@app.callback(
    dash.dependencies.Output('popup-right', 'style'),
    [
        dash.dependencies.Input('open-disclaimer', 'n_clicks'),
        dash.dependencies.Input('close-disclaimer', 'n_clicks')
    ]
)

# This function is called whenever the 'Disclaimer & Privacy Policy' button in the footer bar or the 'X' in the popup
# window is clicked
def right_popup(btn1, btn2):

    # Determine the ID of the button that was clicked (either 'open-disclaimer' or 'close-disclaimer')
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0].split('.')[0]

    # Change the display of the popup based on the ID of the button that triggered this function
    if changed_id == 'open-disclaimer':
        return {'display': 'block'}
    elif changed_id == 'close-disclaimer':
        return {'display': 'none'}

# Show the 'About' popup shown when 'About the Developer' is clicked
# Also, close the popup when the X button is clicked
@app.callback(
    dash.dependencies.Output('popup-left', 'style'),
    [dash.dependencies.Input('open-about', 'n_clicks'),
     dash.dependencies.Input('close-about', 'n_clicks')]
)

# This function is called whenever the 'About the Developer' button in the footer bar or the 'X' in the popup
# window is clicked
def left_popup(btn1, btn2):

    # Determine the ID of the button that was clicked (either 'open-disclaimer' or 'close-disclaimer')
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0].split('.')[0]

    # Change the display of the popup based on the ID of the button that triggered this function
    if changed_id == 'open-about':
        return {'display': 'block'}
    elif changed_id == 'close-about':
        return {'display': 'none'}

if __name__ == '__main__':
    app.run_server()
