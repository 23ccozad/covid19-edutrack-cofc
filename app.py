import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import urllib.error
import datetime
import re
from flask import request

external_scripts = [
    'https://www.googletagmanager.com/gtag/js?id=UA-174296614-1',
]

app = dash.Dash(__name__, external_scripts=external_scripts)
server = app.server
app.title = 'COVID-19 EduTrack @ CofC'

is_mobile = None

@server.before_request
def before_request():
    agent = request.headers.get("User_Agent")
    mobile_string = "(?i)android|fennec|iemobile|iphone|opera (?:mini|mobi)|mobile"
    re_mobile = re.compile(mobile_string)
    global is_mobile
    is_mobile = len(re_mobile.findall(agent)) > 0

data_url_root = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/"
today = datetime.datetime.utcnow()

days = 0
us_current = None
while us_current is None:
    try:
        date = (today + datetime.timedelta(days=days)).strftime("%m-%d-%Y")
        current_data_url = data_url_root + "csse_covid_19_daily_reports/" + date + ".csv"
        us_current = pd.read_csv(current_data_url)
    except urllib.error.HTTPError:
        days -= 1
        pass


sc_current = us_current.loc[us_current['Province_State'] == 'South Carolina']
sc_total_cases = sc_current['Confirmed'].sum()
sc_total_deaths = sc_current['Deaths'].sum()

chs_current = sc_current.loc[sc_current['Admin2'] == 'Charleston']
chs_total_cases = chs_current['Confirmed'].values[0]
chs_total_deaths = chs_current['Deaths'].values[0]

historical_cases_url = data_url_root + "csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
us_historical_cases = pd.read_csv(historical_cases_url)

sc_historical_cases = us_historical_cases.loc[us_historical_cases['Province_State'] == 'South Carolina']
chs_historical_cases = sc_historical_cases.loc[us_historical_cases['Admin2'] == 'Charleston']

sc_historical_cases = sc_historical_cases.sum()[11:].to_frame()
sc_historical_cases.reset_index(drop=False, inplace=True)
sc_historical_cases.columns = ['Date', 'Confirmed']
sc_historical_cases['Date'] = pd.to_datetime(sc_historical_cases['Date'])
sc_historical_cases['Daily_Confirmed'] = sc_historical_cases['Confirmed'].diff()
sc_historical_cases['Daily_Confirmed'] = sc_historical_cases['Daily_Confirmed'].clip(lower=0)
sc_historical_cases['Daily_Confirmed_MA'] = sc_historical_cases['Daily_Confirmed'].rolling(7).mean()

chs_historical_cases = chs_historical_cases.transpose()
chs_historical_cases = chs_historical_cases.iloc[11:]
chs_historical_cases.reset_index(drop=False, inplace=True)
chs_historical_cases.columns = ['Date', 'Confirmed']
chs_historical_cases['Date'] = pd.to_datetime(chs_historical_cases['Date'])
chs_historical_cases['Daily_Confirmed'] = chs_historical_cases['Confirmed'].diff()
chs_historical_cases['Daily_Confirmed'] = chs_historical_cases['Daily_Confirmed'].clip(lower=0)
chs_historical_cases['Daily_Confirmed_MA'] = chs_historical_cases['Daily_Confirmed'].rolling(7).mean()

historical_deaths_url = data_url_root + "csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
us_historical_deaths = pd.read_csv(historical_deaths_url)

sc_historical_deaths = us_historical_deaths.loc[us_historical_deaths['Province_State'] == 'South Carolina']
chs_historical_deaths = sc_historical_deaths.loc[us_historical_deaths['Admin2'] == 'Charleston']

sc_historical_deaths = sc_historical_deaths.sum()[12:].to_frame()
sc_historical_deaths.reset_index(drop=False, inplace=True)
sc_historical_deaths.columns = ['Date', 'Deaths']
sc_historical_deaths['Date'] = pd.to_datetime(sc_historical_deaths['Date'])
sc_historical_deaths['Daily_Deaths'] = sc_historical_deaths['Deaths'].diff()
sc_historical_deaths['Daily_Deaths'] = sc_historical_deaths['Daily_Deaths'].clip(lower=0)
sc_historical_deaths['Daily_Deaths_MA'] = sc_historical_deaths['Daily_Deaths'].rolling(7).mean()

chs_historical_deaths = chs_historical_deaths.transpose()
chs_historical_deaths = chs_historical_deaths.iloc[12:]
chs_historical_deaths.reset_index(drop=False, inplace=True)
chs_historical_deaths.columns = ['Date', 'Deaths']
chs_historical_deaths['Date'] = pd.to_datetime(chs_historical_deaths['Date'])
chs_historical_deaths['Daily_Deaths'] = chs_historical_deaths['Deaths'].diff()
chs_historical_deaths['Daily_Deaths'] = chs_historical_deaths['Daily_Deaths'].clip(lower=0)
chs_historical_deaths['Daily_Deaths_MA'] = chs_historical_deaths['Daily_Deaths'].rolling(7).mean()

class_mode_intervals = pd.read_csv('assets/intervals.csv')
class_mode_intervals['Start_Date'] = pd.to_datetime(class_mode_intervals['Start_Date'])
class_mode_intervals['End_Date'] = pd.to_datetime(class_mode_intervals['End_Date'])

layout = go.Layout(
    margin=go.layout.Margin(l=50, r=50, b=20, t=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)

class_mode_shapes = []
class_mode_labels = []
for row in class_mode_intervals.itertuples():
    label = row[2]
    start_date = row[3]
    end_date = row[4]
    class_mode_shapes.append(dict(
        fillcolor="rgba(211, 211, 211, 0.2)",
        line={"width": 0},
        type="rect",
        x0=start_date,
        x1=end_date,
        xref="x",
        y0=0,
        y1=1.0,
        yref="paper"
    ))
    class_mode_labels.append(dict(
        x=start_date + (end_date - start_date) / 2,
        showarrow=False,
        y=1.0,
        ax=0,
        text=label,
        xref="x",
        yanchor="top",
        yref="paper"
    ))

semester_shapes=[]
semester_labels=[]
for semester in class_mode_intervals["Semester"].unique():
    all_intervals_in_semester = class_mode_intervals.loc[class_mode_intervals["Semester"] == semester]
    start_date = all_intervals_in_semester['Start_Date'].min()
    end_date = all_intervals_in_semester['End_Date'].max()
    semester_shapes.append(dict(
        fillcolor="rgba(211, 211, 211, 0.5)",
        line={"width": 0},
        type="rect",
        x0=start_date,
        x1=end_date,
        xref="x",
        y0=1.0,
        y1=1.1,
        yref="paper"
    ))
    semester_labels.append(dict(
        x=start_date + (end_date - start_date) / 2,
        showarrow=False,
        y=1.05,
        ax=0,
        text=semester,
        xref="x",
        yanchor="middle",
        yref="paper"
    ))

def generate_fig(show_chs_cases=False, show_chs_deaths=False, show_sc_cases=False, show_sc_deaths=False):
    fig = go.Figure(
        layout=layout
    )

    if show_chs_cases:
        fig.add_trace(go.Bar(
            x=chs_historical_cases["Date"],
            y=chs_historical_cases["Daily_Confirmed"],
            marker = dict(
                color='rgba(5, 102, 87, 0.4)',
                line_width=0
            ),
            hovertemplate=
            '<span style="font-size: 20px; font-weight: 900; color: #056657">%{y:,}</span>' +
            '<span style="font-size: 12px; font-weight: 500; color: #555555"> cases</span>' +
            '<span style="color: gray"><br>%{x}' +
            '<br>Charleston County, SC</span>' +
            '<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=chs_historical_cases["Date"],
            y=chs_historical_cases["Daily_Confirmed_MA"],
            line=dict(color='#056657', width=2),
            hoverinfo='none'
        ))

    if show_chs_deaths:
        fig.add_trace(go.Bar(
            x=chs_historical_deaths["Date"],
            y=chs_historical_deaths["Daily_Deaths"],
            marker = dict(
                color='rgba(5, 102, 87, 0.4)',
                line_width=0
            ),
            hovertemplate=
            '<span style="font-size: 20px; font-weight: 900; color: #056657">%{y:,}</span>' +
            '<span style="font-size: 12px; font-weight: 500; color: #555555"> deaths</span>' +
            '<span style="color: gray"><br>%{x}' +
            '<br>Charleston County, SC</span>' +
            '<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=chs_historical_deaths["Date"],
            y=chs_historical_deaths["Daily_Deaths_MA"],
            line=dict(color='#056657', width=2),
            hoverinfo='none'
        ))

    if show_sc_cases:
        fig.add_trace(go.Bar(
            x=sc_historical_cases["Date"],
            y=sc_historical_cases["Daily_Confirmed"],
            marker=dict(
                color='rgba(0, 51, 102, 0.4)',
                line_width=0
            ),
            hovertemplate=
            '<span style="font-size: 20px; font-weight: 900; color: #003366">%{y:,}</span>' +
            '<span style="font-size: 12px; font-weight: 500; color: #555555"> cases</span>' +
            '<span style="color: gray"><br>%{x}' +
            '<br>South Carolina</span>' +
            '<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=sc_historical_cases["Date"],
            y=sc_historical_cases["Daily_Confirmed_MA"],
            line=dict(color='#003366', width=2),
            hoverinfo='none'
        ))

    if show_sc_deaths:
        fig.add_trace(go.Bar(
            x=sc_historical_deaths["Date"],
            y=sc_historical_deaths["Daily_Deaths"],
            marker=dict(
                color='rgba(0, 51, 102, 0.4)',
                line_width=0
            ),
            hovertemplate=
            '<span style="font-size: 20px; font-weight: 900; color: #003366">%{y:,}</span>' +
            '<span style="font-size: 12px; font-weight: 500; color: #555555"> deaths</span>' +
            '<span style="color: gray"><br>%{x}' +
            '<br>South Carolina</span>' +
            '<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=sc_historical_deaths["Date"],
            y=sc_historical_deaths["Daily_Deaths_MA"],
            line=dict(color='#003366', width=2),
            hoverinfo='none'
        ))

    def configure_rangeslider():
        if not is_mobile:
            return dict(
                visible=True,
                bgcolor="rgba(211, 211, 211, 0.2)",
                range=[datetime.datetime(2020, 1, 8), datetime.datetime(2020, 12, 14)]
            )
        else:
            return dict(visible=False)

    fig.update_layout(
        autosize=True,
        dragmode=False,
        font_family="Open Sans",
        font_color="#222222",
        spikedistance=1000,
        xaxis=dict(
            ticks="outside",
            tickcolor='white',
            ticklen=5,
            tickfont=dict(
                color="dimgray"
            ),
            rangeslider=configure_rangeslider(),
            type="date",
            # showline=True,
            # spikethickness=1.5,
            # spikesnap='cursor',
            # spikedash="solid",
            # spikecolor="#AFAFAF",
            # spikemode="across",
        ),
        yaxis=dict(
            ticks="outside",
            tickcolor='white',
            ticklen=5,
            tickfont=dict(
                color="dimgray"
            ),
        ),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="rgb(248, 248, 248)",
            font_size=10,
            font_family="Open Sans",
            font_color='black'
        ),
        hovermode='x'
    )

    fig.update_yaxes(
        rangemode="tozero",
    )

    fig.update_xaxes(
        range=[datetime.datetime(2020, 4, 30), datetime.datetime(2020, 12, 14)]
    )

    fig.update_layout(
        shapes=class_mode_shapes + semester_shapes,
        annotations=class_mode_labels + semester_labels,
        showlegend=False,
        transition_duration=1000,
        transition_easing='exp-in-out',
    )

    return fig

app.layout = html.Div(children=[

    html.Meta(
        name='viewport',
        content='width=device-width, initial-scale=1.0'
    ),

    html.Link(
        href='https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700;800&display=swap',
        rel="stylesheet"
    ),

    html.Div([
        html.Img(src='assets/horizontal_logo_for_light_background.png', id='logo'),
        html.P('at College of Charleston', id='title')
    ], id='header'),

    html.Div([

        html.Div([
            html.H2(children='', id='graph-title', className='card-title'),
            dcc.Graph(
                id='graph',
                figure=generate_fig(),
                config={
                    "displayModeBar": False,
                    "showTips": False,
                    "responsive": True,
                    "autosizable": True,
                    "doubleClick": not is_mobile,
                }
            )
        ], id='graph-container', className='dashboard-card'),

        html.Div([

            html.Div([
                html.H2(children='College of Charleston', id='cofc-title', className='card-title'),
                html.Div([
                    html.P(children='0', className='number'),
                    html.P(children='Confirmed Cases', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-cofc-cases', disabled=True)
                ], className='card-deaths'),
                html.Div([
                    html.P(children='0', className='number'),
                    html.P(children='Reported Deaths', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-cofc-deaths', disabled=True)
                ], className='card-cases')
            ], className='dashboard-card sidebar-card remove-top-margin'),

            html.Div([
                html.H2(children='Charleston County', id='chs-title', className='card-title'),
                html.Div([
                    html.P(children="{:,}".format(chs_total_cases), className='number'),
                    html.P(children='Confirmed Cases', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-chs-cases')
                ], className='card-deaths'),
                html.Div([
                    html.P(children="{:,}".format(chs_total_deaths), className='number'),
                    html.P(children='Reported Deaths', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-chs-deaths')
                ], className='card-cases')
            ], className='dashboard-card sidebar-card'),

            html.Div([
                html.H2(children='South Carolina', id='sc-title', className='card-title'),
                html.Div([
                    html.P(children="{:,}".format(sc_total_cases), className='number'),
                    html.P(children='Confirmed Cases', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-sc-cases')
                ], className='card-deaths'),
                html.Div([
                    html.P(children="{:,}".format(sc_total_deaths), className='number'),
                    html.P(children='Reported Deaths', className='label'),
                    html.Button('Show Graph', className='toggle-graph-button', id='show-sc-deaths')
                ], className='card-cases')
            ], className='dashboard-card sidebar-card'),

            html.A([
                html.Div([
                    html.P(["CofC Back on the Bricks Plan"], className='link-card-text')
                ], className='dashboard-card sidebar-card link-card')
            ], href='https://cofc.edu/back-on-the-bricks/', target="_blank", className="no-underline"),

            html.A([
                html.Div([
                    html.P(["SC DHEC COVID-19 Information"],
                           className='link-card-text')
                ], className='dashboard-card sidebar-card link-card remove-bottom-margin')
            ], href='https://www.scdhec.gov/infectious-diseases/viruses/coronavirus-disease-2019-covid-19',
            target="_blank",
            className="no-underline"),

        ], id='sidebar')

    ], id='body'),

    html.Div([
        html.P('About the Developer', className='footer-items left-footer', id='open-about'),
        html.P('Disclaimer & Privacy Policy', className='footer-items right-footer', id='open-disclaimer')
    ], id='footer'),

    html.Div([
        html.Div([
            html.H2('About the Developer', className='popup-title'),
            html.P('×', className='popup-close', id='close-about')
        ], className="popup-heading"),
        html.P([
            'This dashboard was developed by Connor Cozad, an undergraduate studying data science at the College of '
            'Charleston. Feel free to reach out via ',
            html.A('LinkedIn', href='https://www.linkedin.com/in/connor-cozad', target='_blank'),
            ' or by email at 23ccozad@gmail.com.',
            html.Br(), html.Br(),
            'Copyright © 2020 Connor Cozad'
        ],
        className='popup-body')
    ], id="popup-left", className="popup-box", style={'display': 'none'}),

    html.Div([
        html.Div([
            html.H2('Disclaimer & Privacy Policy', className='popup-title'),
            html.P('×', className='popup-close', id='close-disclaimer')
        ], className="popup-heading"),
        html.P([
            'This webpage is not affiliated with the College of Charleston, the City of Charleston, Charleston County, '
            'the State of South Carolina, or the South Carolina Department of Health and Environmental Control. Links to external websites do not indicate an affiliation.',
            html.Br(), html.Br(),
            'Data presented on this webpage is provided by ',
            html.A('JHU CSSE COVID-19 Data', href='https://github.com/CSSEGISandData/COVID-19', target='_blank'),
            '. The developer is not liable nor responsible for the accuracy of this data, nor any decisions made based '
            'on the presentation of this data.',
            html.Br(), html.Br(),
            'This website uses Google Analytics scripts and cookies to collect information about users and how they '
            'interact with this website. This information includes the user’s IP address. The collected information '
            'allows the developer to make improvements to this website. The developer does not share this information '
            'with third parties. Users may click the following link to learn more about ',
            html.A('Google Analytics Terms of Service.', href='https://marketingplatform.google.com/about/analytics/terms/us/', target='_blank'),
            ' Users may use the browser tool at the following link to ',
            html.A('opt-out of Google Analytics.', href='https://tools.google.com/dlpage/gaoptout?hl=en', target='_blank'),
            ' Users may also use the instructions at the following link to ',
            html.A('disable cookies in their browser', href='https://www.avast.com/c-enable-disable-cookies', target='_blank'),
            '. For more information about the privacy policy, contact the developer by email at 23ccozad@gmail.com.'
        ], className='popup-body'),
    ], id="popup-right", className="popup-box", style={'display': 'none'})
])

@app.callback(
    [dash.dependencies.Output('graph', 'figure'),
     dash.dependencies.Output('graph-title', 'children'),
     dash.dependencies.Output('graph-title', 'id'),
     dash.dependencies.Output('show-sc-deaths', 'className'),
     dash.dependencies.Output('show-sc-cases', 'className'),
     dash.dependencies.Output('show-chs-deaths', 'className'),
     dash.dependencies.Output('show-chs-cases', 'className')],
    [dash.dependencies.Input('show-sc-deaths', 'n_clicks'),
     dash.dependencies.Input('show-sc-cases', 'n_clicks'),
     dash.dependencies.Input('show-chs-deaths', 'n_clicks'),
    dash.dependencies.Input('show-chs-cases', 'n_clicks')]
)
def on_click(btn1, btn2, btn3, btn4):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    selected_class = 'toggle-graph-button selected-graph-button'
    normal_class = 'toggle-graph-button'
    if 'show-chs-cases' in changed_id:
        fig = generate_fig(show_chs_cases=True)
        title = "Daily Confirmed Cases in Charleston County"
        return fig, title, "chs-title", normal_class, normal_class, normal_class, selected_class
    elif 'show-chs-deaths' in changed_id:
        fig = generate_fig(show_chs_deaths=True)
        title = "Daily Deaths in Charleston County"
        return fig, title, "chs-title", normal_class, normal_class, selected_class, normal_class
    elif 'show-sc-cases' in changed_id:
        fig = generate_fig(show_sc_cases=True)
        title = "Daily Confirmed Cases in South Carolina"
        return fig, title, "sc-title", normal_class, selected_class, normal_class, normal_class
    elif 'show-sc-deaths' in changed_id:
        fig = generate_fig(show_sc_deaths=True)
        title = "Daily Deaths in South Carolina"
        return fig, title, "sc-title", selected_class, normal_class, normal_class, normal_class

@app.callback(
    dash.dependencies.Output('popup-right', 'style'),
    [dash.dependencies.Input('open-disclaimer', 'n_clicks'),
     dash.dependencies.Input('close-disclaimer', 'n_clicks')]
)
def right_popup(btn1, btn2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0].split('.')[0]
    if changed_id == 'open-disclaimer':
        return {'display': 'block'}
    elif changed_id == 'close-disclaimer':
        return {'display': 'none'}

@app.callback(
    dash.dependencies.Output('popup-left', 'style'),
    [dash.dependencies.Input('open-about', 'n_clicks'),
     dash.dependencies.Input('close-about', 'n_clicks')]
)
def left_popup(btn1, btn2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0].split('.')[0]
    if changed_id == 'open-about':
        return {'display': 'block'}
    elif changed_id == 'close-about':
        return {'display': 'none'}


if __name__ == '__main__':
    app.run_server()
