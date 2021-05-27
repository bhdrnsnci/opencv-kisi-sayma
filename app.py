from flask import Flask, Response, render_template
from datetime import date
import sqlite3
import io
import numpy as np
import cv2 as cv
import Person
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)

count = 0
control = True
tyear = ""
tmonth = ""
tday = ""
nyear = ""
nmonth = ""
nday = ""
vyear = ""
vmonth = ""
vday = ""
vtnumbers = 0

def webStream():
    global count
    global control
    global tyear
    global tmonth
    global tday
    global nyear
    global nmonth
    global nday
    global vyear
    global vmonth
    global vday
    global vtnumbers

    today = date.today()
    tyear = str(today.year)
    tmonth = str(today.month)
    tday = str(today.day)

    cap = cv.VideoCapture("a.avi")

    h = 480
    w = 640
    frameArea = h*w
    areaTH = frameArea/250

    line_up = int(2*(h/5))
    line_down   = int(3*(h/5))

    up_limit =   int(1*(h/5))
    down_limit = int(4*(h/5))
    
    pt1 =  [line_down,0]
    pt2 =  [line_down,w]
    pts_L1 = np.array([pt1,pt2], np.int32)
    pts_L1 = pts_L1.reshape((-1,1,2))
    pt3 =  [line_up,0]
    pt4 =  [line_up,w]
    pts_L2 = np.array([pt3,pt4], np.int32)
    pts_L2 = pts_L2.reshape((-1,1,2))

    pt5 =  [up_limit,0]
    pt6 =  [up_limit,w]
    pts_L3 = np.array([pt5,pt6], np.int32)
    pts_L3 = pts_L3.reshape((-1,1,2))
    pt7 =  [down_limit,0]
    pt8 =  [down_limit,w]
    pts_L4 = np.array([pt7,pt8], np.int32)
    pts_L4 = pts_L4.reshape((-1,1,2))

    fgbg = cv.createBackgroundSubtractorMOG2(detectShadows = True)

    kernelOp = np.ones((3,3),np.uint8)
    kernelCl = np.ones((11,11),np.uint8)

    font = cv.FONT_HERSHEY_SIMPLEX
    persons = []
    max_p_age = 5
    pid = 1
    if (cap.isOpened):
        control = True
    else:
        control = False
    

    while(control):
        _, frame = cap.read()
        now = date.today()
        nyear = str(now.year)
        nmonth = str(now.month)
        nday = str(now.day)
        with sqlite3.connect("Counter.db") as cdb:
            cursor = cdb.cursor()
            cursor.execute("select * from people where id = (select max(id) from people)")
            rows = cursor.fetchall()
            for row in rows:
                vyear = row[1]
                vmonth = row[2]
                vday = row[3]

        for i in persons:
            i.age_one()

        fgmask = fgbg.apply(frame)
        
        try:
            _,imBin= cv.threshold(fgmask,200,255,cv.THRESH_BINARY)
            mask = cv.morphologyEx(imBin, cv.MORPH_OPEN, kernelOp)
            mask =  cv.morphologyEx(mask , cv.MORPH_CLOSE, kernelCl)
        except:
            break
        
        contours0, hierarchy = cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours0:
            area = cv.contourArea(cnt)
            if area > areaTH:
                M = cv.moments(cnt)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                x,y,w,h = cv.boundingRect(cnt)

                new = True
                if cy in range(up_limit,down_limit):
                    for i in persons:
                        if abs(x-i.getX()) <= w and abs(y-i.getY()) <= h:
                            new = False
                            i.updateCoords(cx,cy)
                            if i.going_UP(line_down,line_up) == True:
                                count += 1
                                
                            elif i.going_DOWN(line_down,line_up) == True:
                                count += 1
                            break

                        if i.getState() == '1':
                            if i.getDir() == 'down' and i.getY() > down_limit:
                                i.setDone()
                            elif i.getDir() == 'up' and i.getY() < up_limit:
                                i.setDone()
                        if i.timedOut():
                            index = persons.index(i)
                            persons.pop(index)
                            del i

                    if new == True:
                        p = Person.MyPerson(pid,cx,cy, max_p_age)
                        persons.append(p)
                        pid += 1     
                        
                cv.circle(frame,(cx,cy), 5, (0,0,255), -1)
                img = cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)       
            
        str_up = str(count)
        cv.putText(frame, str_up ,(10,40),font,0.5,(255,255,255),2,cv.LINE_AA)
        cv.putText(frame, str_up ,(10,40),font,0.5,(0,0,0),1,cv.LINE_AA)

        imgShow = cv.imencode('.jpg', frame)[1]
        imgData = imgShow.tobytes()
        yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n' + imgData + b'\r\n')    

        if (tyear != nyear or tmonth != nmonth or tday != nday):
            # Gün atlar
            if (tyear == vyear and tmonth == vmonth and tday == vday):
                # Veritabanında güncelleme yapar
                with sqlite3.connect("Counter.db") as cdb:
                    cursor = cdb.cursor()
                    cursor.execute("select * from people where id = (select max(id) from people)")
                    rows = cursor.fetchall()
                    for row in rows:
                        vtnumbers = row[4]
                    cursor.execute("update people set numbers=? where year=? and month=? and day=?", ((vtnumbers+count), tyear, tmonth, tday))
                tyear = nyear
                tmonth = nmonth
                tday = nday
                count = 0
            else:
                # Veritabanına yeni tarih ekler.
                with sqlite3.connect("Counter.db") as cdb:
                    cursor = cdb.cursor()
                    cursor.execute("insert into people(year, month, day, numbers) values(?,?,?,?)", (tyear, tmonth, tday, count))
                tyear = nyear
                tmonth = nmonth
                tday = nday
                count = 0

        k = cv.waitKey(30) & 0xff
        if k == 27:
            break

# def reportStream():
#     dates = []
#     numbers = []
#     with sqlite3.connect("Counter.db") as cdb:
#         cursor = cdb.cursor()
#         cursor.execute("select * from people")
#         rows = cursor.fetchall()
#         for row in rows:
#             date = row[1]+"-"+row[2]+"-"+row[3]
#             dates.append(date)
#             numbers.append(row[4])
#     plt.plot(dates,numbers,"b--")
#     plt.show()

@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    dates = []
    numbers = []
    with sqlite3.connect("Counter.db") as cdb:
        cursor = cdb.cursor()
        cursor.execute("select * from people")
        rows = cursor.fetchall()
        for row in rows:
            date = row[1]+"-"+row[2]+"-"+row[3]
            dates.append(date)
            numbers.append(row[4])
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.grid()
    axis.plot(dates, numbers)
    return fig

@app.route("/frame")
def frame():
    return Response(webStream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/exit")
def exit():
    global count
    global control
    global tyear
    global tmonth
    global tday
    global nyear
    global nmonth
    global nday
    global vyear
    global vmonth
    global vday
    global vtnumbers
    if (tyear == vyear and tmonth == vmonth and tday == vday):
        # Veritabanında güncelleme yapar
        with sqlite3.connect("Counter.db") as cdb:
            cursor = cdb.cursor()
            cursor.execute("select * from people where id = (select max(id) from people)")
            rows = cursor.fetchall()
            for row in rows:
                vtnumbers = row[4]
            cursor.execute("update people set numbers=? where year=? and month=? and day=?", ((vtnumbers+count), tyear, tmonth, tday))
            count = 0
    else:
        # Veritabanına yeni tarih ekler.
        with sqlite3.connect("Counter.db") as cdb:
            cursor = cdb.cursor()
            cursor.execute("insert into people(year, month, day, numbers) values(?,?,?,?)", (tyear, tmonth, tday, count))
            count = 0
    return render_template("index.html")

@app.route("/countcam")
def countcam():
    return render_template("countcam.html")
        
@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=False, threaded=True)