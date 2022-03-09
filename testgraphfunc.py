#https://towardsdatascience.com/finding-most-common-colors-in-python-47ea0767a06a

import numpy as np
import cv2
import time as t
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from collections import Counter

cap = cv2.VideoCapture(0)
init_cal = False
x_c_1 = 0
y_c_1 = 0
x_c_2 = 0
y_c_2 = 0
x_pos = 0
prev_x = 0
prev_y = 0
lower_thresh_player = np.array([0, 0, 0])
upper_thresh_player = np.array([0, 0, 0])
counter = 0 

def track_player(frame, lower_thresh_player, upper_thresh_player):
    global x_pos
    global prev_x
    global prev_y
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get colors of interest
    mask = cv2.inRange(hsv, lower_thresh_player, upper_thresh_player)
    ret,thresh = cv2.threshold(mask,127,255,0)
    res = cv2.bitwise_and(frame,frame, mask= mask)
    #from threshholding cv doc
    th3 = cv2.adaptiveThreshold(mask,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i in contours:
        area = cv2.contourArea(i)
        if area > 4000:
            x,y,w,h = cv2.boundingRect(i)
            #print(prev_x)
            #print(x)
            #if abs(prev_x - x) <= 150:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            x_pos = (x + int(w/2))*2
                #prev_x = x + w//2
                #prev_y = y + h//2
    #print( M )
    #cv.imshow('frame', frame)


def get_calibration_frames(frame):
    global x_c_1
    global x_c_2
    global y_c_1
    global y_c_2
    global counter
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_thresh_LED = np.array([0, 0, 250]) #LED
    upper_thresh_LED = np.array([179, 10, 255]) #LED

    mask = cv2.inRange(hsv, lower_thresh_LED, upper_thresh_LED)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.imshow('calibrating frame', frame)
    if counter == 1:
        print('stand in middle of frame and remain still during calibration')
    if counter == 25:
        print('hold led near top of right shoulder')
    for i in contours:
        #get rid of noise first by calculating area
        area = cv2.contourArea(i)
        if area > 100 and area < 400:
            #cv2.drawContours(frame, [i], -1, (0, 255, 0), 2)
            x, y, width, height = cv2.boundingRect(i)
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)
            x2 = x + width
            y2 = y + height
            if counter == 300:
                x_c_1 = x + (width//2)
                y_c_1 = x + (height//2)
                print('top right corner calibration complete')
                print('hold led near left hip')
            if counter == 600:
                x_c_2 = x + (width//2)
                y_c_2 = x + (height//2)
                print('bottom left corner calibration complete')
    if counter == 600 and (x_c_2-x_c_1 <= 0 or x_c_1 == 0 or x_c_2 == 0 or y_c_2-y_c_1 <= 0 or y_c_1 == 0 or y_c_2 == 0):
        print('calibration failed...try again')
        counter = 0


def calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2):
    global lower_thresh_player
    global upper_thresh_player
    global prev_x
    global prev_y
    global x_pos
    cv2.rectangle(frame, (x_c_1, y_c_1), (x_c_2, y_c_2), (0, 255, 0), 3)
    calibration_frame = frame[y_c_1:y_c_2, x_c_1:x_c_2]
    cal_hsv = cv2.cvtColor(calibration_frame, cv2.COLOR_BGR2HSV)
    x_pos = int(abs(x_c_1 - x_c_2)/2)
    h_val = cal_hsv[:,:,0]
    s_val = cal_hsv[:,:,1]
    v_val = cal_hsv[:,:,2]
    h_val.sort()
    s_val.sort()
    v_val.sort()
    #discard outliers
    (h,w) = h_val.shape
    h_low = h//8
    w_low = w//8
    h_high = h-h_low
    w_high = w-w_low
    h_val_ab = h_val[h_low:h_high,w_low:w_high]
    s_val_ab = s_val[h_low:h_high,w_low:w_high]
    v_val_ab = v_val[h_low:h_high,w_low:w_high]
    avg_h = np.average(h_val_ab)
    avg_s = np.average(s_val_ab)
    avg_v = np.average(v_val_ab)
    hsv_avg = np.array([int(avg_h),int(avg_s),int(avg_v)])
    lower_thresh_player = np.array([int(avg_h)-30,int(avg_s)-40,int(avg_v)-40])
    upper_thresh_player = np.array([int(avg_h)+30,int(avg_s)+100,int(avg_v)+100])
    # prev_x = (x_c_2 + x_c_1)//2
    # prev_y = (y_c_2 + y_c_1)//2
    # clt= KMeans(n_clusters=3)
    # clt.fit(calibration_frame.reshape(-1, 3))
    # show_img_compar(calibration_frame, palette_perc(clt))

def calibration():
    global counter
    global lower_thresh_player
    global upper_thresh_player
    while (True):
        ret, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        if counter <= 600:
            get_calibration_frames(frame)
            counter = counter+1
        elif counter == 601:
            pass
            #print('center shirt in box and stay still')
        elif counter == 602:
            print('calibrating...')
            t.sleep(3)
            calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2)
        elif counter > 602:
            print('exiting calibration !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            return
        counter = counter+1
        cv2.imshow('calibrating frame', frame)
        # Display the resulting frames
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

calibration()

while(True):
    # Capture frame-by-frame
    print('in while true ')
    ret, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # track player
    track_player(frame, lower_thresh_player, upper_thresh_player)
    cv2.imshow('calibrating frame', frame)
    #cv2.resizeWindow('calibrating frame', 600,600)
    # Display the resulting frames
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

