import dash_core_components as dcc
import dash_html_components as html
from dash_extensions import Download
from dash_extensions.snippets import send_file


#initialize variables so dun throw error 
files = []
image = None
fig = {"data":[{"x":[0],"y":[0]}]}
fig2 = {"data":[{"x":[0],"y":[0]}]}
fig4 = {"data":[{"x":[0],"y":[0]}]}
fig5 = {"data":[{"x":[0],"y":[0]}]}

page_1_layout = html.Div([
    dcc.Location(id='url', refresh=False),

    html.H1("Auto XSEM Measurer",className = 'navbar text-primary'),
    
    html.Div('Welcome to AXM ! Please begin by uploading the images you want to measure below:'),

    html.Div([

    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),

    html.Button("Ready?",id="ready", n_clicks=0)

]),
  

])



#layout for the second page 
page_2_layout = html.Div(
    
    
    [ dcc.Location(id='url', refresh=False),html.Br(),
       html.P("Original Image",style={'text-align':'center'}),
html.Div(dcc.Graph(id="graph-picture", figure=fig),style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),

html.P("Canny Image",style={'text-align':'center'}),

html.Div(dcc.Graph(id="graph-picture2", figure=fig2),style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),

html.P("Noise Filter Slidebar",style={'text-align':'center'}),
dcc.Slider(
id='my-slider',
min=1,
max=21,
step=2,
value=1,
),

html.Div(id='slider-output-container'),

html.P("Indicate Points to measure here",style={'text-align':'center'}),

html.Div(dcc.Graph(id="graph-picture4", figure=fig4),style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
html.Div([
html.Button('Scale Bar', id ='Scale Bar', n_clicks=0, style = {'width': '220px'} ),
html.Button('X Dir', id = 'X Dir', n_clicks= 0, style = {'width': '220px'}),
html.Button('Y Dir' ,id ='Y Dir', n_clicks=0, style = {'width': '220px'}),
],style={'text-align':'center'}),
html.Div('Selected Coordinates', id = 'coordinates',style={'text-align':'center'}),
html.Br(),
html.Div([dcc.Input(id='input',type='text',placeholder ="Input your scalebar value", value= None),html.Button('Submit',id = 'submit', n_clicks = 0)],style={'text-align':'center'}),
html.Br(),
html.Div(id='click-data'),

html.Div(dcc.Graph(id="graph-picture5",figure = fig5),style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),

#add refersh button so start from the top
html.A(html.Button('Next Image' ,id ='AO', n_clicks=0, style = {'width': '220px'}),href="/start"),

html.Div([html.Button("Click to Download PPT", id="btn_image"),Download(id="download-image")]),

html.Div([dcc.ConfirmDialog(id='reminder for PPT',message='Pls be reminded to download your PPT :)')])


    ])
