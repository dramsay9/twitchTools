import cv2
from deepface import DeepFace
from gaze_tracking import GazeTracking
import numpy as np
import time

face_cascade_name = cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'  #getting a haarcascade xml file
face_cascade = cv2.CascadeClassifier()  #processing it for our project
if not face_cascade.load(cv2.samples.findFile(face_cascade_name)):  #adding a fallback event
    print("Error loading xml file")

gaze = GazeTracking()

video=cv2.VideoCapture(2)  #requisting the input from the webcam or camera

img_new = cv2.imread("templates/emotion_template_gaze.png")
gaze_background = img_new[1278:1280+102,307:309+402].copy()
gaze_points = [(309+200,1280+50)]*40

def draw_gaze(img, new_gazepoint):
	
    #redraw background
    img[1278:1280+102,307:309+402] = gaze_background

    #draw points on top	
    for i in range(len(gaze_points)):
        x,y = gaze_points[i]
        colorval = round(220-(i*(220/40)))
        colorval2 = round(155+(i*(100/40)))
        cv2.line(img, (x-6,y-6), (x+6,y+6), (colorval,colorval2,colorval), 4)
        cv2.line(img, (x+6,y-6), (x-6,y+6), (colorval,colorval2,colorval), 4)
        
    if new_gazepoint[0] is None:
        #failed to detect a new gazepoint
        cv2.putText(img, 'undetected.', (312,1370), cv2.FONT_HERSHEY_SIMPLEX, 1, (76,52,255), 2, cv2.LINE_AA)
    else:
        #gaze is between 0-1 (x,y)
        new_x = round(314 + 390*min(1,new_gazepoint[0]))
        new_y = round(1290 + 80 - 80*min(1,new_gazepoint[1]))

        #add new gazepoint
        gaze_points.pop(0)
        gaze_points.append((new_x, new_y))
        
        #draw it
        cv2.line(img, (new_x-8,new_y-8), (new_x+8,new_y+8), (0,0,0), 5)
        cv2.line(img, (new_x+8,new_y-8), (new_x-8,new_y+8), (0,0,0), 5)



def fill_rect(img, x, val, color):
    if color=='red':
        if val < 15:
            c=(204,204,255)
        elif val < 30:
            c=(102,102,255)
        else:
            c=(0,0,255)
    elif color=='blue':
        if val < 15:
            c=(255,229,204)
        elif val < 30:
            c=(255,178,102)
        else:
            c=(255,128,0)
    elif color=='purple':
        if val < 15:
            c=(255,204,229)
        elif val < 30:
            c=(255,102,178)
        else:
            c=(255,0,127)
    elif color=='grey':
        if val < 15:
            c=(224,224,224)
        elif val < 30:
            c=(160,160,160)
        else:
            c=(128,128,128)
    elif color=='green':
        if val < 15:
            c=(204,255,204)
        elif val < 30:
            c=(102,255,102)
        else:
            c=(0,255,0)
    elif color=='yellow':
        if val < 15:
            c=(204,255,255)
        elif val < 30:
            c=(102,255,255)
        else:
            c=(0,255,255)
    elif color=='magenta':
        if val < 15:
            c=(229,204,255)
        elif val < 30:
            c=(178,102,255)
        else:
            c=(127,0,255)

    cv2.rectangle(img, (x,220), (x+40, 220+275), (255,255,255), -1)
    cv2.rectangle(img, (x,220+(270-round(val*2.7))), (x+40, 220+275), c, -1)

    if val < 15:
        c=(224,224,224)
    elif val < 30:
        c=(160,160,160)
    else:
        c=(128,128,128)

    cv2.rectangle(img, (x+1,221+(270-round(val*2.7))), (x+39, 220+274), c, 2)

tick = time.perf_counter()

durations = {'happy':0, 'sad':0,'surprise':0,'angry':0,'fear':0,'disgust':0,'neutral':0}
amount = {'happy':0,'sad':0,'surprise':0,'angry':0,'fear':0,'disgust':0,'neutral':0,'total':0}

while video.isOpened():  #checking if are getting video feed and using it
    _,frame = video.read()
    tock = time.perf_counter()	

    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)  #changing the video to grayscale to make the face analisis work properly
    face=face_cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5)
    gaze.refresh(frame)


    try:

        analyze = DeepFace.analyze(frame,actions=['emotion'])

        frame = gaze.annotated_frame()

        x,y,w,h = face[0]
        img_new[233:233+314,49:49+314] = cv2.resize(frame[y:y+h, x:x+w], (314,314))

	#main text
        cv2.rectangle(img_new, (394,34), (394+530,34+110), (255,255,255), -1)
        cv2.putText(img_new, ' ' + analyze[0]['dominant_emotion'].upper() + ' (%2.0f%%)' % analyze[0]['emotion'][analyze[0]['dominant_emotion']], (394,123), cv2.FONT_HERSHEY_TRIPLEX, 1.6, (76,52,5), 2, cv2.LINE_AA)
	
        #ft.putText(img_new, analyze[0]['dominant_emotion'].upper() + '(%3.2f)' % analyze[0]['emotion'][analyze[0]['dominant_emotion']], (394,128), 40, (0,0,0), -1, cv2.LINE_AA, bottomLeftOrigin=True)

        fill_rect(img_new, 435, analyze[0]['emotion']['happy'], 'yellow')
        fill_rect(img_new, 503, analyze[0]['emotion']['sad'], 'blue')
        fill_rect(img_new, 571, analyze[0]['emotion']['surprise'], 'magenta')
        fill_rect(img_new, 639, analyze[0]['emotion']['angry'], 'red')
        fill_rect(img_new, 707, analyze[0]['emotion']['fear'], 'purple')
        fill_rect(img_new, 774, analyze[0]['emotion']['disgust'], 'green')
        fill_rect(img_new, 842, analyze[0]['emotion']['neutral'], 'grey')

        passed = tock-tick
        tick = tock
        if passed < 1:
            durations[analyze[0]['dominant_emotion']] += passed/60

        for emote in durations.keys():
            amount[emote] += analyze[0]['emotion'][emote]		

        amount['total'] += 1
        
        cv2.rectangle(img_new, (478, 624), (478+400, 624+65), (255,255,255), -1)
        cv2.putText(img_new, '%2.1f mins (%02.1f%%)' % (durations['happy'], amount['happy']/amount['total']), (478,614+65), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (6,5,5), 1, cv2.LINE_AA)

        cv2.rectangle(img_new, (478, 708), (478+400, 708+65), (255,255,255), -1)
        cv2.putText(img_new, '%2.1f mins (%02.1f%%)' % (durations['sad'], amount['sad']/amount['total']), (478,763), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (6,5,5), 1, cv2.LINE_AA)

        cv2.rectangle(img_new, (478, 793), (478+400, 793+65), (255,255,255), -1)
        cv2.putText(img_new, '%2.1f mins (%02.1f%%)' % (durations['surprise'], amount['surprise']/amount['total']), (478,848), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (6,5,5), 1, cv2.LINE_AA)
	
        cv2.rectangle(img_new, (478, 877), (478+400, 877+65), (255,255,255), -1)
        cv2.putText(img_new, '%2.1f mins (%02.1f%%)' % (durations['angry'], amount['angry']/amount['total']), (478,867+65), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (6,5,5), 1, cv2.LINE_AA)

        cv2.rectangle(img_new, (478, 962), (478+400, 962+65), (255,255,255), -1)
        cv2.putText(img_new, '%2.1f mins (%02.1f%%)' % (durations['fear'], amount['fear']/amount['total']), (478,952+65), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (6,5,5), 1, cv2.LINE_AA)

        cv2.rectangle(img_new, (478, 1046), (478+400, 1046+65), (255,255,255), -1)
        cv2.putText(img_new, '%2.1f mins (%02.1f%%)' % (durations['disgust'], amount['disgust']/amount['total']), (478,1036+65), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (6,5,5), 1, cv2.LINE_AA)

        cv2.rectangle(img_new, (478, 1131), (478+400, 1131+65), (255,255,255), -1)
        cv2.putText(img_new, '%2.1f mins (%02.1f%%)' % (durations['neutral'], amount['neutral']/amount['total']), (478,1121+65), cv2.FONT_HERSHEY_TRIPLEX, 1.3, (6,5,5), 1, cv2.LINE_AA)

        draw_gaze(img_new, (gaze.horizontal_ratio(), gaze.vertical_ratio()))

    except Exception as e:
        pass
        #print('no face detected')
        #print(e)

    #img_resize = cv2.resize(img_new, (308,483))
    img_resize = cv2.resize(img_new, (462,725))

    #this is the part where we display the output to the user
    cv2.imshow('classifier', img_resize)

    key=cv2.waitKey(1) 
    if key==ord('q'):   # here we are specifying the key which will stop the loop and stop all the processes going
        break

video.release()
