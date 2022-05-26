import time as t 
import paho.mqtt.client as mqtt
import cv2
import pygame
track = 0
def on_connect(client, userdata, flags, rc):
    global gamestart
    print("Connection returned result: "+str(rc))
    gamestart = rc
    client.subscribe('1Team8TrackB',qos=1)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')

def on_message(client, userdata, message):
    if int(message.payload) == 1:
        track = 1 

    
client = mqtt.Client()
# add additional client options (security, certifications, etc.)
# many default options should be good to start off.
# add callbacks to client.
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
# 2. connect to a broker using one of the connect*() functions.
client.connect_async("test.mosquitto.org")
client.loop_start()

def track_player(frame,lower_thresh_player,upper_thresh_player):
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
            x_pos = 1200 - (x + int(w/2))*2

def get_calibration_frames(frame):
    global x_c_1
    global x_c_2
    global y_c_1
    global y_c_2
    global counter
    x_c_1 = 200
    x_c_2 = 400
    y_c_1 = 250
    y_c_2 = 495
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.rectangle(frame, (x_c_1, y_c_1), (x_c_2, y_c_2), (0, 255, 0), 3)

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

def calibration():
    global counter
    global lower_thresh_player
    global upper_thresh_player
    surface = pygame.display.set_mode([1200,800])
    while (True):
        ret, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        if counter <= 301:
            get_calibration_frames(frame)
        elif counter == 302:
            print('calibrating...')
            t.sleep(1)
            calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2)
        elif counter > 302:
            print('exiting calibration...')
            return
        counter = counter+1
    # The video uses BGR colors and PyGame needs RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        surf = pygame.surfarray.make_surface(frame)
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                background_color = red
                surface.fill(background_color)
                pygame.display.update
                end_time = self.time()
        surface.blit(calimg,(0,0))
        # Show the PyGame surface!
        surface.blit(surf, (300,300))
        pygame.display.flip()
#vision processing code
calibration()
cap = cv2.VideoCapture(0)
fps = cap.get(cv2.CAP_PROP_FPS)
#cam is 30fps
cap.set(cv2.CAP_PROP_FPS, 30)
while(1):
    ret, frame = cap.read()
    frame = cv2.flip(frame,0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    track_player(frame, lower_thresh_player, upper_thresh_player)
    while(track == 1):
        client.publish('1Team8TrackA',str(x_pos),qos=1)
        t.sleep(.5)
