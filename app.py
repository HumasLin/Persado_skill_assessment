import os
import sys
import dash
import nltk
import time
import flask
import base64
import dash_table
import webbrowser
import numpy as pd
import pandas as pd
import dash.dependencies as dd
import matplotlib.pyplot as plt
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from io import BytesIO
from threading import Timer
from datetime import datetime
from wordcloud import WordCloud
from dash.dependencies import Input, Output
from nltk.corpus import stopwords
nltk.download('stopwords')

from lib.data import *
from lib.utils import *
from lib.scraper import *
from lib.analysis import *

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash('app', server=server)

df_post_1 = pd.read_csv('data/SKECHERS_posts.csv',index_col=0)
df_post_2 = pd.read_csv('data/ASICSamerica_posts.csv',index_col=0)

cols = [{"name": i, "id": i, "deletable": False, "selectable": False} 
            for i in ['time','text','image_flag','video_flag','product_flag']]
cols[0]["name"] = "Post Time"
cols[1]["name"] = "Post Content"
cols[2]["name"] = "Image"
cols[3]["name"] = "Video"
cols[4]["name"] = "Product"

dataframes={'SKECHERS':df_post_1,
            'ASICSamerica':df_post_2}

df_product_1 = pd.read_csv('data/SKECHERS_products.csv',index_col=0)
df_product_2 = pd.read_csv('data/ASICSamerica_products.csv',index_col=0)

cols_product = [{"name": i, "id": i, "deletable": False, "selectable": False} 
            for i in ['product_name','price','details']]
cols_product[0]["name"] = "Product Name"
cols_product[1]["name"] = "Price"
cols_product[2]["name"] = "Details"

dataframes_product={'SKECHERS':df_product_1,
                    'ASICSamerica':df_product_2}

doc1 = [clean(str(text)) for text in list(df_post_1['text']) if clean(str(text))!='nan']
doc2 = [clean(str(text)) for text in list(df_post_2['text']) if clean(str(text))!='nan']

@app.callback(dd.Output('image_wc_1', 'src'), [dd.Input('image_wc_1', 'id')])
def make_image(b):
    img = BytesIO()
    plot_wordcloud(data=doc1).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

@app.callback(dd.Output('image_wc_2', 'src'), [dd.Input('image_wc_2', 'id')])
def make_image(b):
    img = BytesIO()
    plot_wordcloud(data=doc2).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

@app.callback(Output('data_table', 'data'),[Input('brand_dropdown', 'value')])
def table_brand(selected_dropdown_value):
    display_df = dataframes[selected_dropdown_value]
    return display_df.to_dict('rows')

@app.callback(
    Output('selected_data', "data"),
    Input('brand_dropdown', 'value'),
    Input('data_table', "data"),
    Input('data_table', "derived_virtual_data"),
    Input('data_table', "derived_virtual_selected_rows"))
def table_product(selected_dropdown_value, rows, data, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        assemble = pd.DataFrame()
    else:
        dataframes_list=[]
        products = dataframes_product[selected_dropdown_value]
        for row in derived_virtual_selected_rows:
            post_id = data[row]['id']
            target = products[products['post_id']==post_id]
            dataframes_list.append(target)
        assemble = pd.concat(dataframes_list) if len(dataframes_list)>0 else pd.DataFrame()
    return assemble.to_dict('rows')

@app.callback(
    Output('product_summarization', "children"),
    Input('selected_data', "data"),
    Input('selected_data', "derived_virtual_data"),
    Input('selected_data', "derived_virtual_selected_rows"))
def get_text_summary(rows, data, derived_virtual_selected_rows):
    text = ""
    if derived_virtual_selected_rows is not None and len(derived_virtual_selected_rows):
        text = data[sorted(derived_virtual_selected_rows)[0]]['details']
        text = query(text)[0]['summary_text']
    return '{}'.format(text)

app.layout = dbc.Row(
                [dbc.Col(md=7,children=[
                    dbc.Row([
                        html.H1(children='Persado Skill Assessment'),
                        html.Div(children='Choose brand', style={
                            'font-style': 'italic',
                            'font-weight': 'bold'
                        }),
                        dcc.Dropdown(
                        id='brand_dropdown',
                        options=[{'label': 'SKECHERS', 'value': 'SKECHERS'},
                                {'label': 'ASICS', 'value': 'ASICSamerica'},],
                        value='SKECHERS',
                        )],style={"width": "45%", "margin-left": "25px"}),
                    dbc.Row([
                    dbc.Row([
                    dash_table.DataTable(
                        id='data_table',
                        columns= cols,
                        editable=True,
                        sort_action="native",
                        sort_mode='multi',
                        row_selectable='multi',
                        selected_rows=[],
                        tooltip_delay=0,
                        tooltip_duration=None,
                        virtualization=True,
                        fixed_rows={'headers': True},
                        style_cell_conditional=[
                        {'if': {'column_id':'time'},'width':'2px'},
                        {'if': {'column_id':'image_flag'},'width':'2px'},
                        {'if': {'column_id':'video_flag'},'width':'2px'},
                        {'if': {'column_id':'product_flag'},'width':'2px'}
                        ],
                        style_cell={'minWidth': '5px', 'width': 75, 'maxWidth': 75, 
                                    'Height':10, 'padding': '15px', 'textAlign': 'center'},
                        style_table={'height': 1000, 'overflowY': 'auto', 'overflowX': 'auto'}),
                    ], style={"width": "45%", "margin-left": "25px","margin-top": "5px",'display':'inline-block'},className='divBorder'),
                    
                    dbc.Row([
                    dash_table.DataTable(
                        id='selected_data',
                        columns=cols_product,
                        editable=True,
                        sort_action="native",
                        sort_mode='multi',
                        row_selectable='multi',
                        selected_rows=[],
                        page_action="native",
                        page_current= 0,
                        page_size= 4,
                        style_as_list_view=True,

                        fixed_rows={'headers': True},
                        style_cell_conditional=[
                        {'if': {'column_id':'product_name'},'width':'20px'},
                        {'if': {'column_id':'image_flag'},'width':'10px'},
                        {'if': {'column_id':'video_flag'},'width':'10px'},
                        {'if': {'column_id':'product_flag'},'width':'10px'}
                        ],
                        style_cell={'minWidth': '3px', 'width': '5px', 'maxWidth': '10px', 'border':'1px solid black',
                                    'Height':10, 'padding': '15px', 'textAlign': 'center'},
                        style_header={'border':'1px solid black'},
                    ),
                    dbc.Row([html.H3(["By checking the item associated with product links in the left table and then \
                                      selecting a product in the above table, you can inspect the summarization of \
                                       the product details through the selected NLP model from Huggingface:"],
                                       style={'width':'90%'})],style={'position':'absolute',
                                                                      'margin-left':'5px','margin-top':'20px'}),
                    html.Div([
                        dbc.Row([html.Div(children='*Note that when selecting multiple rows, only details in the row with\
                                                smallest index will be summarized', style={
                                                                  'width':'90%','font-style': 'italic','font-weight': 'bold'})
                                                                    ],style={'position':'absolute',
                                                                  'margin-left':'5px','margin-top':'110px'}),
                        dbc.Row([html.H4(["Product Detail Summarization:"],style={'width':'90%'})],style={'position':'absolute',
                                                                      'margin-left':'5px','margin-top':'130px'}),
                        dbc.Row([html.Div(id="product_summarization",style={'width':'90%'})],style={'position':'absolute',
                                                                  'margin-left':'5px','margin-top':'190px'}),],
                        className='divBorder')
                    ],style={"width": "45%", "margin-left": "75px","margin-top": "5px",'display':'inline-block'}),
                ],no_gutters=True)
                ],style={'width':'100%'}),
                
                dbc.Col(md=5,children=[
                    dbc.Row([
                        html.H2("Comparison",style={'height': '100%','width': '100%',
                                                             'margin-left':'25px',
                                                             'margin-top':'25px',
                                                             'textAlign':'center'}),
                        html.H3("WordCloud",style={'height': '100%','width': '100%',
                                                             'margin-left':'25px',
                                                             'margin-top':'25px',
                                                             'textAlign':'center'},className='divBorder'),])]),

                dbc.Col(md=5,children=[
                    dbc.Row([
                        html.H4("SKECHERS WordCloud",style={'height': '100%','width': '100%',
                                                             'padding':'25px','textAlign':'center'}),
                        html.Img(id="image_wc_1",style={'height': '100%','width': '100%',
                                                      'margin-left':'25px','margin-right':'25px'})],
                        style={'width':'45%','display': 'inline-block'}),
                    dbc.Row([
                        html.H4("ASICS WordCloud",style={'height': '100%','width': '100%','margin-left':'75px',
                                                          'padding':'25px','textAlign':'center'}),
                        html.Img(id="image_wc_2",style={'height': '100%','width': '100%',
                                                       'margin-left':'100px','margin-right':'25px'})],
                        style={'width':'45%','display': 'inline-block'})   
                ]),
                html.H3("Word Usage",style={'height': '100%','width': '100%',
                                             'margin-top':'25px',
                                             'margin-bottom':'25px',
                                             'textAlign':'center'},className='divBorder'),
                dbc.Col(md=5,children=[
                    html.H4("According to results from TfidfVectorizer, the 10 words SKECHERS uses most frequently\
                        in their posts are:",style={'padding':'5px'}),
                    html.H4("['skechers', 'skechersstyle', 'style', 'comfort', 'fashion',\
                        'streetstyle', 'mens', 'shoes', 'sneakers', 'love']",style={'padding':'5px'}),
                    html.H4("But for ASICS, the 10 words they use most frequently\
                        in their posts are:",style={'padding':'5px'}),
                    html.H4("['run', 'long', 'win', 'new', 'shop', 'running', 'shoe',\
                       'collection', 'asics', 'gel']",style={'padding':'5px'}),
                    html.H4("Combined with the WordCloud, based on the word usage, the difference between how\
                        these two companies promote their products are easy to tell.",style={'padding':'5px'}),
                ],style={'width':'100%','textAlign':'center'})
                ],no_gutters=True)

def open_browser():
    webbrowser.open_new("http://localhost:{}".format(8050))

if __name__ == '__main__':

    Timer(1, open_browser).start();
    app.run_server(debug=True)
