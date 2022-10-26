import dash
from dash.dependencies import Input, Output,State
import base64
import os
from urllib.parse import quote as urlquote
import uuid
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
from app import app
from dash_extensions import Download
from dash_extensions.snippets import send_file
#from pptx import Presentation
#from pptx.util import Inches,Pt
import time





font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX

def saver2(files,measurements,timestr):
    prs = Presentation()
    #meausrements is my ll
    #files is my axmimages list
    for n in range(len(files)):
        print(n)
        pathh = files[n]
        print(f"filepath is {pathh}")
        lyt=prs.slide_layouts[1] # choosing a slide layout with title
        slide=prs.slides.add_slide(lyt) # adding a slide
        title=slide.shapes.title # assigning a title
        title.text=str(files[n])[54:] # title
        title_para = slide.shapes.title.text_frame.paragraphs[0]
        title_para.font.name = "Calibri"
        title_para.font.size = Pt(15)
        img=slide.shapes.add_picture(pathh, (prs.slide_width - Inches(5)) / 2,(prs.slide_width - Inches(5))/3,
                               width=Inches(5), height=Inches(5))

        lyt=prs.slide_layouts[6] # choosing a slide layout which is blankk
        slide=prs.slides.add_slide(lyt) 
        x, y, cx, cy = Inches(2), Inches(2), Inches(4), Inches(1.5)
        shape = slide.shapes.add_table(len(measurements[n])+1, 1, x, y, cx, cy)
        table = shape.table
        cell = table.cell(0, 0)
        cell.text = 'Measurements/au'
        #for every measurement , create a new appending the value
        s=1
        for a in measurements[n]:
            cell = table.cell(s, 0)
            cell.text = str(a)
            s = s + 1

    prs.save("AXM"+timestr+".pptx")


def auto_canny(i, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(i)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0- sigma) * v))
    upper = int(min(255, (1.0+ sigma) * v))
    edged = cv2.Canny(i, lower, upper)
    # return the optimal edged/countour image
    return edged


def save_file(name, content,UPLOAD_DIRECTORY):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))

#to create files list of all the files uploaded
def uploaded_files(UPLOAD_DIRECTORY):
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(path)
    #only if files is not empty then return it or not dun do anything
    #this prevent continous looping
    if len(files)!=0:
        return files


#need output file data,directory data,timestr data(for saving under same file name),files_len_data for use in saver to dcc.store so it can be referred in /start
#once uploaded then change url immediately 
@app.callback(Output('url', 'pathname'),
              Output('ud_data','data'),
              Output('files_data','data'),
              Output('files_len_data','data'),
              Output('timestr','data'),
              Input('upload-image', 'contents'),
              Input('upload-image', 'filename'),
              prevent_initial_call=True
              )
# only if going to upload file then create folder  or not return nothing for each of the output 
def affirmative(contents,fnames):
    if contents is not None and fnames is not None:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        id = str(uuid.uuid4())
        UPLOAD_DIRECTORY = os.path.join(r"C:\Users\cvaahsan\Desktop\OpenCVStuff\AXM_Prod\assets",id)
        os.mkdir(UPLOAD_DIRECTORY)
        print(f"Created a new folder {id}")
        for name, data in zip(fnames, contents):
            save_file(name, data,UPLOAD_DIRECTORY)
        files = uploaded_files(UPLOAD_DIRECTORY)
        print(f"Any files here ?{files}")
        return "/start",UPLOAD_DIRECTORY,files,len(files),timestr
    else:
        return None,None,None,0,0




#show canny image and also adjust blur value with the slide bar
#state for the file data, directory data,r
#input is slider
@app.callback(
Output('graph-picture','figure'),
Output('graph-picture2', 'figure'),
Output('df','data'),
Output('image','data'),
Input('my-slider', 'value'),
State('files_data','data'),
State('ud_data','data'),
State('r','data'))

def update_output(slidervalue,data,udata,r):
    #print(f"this is my new files data {data}")
    #print(f"this is my new upload directory data {udata}")

    #print(f"r values is {r}")


    image = cv2.imread(data[r])
    fig = px.imshow(image)
    fig.update_layout(width=int(1200),height=int(1200))


    blurred = cv2.GaussianBlur(image, (slidervalue,slidervalue),0)
    auto = auto_canny(blurred)

    #changed retrival method from cv2.RETR_EXTERNAL to cv2.RETR_LIST
    contours, hierarchy = cv2.findContours(auto, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    #stack the mulitple arrays into a single array
    d = np.vstack(contours)

    #flatten the array to 1D
    e = d.ravel()   

    x = []
    y = []

    b = 0

    # do unpacking of list e into x and y where x is the odd index and y is the even index
    for a in e:
        if (b%2==0):
            x.append(e[b])
        else:
            y.append(e[b])
        b=b+1

    #make a dataframe out of the 2 lists with columns x and y
    df = pd.DataFrame({"x":x,"y":y})

    #remove the duplicates 
    df = df.drop_duplicates()

    fig2 = px.imshow(auto)
    fig2.update_layout(width=int(1200),height=int(1200))
    
    #cant output df for dcc.store
    return fig,fig2,df.to_json(orient="split"),image


#give annotated image based on the slider 
#need annotate here
#input is only the clicking on graph pict,slider value,scale bar,x Dir,Y Dir button
#rest of them are states
#need output the xcounter,ycounter so that can swithc between X and Y Dir buttons
#need output scale,xcoor,ycoor so later can use in def final
#need output auto so that the same annotated images appears after we placed a dot on the picture
@app.callback(
Output('graph-picture4','figure'),
Output('auto','data'),
Output('xcounter','data'),
Output('ycounter','data'),
Output('scale','data'),
Output('xcoor','data'),
Output('ycoor','data'),
Input('graph-picture4', 'clickData'),
Input('my-slider', 'value'),
Input('Scale Bar', 'n_clicks'),
Input('X Dir', 'n_clicks'),
Input('Y Dir', 'n_clicks'),
State('image','data'),
State('auto','data'),
State('xcounter','data'),
State('ycounter','data'),
State('scale','data'),
State('xcoor','data'),
State('ycoor','data'),
State('files_data','data'),
State('r','data')
)

def annotater(clickData,slidervalue,sclick,xclick,yclick,image,auto,xcounter,ycounter,scale,xcoor,ycoor,data,r):
    #bring global here so after annotate with circle wont reset
    #global auto,xcounter,ycounter
    image = cv2.imread(data[r])
    #convert image type from list back to numpy array
    #after that use uint8 as per this link https://stackoverflow.com/questions/19103933/depth-error-in-2d-image-with-opencv-python
    #image = np.array(image)
    #image = np.uint8(image)

    #convert auto type from list back to numpy array
    auto = np.array(auto)

    print(f"xcounter is {xcounter}")
    print(f"ycounter is {ycounter}")
    print(f"xcoor is {xcoor}")
    print(f"ycoor is {ycoor}")
    print(f"scale is {scale}")


    print(f"x click is {xclick} and y click is {yclick}")
    #see last event either click or button event
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    print(f"last clicked is {changed_id}")
    #do this here so no lag between graphpicture 3 and here
    if clickData == None:
        blurred = cv2.GaussianBlur(image, (slidervalue,slidervalue),0)
        auto = auto_canny(blurred)
        fig4 = px.imshow(auto)
        fig4.update_layout(width=int(1200), height=int(1200))
        return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor

        #for the first scalre bar click 
    if sclick > xclick and sclick > yclick and clickData != None:
        print("SSSS")
        print(len(scale))
        x = int(clickData['points'][0]['x'])
        y = int(clickData['points'][0]['y'])
        cv2.circle(auto, (x,y),3,(255,153,255),-1)
        scale.append(x)
        print('sbola')
        print(scale)
        fig4 = px.imshow(auto)
        return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor
    #if first click is X
    elif xclick > yclick and clickData != None:
        #ensures that the previously click points dun go into xcoord list
        if 'X Dir' in changed_id:
            fig4 = px.imshow(auto)
            return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor
        else:
            print("XXXX")
            x = int(clickData['points'][0]['x'])
            y = int(clickData['points'][0]['y'])
            cv2.circle(auto, (x,y),3,(127,255,212),-1)
            xcoor.append([x, y])
            fig4 = px.imshow(auto)
            fig4.update_layout(width=int(1200),height=int(1200))
            print(f"X selected is {xcoor}")
            #just add this xcounter to show x dir measurement made
            xcounter = 1
            return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor
    #if first click is y
    elif yclick > xclick and clickData != None:
        #ensures that the previously click points dun go into xcoord list
        if 'Y Dir' in changed_id:
            fig4 = px.imshow(auto)
            fig4.update_layout(width=int(1200),height=int(1200))
            return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor
        else:
            print("YYYY")
            print(len(ycoor))
            x = int(clickData['points'][0]['x'])
            y = int(clickData['points'][0]['y'])
            cv2.circle(auto, (x,y),3,(127,255,212),-1)
            ycoor.append([x, y])
            fig4 = px.imshow(auto)
            fig4.update_layout(width=int(1200),height=int(1200))
            print(f"Y selected is {ycoor}")
            #just add this xcounter to show y dir measurement made
            ycounter = 1
            return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor
    #if click x first then this ensures y is measured next 
    elif xclick == yclick  and xcounter == 1 and clickData != None:
        #ensures that the previously click points dun go into ycoord list
        if 'Y Dir' in changed_id:
            fig4 = px.imshow(auto)
            fig4.update_layout(width=int(1200),height=int(1200))
            return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor
        else:
            print("YYYY")
            print(len(ycoor))
            x = int(clickData['points'][0]['x'])
            y = int(clickData['points'][0]['y'])
            cv2.circle(auto, (x,y),3,(127,255,212),-1)
            ycoor.append([x, y])
            fig4 = px.imshow(auto)
            fig4.update_layout(width=int(1200),height=int(1200))
            print(f"Y selected is {ycoor}")
            return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor
    #if click y first then this ensures x is measured next 
    elif xclick == yclick and ycounter==1 and clickData != None:
        #ensures that the previously click points dun go into xcoord list
        if 'X Dir' in changed_id:
            fig4 = px.imshow(auto)
            return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor
        else:
            print("XXXX")
            x = int(clickData['points'][0]['x'])
            y = int(clickData['points'][0]['y'])
            cv2.circle(auto, (x,y),3,(127,255,212),-1)
            xcoor.append([x, y])
            fig4 = px.imshow(auto)
            fig4.update_layout(width=int(1200),height=int(1200))
            print(f"X selected is {xcoor}")
            xcounter = 1
            return fig4,auto,xcounter,ycounter,scale,xcoor,ycoor


#say to user now to measure x direction then click this x button first 
#same for Y - Dir
@app.callback(
Output('coordinates','children'),
Input('X Dir', 'n_clicks'),
Input('Y Dir', 'n_clicks'))

def annotate(x,y):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'X Dir' in changed_id:
        return "Pls proceed to indicate X Dir Location Measurements"
    elif 'Y Dir' in changed_id:
        return "Pls proceed to indicate Y Dir Location Measurements"


#annotate the final image based on our algo once clicked submit 
#also save to PPT here using def saver2
#input value is the scale bar raw values user provided
#df is the dataframe from def update output
@app.callback(
Output('graph-picture5','figure'),
Output('l','data'),
Output('axmimages','data'),
Output('ll','data'),
Input('submit', 'n_clicks'),
State('input','value'),
State('df','data'),
State('image','data'),
State('files_data','data'),
State('scale','data'),
State('xcoor','data'),
State('ycoor','data'),
State('r','data'),
State('l','data'),
State('axmimages','data'),
State('ll','data'),
State('timestr','data'),
)

def final(submitclick,ip,df,image,data,scale,xcoor,ycoor,r,l,axmi,ll,timestr):
    #global n
    l=[]
    image = cv2.imread(data[r])
    
    print(f"xcoor is {xcoor} in final")
    print(f"ycoor is {ycoor} in final")
    print(f"scale is {scale} in final")

    if submitclick > 0:
        df = pd.read_json(df,orient='split')
        #float(dagger(files(n))/10^9)
        #ratio = float(dagger(files[n])/float(0.000000001))
        #print(ip)
        ratio  = scale[1]-scale[0]
        ratio = float(ip)/ratio
        print(ratio)
        #print(f"Ratio for multiplication later is {ratio}")
        #print("XXXX")
        for n in xcoor:

            i = n[0]

            #filter to only have y dir points in df
            df2a = df[df["y"] == n[1]]

            #filter to only have x dir points
            df3a = df2a[df2a["x"] == n[0]]

            #go left side in x dir until find a point (df size is not zero)
            while df3a.shape[0] == 0:
                df2a = df[df["y"] == n[1]]
                n[0] = n[0] - 1
                df3a = df2a[df2a["x"] == n[0]]

            #reset the x dir coord
            n[0] = i

            #filter to only have y dir points in df
            df2b = df[df["y"] == n[1]]

            #filter to only have x dir points
            df3b = df2b[df2b["x"] == n[0]]

            #go right side in x dir until find a point (df size is not zero)
            while df3b.shape[0] == 0:
                df2b = df[df["y"] == n[1]]
                n[0] = n[0] + 1
                df3b = df2b[df2b["x"] == n[0]]

            #convert df to list 
            A = df3a.values.tolist()
            B = df3b.values.tolist()
    

            #annontae with line based on the coordinates
            cv2.arrowedLine(image, A[0],B[0] , (255, 0, 255), 1)
            cv2.arrowedLine(image, B[0],A[0] , (255, 0, 255), 1)
            #input actual length in nm
            cv2.putText(image, str(round((B[0][0] - A[0][0])*ratio,2))+"au", (n[0], n[1]), font, 1, (255, 100, 255), 1)
            l.append(float(round((B[0][0] - A[0][0])*ratio,2)))
            print(l)
        
        #print("YYYY")
        for n in ycoor:

            i = n[1]

            #filter to only have coordinates in the x = n[0] line of sight 
            df2a = df[df["x"] == n[0]]

            #filter to only have coordinates in the y = n[1] line of sight
            df3a = df2a[df2a["y"] == n[1]]

            #go down side in y dir until find a point (df size is not zero)
            while df3a.shape[0] == 0:
                df2a = df[df["x"] == n[0]]
                n[1] = n[1] - 1
                df3a = df2a[df2a["y"] == n[1]]

            #reset the y dir coord
            n[1] = i

            #filter to only have coordinates in the x = n[0] line of sight 
            df2b = df[df["x"] == n[0]]

            #filter to only have coordinates in the y = n[1] line of sight
            df3b = df2b[df2b["y"] == n[1]]

            #go up side in y dir until find a point (df size is not zero)
            while df3b.shape[0] == 0:
                df2b = df[df["x"] == n[0]]
                n[1] = n[1] + 1
                df3b = df2b[df2b["y"] == n[1]]

            #convert df to list 
            A = df3a.values.tolist()
            B = df3b.values.tolist()

            #annontae with line based on the coordinates
            cv2.arrowedLine(image, A[0],B[0] , (255, 0, 255), 1)
            cv2.arrowedLine(image, B[0],A[0] , (255, 0, 255), 1)
            #input actual length in au
            cv2.putText(image, str(round((B[0][1] - A[0][1])*ratio,2))+"au", (n[0], n[1]), font, 1, (255, 100, 255), 1)
            #append every measuremnts into l
            l.append(float(round((B[0][1] - A[0][1])*ratio,2)))
            
            

        #print(l)
        #for evey image all the measurements append into master list ll
        ll.append(l)
        #create a new image with the annotations with AXM name at the back
        cv2.imwrite(str(data[r])[:-4]+"axm.JPG",image)
        #save image path into master image list axmi
        axmi.append(str(data[r])[:-4]+"axm.JPG")
        #print(f"ll is {ll}")
        #print(f"axmi is {axmi}")
        #save to ppr
        saver2(axmi,ll,timestr)
        fig5 = px.imshow(image)
        
        fig5.update_layout(width=int(1200),height=int(1200))
        return fig5,l,ll,axmi
    else:
        fig = px.imshow(image)
        fig.update_layout(width=int(1200),height=int(1200))
        return fig,l,ll,axmi




#button to go to next image
#'IT' is linked 
#r added once click next image
@app.callback(
    Output('r','data'),
    Input('AO','n_clicks'),
    State('l','data'),
    State('r','data'),
    State('files_data','data'))
    
def onemore(AOclicks,l,r,data):
    #AOClikcs resets after refresh
    if AOclicks==1:
        r = r + 1
        return r
    else:
        return r

#to downlaod ppt , need timestr cos want to download the specific one you created earlier 
@app.callback(
    Output("download-image", "data"),
    Input("btn_image", "n_clicks"),
    State('timestr','data'),
    prevent_initial_call=True)
def func(n_clicks,timestr):
    return send_file(r"C:\Users\cvaahsan\Desktop\OpenCVStuff\AXM_Prod\AXM"+timestr+".pptx")


#just remind user to download ppt at the last image 
@app.callback(
    Output('reminder for PPT', 'displayed'),
    Input('submit', 'n_clicks'),
    State('r','data'),
    State('files_len_data','data'),
    )

def display_confirm(submit,r,fldata):
    print(f"r is {r} and fldata is {fldata}")
    if submit ==1 and (r == fldata-1 or r == fldata-2):
        return True
    else:
        return False
