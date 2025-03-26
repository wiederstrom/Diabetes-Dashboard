import dash
import os
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px


df = pd.read_csv('diabetes_012_health_indicators_BRFSS2015.csv')

diabetes_map = {
    0: 'No Diabetes',
    1: 'Pre-Diabetes',
    2: 'Diabetes'
}

general_health_map = {
    1: 'Excellent',
    2: 'Very Good',
    3: 'Good',
    4: 'Fair',
    5: 'Poor'
}

sex_map = {
    0: 'Female',
    1: 'Male'
}

age_map = {
    1: '18-24',
    2: '25-29',
    3: '30-34',
    4: '35-39',
    5: '40-44',
    6: '45-49',
    7: '50-54',
    8: '55-59',
    9: '60-64',
    10: '65-69',
    11: '70-74',
    12: '75-79',
    13: '80+'
}

eduacation_map = {
    1: 'No Schooling',
    2: 'Elementary School',
    3: 'Middle School',
    4: 'High School',
    5: 'Some College',
    6: 'College Graduate'
}

income_map = {
    1: 'Less than $10,000',
    2: '$10,000 to $15,000',
    3: '$15,000 to $20,000',
    4: '$20,000 to $25,000',
    5: '$25,000 to $35,000',
    6: '$35,000 to $50,000',
    7: '$50,000 to $75,000',
    8: '$75,000 or more'
}

df['Diabetes Status'] = df['Diabetes_012'].map(diabetes_map)
df['General Health'] = df['GenHlth'].map(general_health_map)
df['Sex Label'] = df['Sex'].map(sex_map)
df['Age Group'] = df['Age'].map(age_map)
df['Education Level'] = df['Education'].map(eduacation_map)
df['Income Level'] = df['Income'].map(income_map)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = dbc.Container([
    dbc.Navbar(
        dbc.Container([
            html.Div([
                html.H3("U.S. Diabetes Insights (BRFSS 2015)", className="mb-0 text-white"),
                html.P("Explore diabetes prevalence by age, income, gender, and education using BRFSS 2015 data.",
                       className="mb-0 text-white-50", style={"fontSize": "0.9rem"})
            ])
        ]),
        color="primary",
        dark=True,
        className="mb-4"
    ),

    dbc.Row([
        dbc.Col([
            html.H5("Filters", className="mb-2"),

            dbc.Label("Gender"),
            dcc.Dropdown(
                options=[{"label": sex, "value": sex} for sex in sorted(df['Sex Label'].unique())],
                id='sex-filter', multi=True
            ),

            dbc.Label("Age Group", className="mt-3"),
            dcc.Dropdown(
                options=[{"label": age_map[k], "value": age_map[k]} for k in sorted(age_map)],
                id='age-filter', multi=True
            ),

            dbc.Label("Education Level", className="mt-3"),
            dcc.Dropdown(
                options=[{"label": eduacation_map[k], "value": eduacation_map[k]} for k in sorted(eduacation_map)],
                id='education-filter', multi=True
            ),

            dbc.Label("Income Level", className="mt-3"),
            dcc.Dropdown(
                options=[{"label": income_map[k], "value": income_map[k]} for k in sorted(income_map)],
                id='income-filter', multi=True
            )
        ], width=3),

        dbc.Col([
            dcc.Loading(
                type="circle",
                children=[
                    dbc.Row([
                        dbc.Col(dbc.Card([
                            dbc.CardHeader("Diabetes Status Distribution"),
                            dbc.CardBody(dcc.Graph(id='diabetes-pie'))
                        ]), width=12)
                    ], className="mb-4"),

                    dbc.Row([
                        dbc.Col(dbc.Card([
                            dbc.CardHeader("Diabetes by Gender"),
                            dbc.CardBody(dcc.Graph(id='diabetes-bar'))
                        ]), width=12)
                    ], className="mb-4"),

                    dbc.Row([
                        dbc.Col(dbc.Card([
                            dbc.CardHeader("Average BMI by Diabetes Status"),
                            dbc.CardBody(dcc.Graph(id='bmi-violin'))
                        ]), width=12)
                    ], className="mb-4"),

                    dbc.Row([
                        dbc.Col(dbc.Card([
                            dbc.CardHeader(id="record-count"),
                            dbc.CardBody(dash_table.DataTable(
                                id='filtered-table',
                                page_size=10,
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'left'}
                            ))
                        ]), width=12)
                    ])
                ]
            )
        ], width=9)
    ]),

    dbc.Row([
        dbc.Col(
            html.Footer("Data Source: Behavioral Risk Factor Surveillance System (BRFSS) for 2015"),
            width=12,
            className="text-center text-muted my-4"
        )
    ])
], fluid=True)


@app.callback(
    [Output('diabetes-pie', 'figure'),
     Output('diabetes-bar', 'figure'),
     Output('bmi-violin', 'figure'),
     Output('filtered-table', 'data'),
     Output('filtered-table', 'columns'),
     Output('record-count', 'children')],
    [Input('sex-filter', 'value'),
     Input('age-filter', 'value'),
     Input('education-filter', 'value'),
     Input('income-filter', 'value')]
)
def update_graphs(sex, age, edu, income):
    dff = df.copy()
    if sex:
        dff = dff[dff['Sex Label'].isin(sex)]
    if age:
        dff = dff[dff['Age Group'].isin(age)]
    if edu:
        dff = dff[dff['Education Level'].isin(edu)]
    if income:
        dff = dff[dff['Income Level'].isin(income)]

    pie_fig = px.pie(dff, names='Diabetes Status', template='plotly_white', hover_data=None)
    pie_fig.update_traces(textinfo='label+percent', hovertemplate='%{label}<extra></extra>')
    pie_fig.update_layout(title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    bar_df = dff['Diabetes Status'].value_counts().reset_index()
    bar_df.columns = ['Diabetes Status', 'Count']

    bar_fig = px.bar(
        bar_df,
        x='Diabetes Status',
        y='Count',
        text='Count',
        template='plotly_white',
        color='Diabetes Status',
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    bar_fig.update_traces(textposition='outside')
    bar_fig.update_layout(
        title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    violin_fig = px.violin(dff, x='Diabetes Status', y='BMI', box=True, points=False,
                           template='plotly_white')
    violin_fig.update_layout(title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    preview = dff[['Diabetes Status', 'Sex Label', 'Age Group', 'Education Level', 'Income Level', 'BMI', 'General Health']]
    table_data = preview.to_dict('records')
    table_columns = [{"name": col.replace('_', ' '), "id": col} for col in preview.columns]

    record_info = f"Filtered Data Preview ({len(preview)} records)"

    return pie_fig, bar_fig, violin_fig, table_data, table_columns, record_info


port = int(os.environ.get("PORT", 8050))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)


