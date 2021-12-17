import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

# Data - CSV
csv = 'light_sound.csv'
header_list = ['Time', 'Luminosidad', 'Sonido']

tabs_styles = {
    "flexDirection": "row",
}
tab_style = {
    "padding": "1.3vh",
    "color": 'black',
    "fontSize": '.9vw',
    "backgroundColor": 'rgba(242, 242, 242, 0.0)',
    'borderBottom': '1px black solid',

}

tab_selected_style = {
    "fontSize": '.9vw',
    "color": 'black',
    "padding": "1.3vh",
    'fontWeight': 'bold',
    "backgroundColor": '#b6c0c8',
    'borderTop': '1px black solid',
    'borderLeft': '1px black solid',
    'borderRight': '1px black solid',
    'borderRadius': '0px 0px 0px 0px',
}

tab_selected_style1 = {
    "fontSize": '.9vw',
    "color": '#F4F4F4',
    "padding": "1.3vh",
    'fontWeight': 'bold',
    "backgroundColor": '#566573',
    'borderTop': '1px white solid',
    'borderLeft': '1px white solid',
    'borderRight': '1px white solid',
    'borderRadius': '0px 0px 0px 0px',
}

chart_humidity = dcc.Graph(id='humidity_chart',
                           animate=True,
                           config={'displayModeBar': 'hover'},
                           className='chart_width'),

chart_temperature = dcc.Graph(id='temperature_chart',
                              animate=True,
                              config={'displayModeBar': 'hover'},
                              className='chart_width')

# Umbrales de tolerancia, y razonables
limite_inferior_luz = 5
limite_superior_luz = 20

limite_inferior_sonido = 5
limite_superior_sonido = 20


def semaforo_factory(limite_inferior, limite_superior):
    semaforo = html.Div([
        html.Div([
            html.Div([html.H5("Peligro", style={"marginBottom": '0px', 'color': 'black'})],
                     className="cell cell-header cell-header-red  card_container four columns"),
            html.Div([html.H5("Alerta", style={"marginBottom": '0px', 'color': 'black'})],
                     className="cell cell-header cell-header-yellow  card_container four "
                               "columns"),
            html.Div([html.H5("Correcto", style={"marginBottom": '0px', 'color': 'black'})],
                     className="cell cell-header cell-header-green card_container four columns")
        ], className="row flex display"
        ),
        html.Div([
            html.Div([html.H5(f"< {limite_inferior}", style={"marginBottom": '0px', 'color': 'red'})],
                     className="cell cell-body cell-body-red danger card_container four columns"),
            html.Div(
                [html.H5(f"{limite_inferior} - {limite_superior}", style={"marginBottom": '0px', 'color': '#FCDE22'})],
                className="cell cell-body cell-body-yellow warning card_container four "
                          "columns"),
            html.Div([html.H5(f"{limite_superior} <", style={"marginBottom": '0px', 'color': '#109D55'})],
                     className="cell cell-body cell-body-green success card_container four columns")
        ], className="row flex display"
        )
    ], className="table row flex display")
    return semaforo

def kpi_color(valor,umbral_minimo, umbral_maximo):
    color = "#E0E0E0"
    if (valor < umbral_minimo):
        color ="#FF0000"
    elif (umbral_minimo < valor < umbral_maximo):
        color = "#FCDE22"
    else:
        color = "#109D55"
    return color

app.layout = html.Div([
    html.Div(id='background_image'),
    html.Div([
        dcc.Interval(id='update_date_time',
                     interval=1000,
                     n_intervals=0),
    ]),

    html.Div([

        # Cabecera
        html.Div([
            html.Div([
                html.H6('E12 - Sensores',
                        style={
                            'lineHeight': '1',
                            'color': 'white'},
                        className='adjust_title six columns'
                        ),
                html.Div([
                    html.Div(id='update',
                             className='image_grid six columns'),
                    html.H6(id='get_date_time',
                            style={
                                'lineHeight': '1',
                                'color': 'white'},
                            className='adjust_date_time'
                            )
                ], className='temp_card1'),
            ], className='adjust_title_and_date_time_two_columns')
        ], className='container_title_date_time twelve columns')
    ], className="row flex-display"),
    html.Div([
        dcc.Interval(id='update_chart',
                     interval=1000,
                     n_intervals=0),
    ]),

    html.Div([
        html.Div([
            # Tarjetas: Luminosidad e Intensidad de sonido
            html.Div([
                #html.Div(id='text1', className='grid_height'),
                html.Div(id='text2', className='grid_height'),
            ], className='grid_two_column'),

            html.Div([
                dcc.Tabs(id="tabs-styled-with-inline",  # value='chart_temperature',
                         children=[
                             dcc.Tab(
                                 children=[
                                     # Gráfico de lineas + KPI + Semáforo + Imagen
                                     html.Div([
                                         # 8 columnas
                                         html.Div([
                                             # Gráfico de lineas
                                             dcc.Graph(id='humidity_chart',
                                                       animate=True,
                                                       config={'displayModeBar': 'hover'},
                                                       className='chart_width'),
                                         ], className="seven columns"),
                                         # 4 columnas
                                         html.Div([
                                             html.Div([
                                                 html.Div([
                                                     # KPI
                                                     html.Div([
                                                         html.Div(id='text1', className='grid_height'),
                                                     ], className="twelve columns"),
                                                 ], className="row flex display"),
                                                 # Semáforo
                                                 html.Div([
                                                     html.Div([
                                                         semaforo_factory("5 LUX", "20 LUX")
                                                     ], className="twelve columns"),
                                                 ], className="row flex display"),
                                                 # Imagen
                                                 html.Div([

                                                 ], className="row flex display"),
                                             ], className="row flex display"),
                                         ], className="five columns"),
                                     ], className="row flex display"),
                                 ],
                                 label='Luminosidad',
                                 # value='chart_humidity',
                                 style=tab_style,
                                 selected_style=tab_selected_style,
                                 className='font_size'),
                             dcc.Tab(chart_temperature,
                                     label='Intensidad del sonido',
                                     value='chart_temperature',
                                     style=tab_style,
                                     selected_style=tab_selected_style,
                                     className='font_size'),
                         ], style=tabs_styles,
                         colors={"border": None,
                                 "primary": None,
                                 "background": None}),

            ], className='create_container3 twelve columns'),
        ], className='adjust_grids'),
    ], className="row flex-display"),

], id="mainContainer",
    style={"display": "flex", "flexDirection": "column"})


# Usado para cambiar la imagen de fondo
@app.callback(Output('background_image', 'children'),
              [Input('update_chart', 'n_intervals')])
def update_graph(n_intervals):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_time = df['Time'].tail(1).iloc[0]
    get_temp = df['Luminosidad'].tail(1).iloc[0].astype(float)
    if n_intervals == 0:
        raise PreventUpdate

    if get_temp >= 21:

        # Cambiarlo por lugar con mucha luz
        return [
            html.Div(style={'backgroundImage': 'url("/assets/sunny.jpg")',
                            'height': '100vh',
                            'backgroundRepeat': 'no-repeat',
                            'backgroundSize': 'auto'
                            }),
        ]

    elif get_temp < 21:
        # Cambiarlo por lugar oscuro / semáforo
        return [
            html.Div(style={'backgroundImage': 'url("/assets/cloudy.jpg")',
                            'height': '100vh',
                            'backgroundRepeat': 'no-repeat',
                            'backgroundSize': 'auto'
                            },
                     ),

        ]


@app.callback(Output('get_date_time', 'children'),
              [Input('update_date_time', 'n_intervals')])
def update_graph(n_intervals):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    if n_intervals == 0:
        raise PreventUpdate

    return [
        html.Div(dt_string),
    ]


@app.callback(Output('humidity_chart', 'figure'),
              [Input('update_chart', 'n_intervals')])
def update_graph(n_intervals):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_time = df['Time'].tail(20)
    get_light_level = df['Luminosidad'].tail(20)
    if n_intervals == 0:
        raise PreventUpdate

    return {
        'data': [go.Scatter(
            x=get_time,
            y=get_light_level,
            mode='markers+lines',
            line=dict(width=3, color='#D35400'),
            marker=dict(size=7, symbol='circle', color='#D35400',
                        line=dict(color='#D35400', width=2)
                        ),

            hoverinfo='text',
            hovertext=
            '<b>Time</b>: ' + get_time.astype(str) + '<br>' +
            '<b>Humidity</b>: ' + [f'{x:,.2f}%' for x in get_light_level] + '<br>'

        )],

        'layout': go.Layout(
            # paper_bgcolor = 'rgba(0,0,0,0)',
            # plot_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor='rgba(255, 255, 255, 0.0)',
            paper_bgcolor='rgba(255, 255, 255, 0.0)',
            title={
                'text': '',

                'y': 0.97,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont={
                'color': 'black',
                'size': 17},

            hovermode='closest',
            margin=dict(t=25, r=0, l=50),

            xaxis=dict(range=[min(get_time), max(get_time)],
                       title='<b>Tiempo</b>',
                       color='black',
                       showline=True,
                       showgrid=False,
                       linecolor='black',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Arial',
                           size=12,
                           color='black')

                       ),

            yaxis=dict(range=[min(get_light_level) - 1, max(get_light_level) + 1],
                       title='<b>Luminosidad</b>',
                       color='black',
                       showline=True,
                       showgrid=True,
                       linecolor='black',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Arial',
                           size=12,
                           color='black')

                       ),

            legend={
                'orientation': 'h',
                'bgcolor': '#F2F2F2',
                'x': 0.5,
                'y': 1.25,
                'xanchor': 'center',
                'yanchor': 'top'},
            font=dict(
                family="sans-serif",
                size=12,
                color='black')

        )

    }


@app.callback(Output('temperature_chart', 'figure'),
              [Input('update_chart', 'n_intervals')])
def update_graph(n_intervals):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_time = df['Time'].tail(20)
    get_sound_level = df['Sonido'].tail(20)
    if n_intervals == 0:
        raise PreventUpdate

    return {
        'data': [go.Scatter(
            x=get_time,
            y=get_sound_level,
            mode='markers+lines',
            line=dict(width=3, color='#CA23D5'),
            marker=dict(size=7, symbol='circle', color='#CA23D5',
                        line=dict(color='#CA23D5', width=2)
                        ),

            hoverinfo='text',
            hovertext=
            '<b>Tiempo</b>: ' + get_time.astype(str) + '<br>' +
            '<b>Intensidad de sonido</b>: ' + [f'{x:,.2f}°C' for x in get_sound_level] + '<br>'

        )],

        'layout': go.Layout(
            plot_bgcolor='rgba(255, 255, 255, 0.0)',
            paper_bgcolor='rgba(255, 255, 255, 0.0)',
            title={
                'text': '',

                'y': 0.97,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont={
                'color': 'black',
                'size': 17},

            hovermode='closest',
            margin=dict(t=25, r=0, l=50),

            xaxis=dict(range=[min(get_time), max(get_time)],
                       title='<b>Tiempo</b>',
                       color='black',
                       showline=True,
                       showgrid=False,
                       linecolor='black',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Arial',
                           size=12,
                           color='black')

                       ),

            yaxis=dict(range=[min(get_sound_level) - 0.1, max(get_sound_level) + 0.1],
                       title='<b>Sonido</b>',
                       color='black',
                       showline=True,
                       showgrid=True,
                       linecolor='black',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Arial',
                           size=12,
                           color='black')

                       ),

            legend={
                'orientation': 'h',
                'bgcolor': '#F2F2F2',
                'x': 0.5,
                'y': 1.25,
                'xanchor': 'center',
                'yanchor': 'top'},
            font=dict(
                family="sans-serif",
                size=12,
                color='black')

        )

    }


@app.callback(Output('text1', 'children'),
              [Input('update_chart', 'n_intervals')])
def update_graph(n_intervals):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_time = df['Time'].tail(1).iloc[0]
    get_light_level = df['Luminosidad'].tail(1).iloc[0].astype(float)
    previous_light_level = df['Luminosidad'].tail(2).iloc[0].astype(float)
    changed_light_level = get_light_level - previous_light_level
    if n_intervals == 0:
        raise PreventUpdate

    color_actual = kpi_color(get_light_level,limite_inferior_luz,limite_superior_luz)
    color_variacion = kpi_color(changed_light_level,0,0)

    # Variación positiva
    if changed_light_level > 0:

        return [
            html.H6('Luminosidad',
                    style={'textAlign': 'left',
                           'lineHeight': '1',
                           'color': '#D35400'}
                    ),
            html.P(get_time,
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 18,
                          'marginTop': '-3px'
                          }
                   ),
            # Nivel Actual
            html.P('{0:,.2f}%'.format(get_light_level),
                   style={'textAlign': 'center',
                          'color': color_actual,
                          'fontSize': 18,
                          'fontWeight': 'bold',
                          'marginTop': '-3px',
                          'lineHeight': '1',
                          }, className='paragraph_value_humi'
                   ),
            html.P('+{0:,.2f}%'.format(changed_light_level) + ' ' + 'vs. medición anterior',
                   style={'textAlign': 'center',
                          'color': color_variacion,
                          'fontSize': 12,
                          'fontWeight': 'bold',
                          'marginTop': '-7px',
                          'lineHeight': '1',
                          }, className='change_paragraph_value_humi'
                   ),
        ]

    elif changed_light_level < 0:

        return [
            html.H6('Luminosidad',
                    style={'textAlign': 'left',
                           'lineHeight': '1',
                           'color': '#D35400'}
                    ),
            html.P(get_time,
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 18,
                          'marginTop': '-3px'
                          }
                   ),
            html.P('{0:,.2f}%'.format(get_light_level),
                   style={'textAlign': 'center',
                          'color': '#dd1e35',
                          'fontSize': 18,
                          'fontWeight': 'bold',
                          'marginTop': '-3px',
                          'lineHeight': '1',
                          }, className='paragraph_value_humi'
                   ),
            html.P('{0:,.2f}%'.format(changed_light_level) + ' ' + 'vs. medición anterior',
                   style={'textAlign': 'center',
                          'color': '#dd1e35',
                          'fontSize': 12,
                          'fontWeight': 'bold',
                          'marginTop': '-7px',
                          'lineHeight': '1',
                          }, className='change_paragraph_value_humi'
                   ),
        ]

    elif changed_light_level == 0:

        return [
            html.H6('Luminosidad',
                    style={'textAlign': 'left',
                           'lineHeight': '1',
                           'color': '#D35400'}
                    ),
            html.P(get_time,
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 18,
                          'marginTop': '-3px'
                          }
                   ),
            html.P('{0:,.2f}%'.format(get_light_level),
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 18,
                          'fontWeight': 'bold',
                          'marginTop': '-3px',
                          'lineHeight': '1',
                          }, className='paragraph_value_humi'
                   ),
            html.P('{0:,.2f}%'.format(changed_light_level) + ' ' + 'vs. medición anterior',
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 12,
                          'fontWeight': 'bold',
                          'marginTop': '-7px',
                          'lineHeight': '1',
                          }, className='change_paragraph_value_humi'
                   ),
        ]


@app.callback(Output('text2', 'children'),
              [Input('update_chart', 'n_intervals')])
def update_graph(n_intervals):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_time = df['Time'].tail(1).iloc[0]
    get_sound_level = df['Sonido'].tail(1).iloc[0].astype(float)
    previous_sound_level = df['Sonido'].tail(2).iloc[0].astype(float)
    changed_sound_level = get_sound_level - previous_sound_level
    if n_intervals == 0:
        raise PreventUpdate

    if changed_sound_level > 0:

        return [
            html.H6('Intensidad de sonido',
                    style={'textAlign': 'left',
                           'lineHeight': '1',
                           'color': '#CA23D5'}
                    ),
            html.P(get_time,
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 18,
                          'marginTop': '-3px'
                          }
                   ),
            html.P('{0:,.2f}°C'.format(get_sound_level),
                   style={'textAlign': 'center',
                          'color': '#008000',
                          'fontSize': 18,
                          'fontWeight': 'bold',
                          'marginTop': '-3px',
                          'lineHeight': '1',
                          }, className='paragraph_value_temp'
                   ),
            html.P('+{0:,.2f}°C'.format(changed_sound_level) + ' ' + 'vs. medición anterior',
                   style={'textAlign': 'center',
                          'color': '#008000',
                          'fontSize': 12,
                          'fontWeight': 'bold',
                          'marginTop': '-7px',
                          'lineHeight': '1',
                          }, className='change_paragraph_value_temp'
                   ),
        ]

    elif changed_sound_level < 0:
        return [
            html.H6('Intensidad de sonido',
                    style={'textAlign': 'left',
                           'lineHeight': '1',
                           'color': '#CA23D5'}
                    ),
            html.P(get_time,
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 18,
                          'marginTop': '-3px'
                          }
                   ),
            html.P('{0:,.2f}°C'.format(get_sound_level),
                   style={'textAlign': 'center',
                          'color': '#dd1e35',
                          'fontSize': 18,
                          'fontWeight': 'bold',
                          'marginTop': '-3px',
                          'lineHeight': '1',
                          }, className='paragraph_value_temp'
                   ),
            html.P('{0:,.2f}°C'.format(changed_sound_level) + ' ' + 'vs. medición anterior',
                   style={'textAlign': 'center',
                          'color': '#dd1e35',
                          'fontSize': 12,
                          'fontWeight': 'bold',
                          'marginTop': '-7px',
                          'lineHeight': '1',
                          }, className='change_paragraph_value_temp'
                   ),
        ]

    elif changed_sound_level == 0:
        return [
            html.H6('Intensidad de sonido',
                    style={'textAlign': 'left',
                           'lineHeight': '1',
                           'color': '#CA23D5'}
                    ),
            html.P(get_time,
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 18,
                          'marginTop': '-3px'
                          }
                   ),
            html.P('{0:,.2f}°C'.format(get_sound_level),
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 18,
                          'fontWeight': 'bold',
                          'marginTop': '-3px',
                          'lineHeight': '1',
                          }, className='paragraph_value_temp'
                   ),
            html.P('{0:,.2f}°C'.format(changed_sound_level) + ' ' + 'vs. medición anterior',
                   style={'textAlign': 'center',
                          'color': 'black',
                          'fontSize': 12,
                          'fontWeight': 'bold',
                          'marginTop': '-7px',
                          'lineHeight': '1',
                          }, className='change_paragraph_value_temp'
                   ),
        ]


# Si es ruidoso o no
@app.callback(Output('update', 'children'),
              [Input('update_chart', 'n_intervals')])
def update_graph(n_intervals):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_sound_level = df['Sonido'].tail(1).iloc[0].astype(float)
    if n_intervals == 0:
        raise PreventUpdate

    # Imagen ruidosa
    if get_sound_level >= 21:
        return [
            html.Div([
                html.H6('Muy ruidoso',
                        style={'lineHeight': '1',
                               'color': '#FFFFFF'}
                        ),
                html.Img(src=app.get_asset_url('sun.png'),
                         style={'height': '35px'}),
            ], className='temp_card2')
        ]

    # Ambiente tranquilo
    elif get_sound_level < 21:
        return [
            html.Div([
                html.H6('Ruido aceptable',
                        style={'lineHeight': '1',
                               'color': '#00FF00'}
                        ),
                html.Img(src=app.get_asset_url('cloudy-day.png'),
                         style={'height': '35px'}),
            ], className='temp_card2')
        ]


if __name__ == "__main__":
    app.run_server(debug=True)
