import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

from app import app
from layouts import page_1_layout,page_2_layout
import callbacks





app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),

    #store the timestr created in browser session so download same PPT later
html.Div([dcc.Store(id="timestr", data = 0,storage_type="session")]),

    #store the AXM images in a master list created in browser session
html.Div([dcc.Store(id="axmimages", data = [],storage_type="session")]),

#store all the AXM images measurements in a master list created in browser session
html.Div([dcc.Store(id="ll", data = [],storage_type="session")]),

#store the directory created in browser session
html.Div([dcc.Store(id="ud_data", data = [],storage_type="session")]),

#store the all uploaded flies list created in browser session
html.Div([dcc.Store(id="files_data", data = [],storage_type="session")]),

#store the length of uploaded flies list created in browser session
html.Div([dcc.Store(id="files_len_data", data = 0,storage_type="session")]),

#store the dataframe of coordinates 
#needs reset
html.Div([dcc.Store(id="df", data = [],storage_type="memory")]),

#store the auto cannied image 
#needs reset
html.Div([dcc.Store(id="auto", data = [],storage_type="memory")]),

#store the original image 
#needs reset
html.Div([dcc.Store(id="image", data = 0,storage_type="memory")]),

#store the x counter values
#needs reset
html.Div([dcc.Store(id="xcounter", data = 0,storage_type="memory")]),

#store the y counter values
#needs reset
html.Div([dcc.Store(id="ycounter", data = 0,storage_type="memory")]),

#store the scalebar values
#needs reset
html.Div([dcc.Store(id="scale", data = [],storage_type="memory")]),

#store the x coor values
#needs reset
html.Div([dcc.Store(id="xcoor", data = [],storage_type="memory")]),

#store the y coor values
#needs reset
html.Div([dcc.Store(id="ycoor", data = [],storage_type="memory")]),

#store the r values (loop to next image)
#needs to be added!!!!
html.Div([dcc.Store(id="r", data = 0,storage_type="session")]),


#store the length values of a single image
#needs to be reset
html.Div([dcc.Store(id="l", data = [],storage_type="memory")]),


])


#with new url display the relevent page
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              State('files_len_data','data'),
              State('r','data'))
def display_page(pathname,fldata,r):
    if pathname == '/start' and r<=fldata:
        return page_2_layout
    else:
        return page_1_layout

