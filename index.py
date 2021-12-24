import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app._favicon = "/assets/favicon.ico"
app.title = "E12 - Sensores"

# Data - CSV
csv = 'light_sound.csv'
header_list = ['Time', 'Luminosidad', 'Sonido', 'Temperatura']

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

chart_humidity = dcc.Graph(id='luminosity-chart',
                           animate=True,
                           config={'displayModeBar': 'hover'},
                           className='chart_width'),

chart_temperature = dcc.Graph(id='sound-chart',
                              animate=True,
                              config={'displayModeBar': 'hover'},
                              className='chart_width')

# Umbrales de tolerancia, y razonables
limite_inferior_luz = 65
limite_superior_luz = 75

limite_inferior_sonido = 30
limite_superior_sonido = 60

limite_inferior_temperatura = 20
limite_superior_temperatura = 32


def semaforo_factory(limite_inferior, limite_superior,
                     titulo_izquierdo="Peligro", titulo_central="Alerta", titulo_derecho="Correcto",
                     color_izquierdo="red", color_central="#FCDE22", color_derecho="#109D55"
                     ):
    semaforo = html.Div([
        html.Div([
            html.Div([html.H5(titulo_izquierdo, style={"marginBottom": '0px', 'color': 'black'})],
                     className="cell cell-header cell-header-red  card_container four columns",
                     style={"backgroundColor": color_izquierdo}),
            html.Div([html.H5(titulo_central, style={"marginBottom": '0px', 'color': 'black'})],
                     className="cell cell-header cell-header-green  card_container four "
                               "columns", style={"backgroundColor": color_central}),
            html.Div([html.H5(titulo_derecho, style={"marginBottom": '0px', 'color': 'black'})],
                     className="cell cell-header cell-header-red card_container four columns",
                     style={"backgroundColor": color_derecho}
                     )
        ], className="row flex display"
        ),
        html.Div([
            html.Div([html.H5(f"< {limite_inferior}", style={"marginBottom": '0px', 'color': color_izquierdo})],
                     className="cell cell-body cell-body-red danger card_container four columns"),
            html.Div(
                [html.H5(f"{limite_inferior} - {limite_superior}",
                         style={"marginBottom": '0px', 'color': color_central})],
                className="cell cell-body cell-body-yellow warning card_container four "
                          "columns"),
            html.Div([html.H5(f"{limite_superior} <", style={"marginBottom": '0px', 'color': color_derecho})],
                     className="cell cell-body cell-body-green success card_container four columns")
        ], className="row flex display"
        )
    ], className="table row flex display")
    return semaforo


def background_factory(value, limite_inferior, limite_superior, fondo_izquierdo, fondo_central, fondo_derecho):
    if value > limite_superior:
        # Cambiarlo por lugar con mucha luz
        return [
            html.Div(style={'backgroundImage': f'url("/assets/{fondo_derecho}")',
                            'height': '100vh',
                            'backgroundRepeat': 'no-repeat',
                            'backgroundSize': 'cover'
                            }),
        ]

    elif value < limite_inferior:
        # Cambiarlo por lugar oscuro / semáforo
        return [
            html.Div(style={'backgroundImage': f'url("/assets/{fondo_izquierdo}")',
                            'height': '100vh',
                            'backgroundRepeat': 'no-repeat',
                            'backgroundSize': 'cover'
                            },
                     ),

        ]
    else:
        return [
            html.Div(style={'backgroundImage': f'url("/assets/{fondo_central}")',
                            'height': '100vh',
                            'backgroundRepeat': 'no-repeat',
                            'backgroundSize': 'cover'
                            },
                     ), ]


def kpi_color(valor, umbral_minimo, umbral_maximo, color_izquierdo="red", color_central="#FCDE22",
              color_derecho="#109D55"):
    if valor < umbral_minimo:
        color = color_izquierdo
    elif valor > umbral_maximo:
        color = color_derecho
    else:
        color = color_central
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
                html.Div([
                    html.Img(src="/assets/autism_logo.png",
                             title="Logo de los autistas",
                             style={
                                 "height": "100px",
                                 "width": "auto",
                                 'marginBottom': "25px"
                             }, id="logo_ocad", className="six columns"),
                    html.H6('E12 - Sensores',
                            style={
                                'lineHeight': '1',
                                'color': 'white',
                                'marginLeft': '20px','fontSize':'50px','paddingTop': '20px'},
                            className='adjust_title six columns'
                            ),
                ], className="six columns row flex display"),

                html.Div([
                    html.Div(id='update',
                             className='image_grid six columns'),
                    html.H6(id='get_date_time',
                            style={
                                'lineHeight': '1',
                                'color': 'white', 'paddingTop': '7%', 'marginRight': '30px'},
                            className='adjust_date_time'
                            )
                ], className='temp_card1', style={'textAlign':'right'}),
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
                # html.Div(id='text1', className='grid_height'),
                # html.Div(id='text2', className='grid_height'),
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
                                             dcc.Graph(id='luminosity-chart',
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
                                                         semaforo_factory(f"{limite_inferior_luz} LUX",
                                                                          f"{limite_superior_luz} LUX", "Correcto",
                                                                          "Alerta",
                                                                          "Peligro", color_izquierdo="#109D55",
                                                                          color_central="#FCDE22", color_derecho="red")
                                                     ], className="twelve columns"),
                                                 ], className="row flex display"),
                                                 # Imagen
                                                 html.Div([
                                                     html.Div(id='update_imagen_luz',
                                                              className='image_grid twelve columns'),
                                                 ], className="row flex display"),
                                             ], className="row flex display"),
                                         ], className="five columns"),
                                     ], className="row flex display"),
                                 ],
                                 label='Intensidad de la luz',
                                 # value='chart_humidity',
                                 style=tab_style,
                                 selected_style=tab_selected_style,
                                 className='font_size'),
                             dcc.Tab(
                                 children=[
                                     # Gráfico de lineas + KPI + Semáforo + Imagen
                                     html.Div([
                                         # 8 columnas
                                         html.Div([
                                             # Gráfico de lineas
                                             dcc.Graph(id='sound-chart',
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
                                                         html.Div(id='text2', className='grid_height'),
                                                     ], className="twelve columns"),
                                                 ], className="row flex display"),
                                                 # Semáforo
                                                 html.Div([
                                                     html.Div([
                                                         semaforo_factory(f"{limite_inferior_sonido} dB",
                                                                          f"{limite_superior_sonido} dB", "Correcto",
                                                                          "Alerta",
                                                                          "Peligro", color_izquierdo="#109D55",
                                                                          color_central="#FCDE22", color_derecho="red")
                                                     ], className="twelve columns"),
                                                 ], className="row flex display"),
                                                 # Imagen
                                                 html.Div([
                                                     html.Div(id='update_imagen_sonido',
                                                              className='image_grid twelve columns'),
                                                 ], className="row flex display"),
                                             ], className="row flex display"),
                                         ], className="five columns"),
                                     ], className="row flex display"),
                                 ],
                                 label='Intensidad del sonido',
                                 style=tab_style,
                                 selected_style=tab_selected_style,
                                 className='font_size'),
                             dcc.Tab(
                                 children=[
                                     # Gráfico de lineas + KPI + Semáforo + Imagen
                                     html.Div([
                                         # 8 columnas
                                         html.Div([
                                             # Gráfico de lineas
                                             dcc.Graph(id='temperature-chart',
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
                                                         html.Div(id='text3', className='grid_height'),
                                                     ], className="twelve columns"),
                                                 ], className="row flex display"),
                                                 # Semáforo
                                                 html.Div([
                                                     html.Div([
                                                         semaforo_factory(f"{limite_inferior_temperatura}°C",
                                                                          f"{limite_superior_temperatura}°C",
                                                                          "Muy frío", "Correcto",
                                                                          "Muy caluroso", color_izquierdo="red",
                                                                          color_central="#109D55", color_derecho="red")
                                                     ], className="twelve columns"),
                                                 ], className="row flex display"),
                                                 # Imagen
                                                 html.Div([
                                                     html.Div(id='update_imagen_temperatura',
                                                              className='image_grid twelve columns'),
                                                     html.P(id="example")
                                                 ], className="row flex display"),
                                             ], className="row flex display"),
                                         ], className="five columns"),
                                     ], className="row flex display"),
                                 ],
                                 label='Temperatura',
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


@app.callback(Output('get_date_time', 'children'),
              [Input('update_date_time', 'n_intervals')])
def update_graph(n_intervals):
    now = datetime.now()
    dt_string = now.strftime("Fecha: %d/%m/%Y, Hora: %H:%M:%S %p")
    if n_intervals == 0:
        raise PreventUpdate

    return [
        html.Div(dt_string),
    ]


@app.callback(Output('luminosity-chart', 'figure'),
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
            '<b>Luminiscencia</b>: ' + [f'{x:,.2f} LUX' for x in get_light_level] + '<br>'

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


@app.callback(Output('sound-chart', 'figure'),
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
            '<b>Intensidad de sonido</b>: ' + [f'{x:,.2f} dB' for x in get_sound_level] + '<br>'

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


@app.callback(Output('temperature-chart', 'figure'),
              [Input('update_chart', 'n_intervals')])
def update_graph(n_intervals):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_time = df['Time'].tail(20)
    get_sound_level = df['Temperatura'].tail(20)
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
            '<b>Temperatura</b>: ' + [f'{x:,.2f} °C' for x in get_sound_level] + '<br>'

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
                       title='<b>Temperatura</b>',
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

    color_actual = kpi_color(get_light_level, limite_inferior_luz, limite_superior_luz, color_izquierdo="#109D55",
                             color_central="#FCDE22", color_derecho="red")
    color_variacion = kpi_color(changed_light_level, 0, 0, color_central="black")

    return [
        html.H6('Luminosidad',
                style={'textAlign': 'center',
                       'lineHeight': '1',
                       'color': 'black',
                       'fontSize': 30,
                       }
                ),
        # Nivel Actual
        html.P('{0:,.2f} LUX'.format(get_light_level),
               style={'textAlign': 'center',
                      'color': color_actual,
                      'fontSize': 30,
                      'fontWeight': 'bold',
                      'marginTop': '5px',
                      'lineHeight': '1',
                      }, className='paragraph_value_humi'
               ),
        html.P('{0:,.2f} LUX'.format(changed_light_level) + ' ' + 'vs. medición anterior',
               style={'textAlign': 'center',
                      'color': color_variacion,
                      'fontSize': 15,
                      'fontWeight': 'bold',
                      'marginTop': '0px',
                      'marginLeft': '0px',
                      'lineHeight': '1',
                      }, className='change_paragraph_value_humi'
               ),
        html.P(get_time,
               style={'textAlign': 'center',
                      'color': 'black',
                      'fontSize': 14,
                      'marginTop': '0px'
                      }
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

    color_actual = kpi_color(get_sound_level, limite_inferior_sonido, limite_superior_sonido, color_izquierdo="#109D55",
                             color_central="#FCDE22", color_derecho="red")
    color_variacion = kpi_color(changed_sound_level, 0, 0, color_central="black")

    return [
        html.H6('Nivel sonoro',
                style={'textAlign': 'center',
                       'lineHeight': '1',
                       'color': 'black',
                       'fontSize': 30,
                       }
                ),
        # Nivel Actual
        html.P('{0:,.2f} dB'.format(get_sound_level),
               style={'textAlign': 'center',
                      'color': color_actual,
                      'fontSize': 30,
                      'fontWeight': 'bold',
                      'marginTop': '5px',
                      'lineHeight': '1',
                      }, className='paragraph_value_humi'
               ),
        html.P('{0:,.2f} dB'.format(changed_sound_level) + ' ' + 'vs. medición anterior',
               style={'textAlign': 'center',
                      'color': color_variacion,
                      'fontSize': 15,
                      'fontWeight': 'bold',
                      'marginTop': '0px',
                      'marginLeft': '0px',
                      'lineHeight': '1',
                      }, className='change_paragraph_value_humi'
               ),
        html.P(get_time,
               style={'textAlign': 'center',
                      'color': 'black',
                      'fontSize': 14,
                      'marginTop': '0px'
                      }
               ),
    ]


@app.callback(Output('text3', 'children'),
              [Input('update_chart', 'n_intervals')])
def update_graph(n_intervals):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_time = df['Time'].tail(1).iloc[0]
    get_temperature_level = df['Temperatura'].tail(1).iloc[0].astype(float)
    previous_temperature_level = df['Temperatura'].tail(2).iloc[0].astype(float)
    changed_temperature_level = get_temperature_level - previous_temperature_level
    if n_intervals == 0:
        raise PreventUpdate

    color_actual = kpi_color(get_temperature_level, limite_inferior_temperatura, limite_superior_temperatura,
                             color_izquierdo="red", color_central="#109D55", color_derecho="red")
    color_variacion = kpi_color(changed_temperature_level, 0, 0, color_central="black")

    return [
        html.H6('Temperatura',
                style={'textAlign': 'center',
                       'lineHeight': '1',
                       'color': 'black',
                       'fontSize': 30,
                       }
                ),
        # Nivel Actual
        html.P('{0:,.2f} °C'.format(get_temperature_level),
               style={'textAlign': 'center',
                      'color': color_actual,
                      'fontSize': 30,
                      'fontWeight': 'bold',
                      'marginTop': '5px',
                      'lineHeight': '1',
                      }, className='paragraph_value_humi'
               ),
        html.P('{0:,.2f} °C'.format(changed_temperature_level) + ' ' + 'vs. medición anterior',
               style={'textAlign': 'center',
                      'color': color_variacion,
                      'fontSize': 15,
                      'fontWeight': 'bold',
                      'marginTop': '0px',
                      'marginLeft': '0px',
                      'lineHeight': '1',
                      }, className='change_paragraph_value_humi'
               ),
        html.P(get_time,
               style={'textAlign': 'center',
                      'color': 'black',
                      'fontSize': 14,
                      'marginTop': '0px'
                      }
               ),
    ]


# Si es ruidoso o no
@app.callback(Output('update_imagen_luz', 'children'), Output('update_imagen_sonido', 'children'),
              Output('update_imagen_temperatura', 'children'),
              [Input('update_chart', 'n_intervals')])
def update_graph(n_intervals):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_light_level = df['Luminosidad'].tail(1).iloc[0].astype(float)
    get_sound_level = df['Sonido'].tail(1).iloc[0].astype(float)
    get_temperature_level = df['Temperatura'].tail(1).iloc[0].astype(float)
    if n_intervals == 0:
        raise PreventUpdate

    children_light = None
    children_sound = None

    # Imagen con mucha luz
    if get_light_level > limite_superior_luz:
        children_light = [
            html.Div([
                html.Img(src=app.get_asset_url('too_shiny.png'),
                         # style={'height': '35px'}
                         ),
            ], className='temp_card2')
        ]

    # Ambiente tranquilo
    elif get_light_level < limite_inferior_luz:
        children_light = [
            html.Div([
                html.Img(src=app.get_asset_url('ok.png'),
                         # style={'height': '35px'}
                         ),
            ], className='temp_card2')
        ]

    else:
        children_light = [
            html.Div([
                html.Img(src=app.get_asset_url('warning.png'),
                         # style={'height': '35px'}
                         ),
            ], className='temp_card2')
        ]

    # Imagen con mucha luz
    if get_sound_level > limite_superior_sonido:
        children_sound = [
            html.Div([
                html.Img(src=app.get_asset_url('too_noisy.png'),
                         # style={'height': '35px'}
                         ),
            ], className='temp_card2')
        ]

    # Ambiente tranquilo
    elif get_sound_level < limite_inferior_sonido:
        children_sound = [
            html.Div([
                html.Img(src=app.get_asset_url('ok.png'),
                         # style={'height': '35px'}
                         ),
            ], className='temp_card2')
        ]

    else:
        children_sound = [
            html.Div([
                html.Img(src=app.get_asset_url('warning.png'),
                         # style={'height': '35px'}
                         ),
            ], className='temp_card2')
        ]

    # Imagen con mucha luz
    if get_temperature_level > limite_superior_temperatura:
        children_temperature = [
            html.Div([
                html.Img(src=app.get_asset_url('too_hot.png'),
                         # style={'height': '35px'}
                         ),
            ], className='temp_card2')
        ]

        # Ambiente tranquilo
    elif get_temperature_level < limite_inferior_temperatura:
        children_temperature = [
            html.Div([
                html.Img(src=app.get_asset_url('too_cold.png'),
                         # style={'height': '35px'}
                         ),
            ], className='temp_card2')
        ]

    else:
        children_temperature = [
            html.Div([
                html.Img(src=app.get_asset_url('ok.png'),
                         # style={'height': '35px'}
                         ),
            ], className='temp_card2')
        ]

    return children_light, children_sound, children_temperature


# Usado para cambiar la imagen de fondo
@app.callback(Output('background_image', 'children'),
              [Input('update_chart', 'n_intervals'), Input("tabs-styled-with-inline", "value")])
def update_graph(n_intervals, n_tab):
    df = pd.read_csv('%s' % csv, names=header_list)
    get_time = df['Time'].tail(1).iloc[0]
    get_luminosity = df['Luminosidad'].tail(1).iloc[0].astype(float)
    get_sound_level = df['Sonido'].tail(1).iloc[0].astype(float)
    get_temperature_level = df['Temperatura'].tail(1).iloc[0].astype(float)
    if n_intervals == 0:
        raise PreventUpdate

    if n_tab == "tab-1":
        background_children = background_factory(get_luminosity, limite_inferior_luz, limite_superior_luz,
                                                 "white_bg.png", "white_bg.png", "too_shiny_bg.png")
    elif n_tab == "tab-2":
        background_children = background_factory(get_sound_level, limite_inferior_sonido, limite_superior_sonido,
                                                 "white_bg.png", "white_bg.png",
                                                 "too_noisy_bg.png")
    else:
        background_children = background_factory(get_temperature_level, limite_inferior_temperatura,
                                                 limite_superior_temperatura,
                                                 "too_cold_bg.png",
                                                 "normal_temperature_bg.png",
                                                 "too_hot_bg.png")

    return background_children


if __name__ == "__main__":
    app.run_server(debug=True)
