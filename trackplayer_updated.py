#https://www.pyimagesearch.com/2021/01/20/opencv-getting-and-setting-pixels/

import numpy as np
import cv2
import time as t
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


cap = cv2.VideoCapture(0)
init_cal = False
x_c_1 = 0
y_c_1 = 0
x_c_2 = 0
y_c_2 = 0
lower_thresh_player_1 = np.array([0, 0, 0])
upper_thresh_player_1 = np.array([0, 0, 0])
lower_thresh_player_2 = np.array([0, 0, 0])
upper_thresh_player_2 = np.array([0, 0, 0])
lower_thresh_player_3 = np.array([0, 0, 0])
upper_thresh_player_3 = np.array([0, 0, 0])
prev_player_pos = np.array([0, 0])
counter = 0 

def track_player(frame, lower_thresh_player, upper_thresh_player):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get only blue colors
    mask_1 = cv2.inRange(hsv, lower_thresh_player_1, upper_thresh_player_1)
    mask_2 = cv2.inRange(hsv, lower_thresh_player_2, upper_thresh_player_2)
    mask_3 = cv2.inRange(hsv, lower_thresh_player_3, upper_thresh_player_3)
    mask = mask_1 + mask_2 + mask_3
    ret,thresh = cv2.threshold(mask,127,255,0)
    res = cv2.bitwise_and(frame,frame, mask= mask)
    #from threshholding cv doc
    th3 = cv2.adaptiveThreshold(mask,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(contours)
    for i in contours:
        area = cv2.contourArea(i)
        if area > 700:
            x,y,w,h = cv2.boundingRect(i)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
    #print( M )
    #cv.imshow('frame', frame)


def get_calibration_frames(frame):
    global x_c_1
    global x_c_2
    global y_c_1
    global y_c_2
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #lower_thresh_LED = np.array([0, 0, 250]) #LED
    #upper_thresh_LED = np.array([179, 10, 255]) #LED
    lower_thresh_LED = np.array([36, 25, 200]) #green LED
    upper_thresh_LED = np.array([86, 255, 255]) #green LED

    mask = cv2.inRange(hsv, lower_thresh_LED, upper_thresh_LED)
    _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if counter == 1:
        print('stand in middle of frame and remain still during calibration')
    if counter == 25:
        print('hold led near top of left shoulder')
    for i in contours:
        #get rid of noise first by calculating area
        area = cv2.contourArea(i)
        if area > 100 and area < 400:
            #cv2.drawContours(frame, [i], -1, (0, 255, 0), 2)
            x, y, width, height = cv2.boundingRect(i)
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)
            x2 = x + width
            y2 = y + height
            if counter == 400:
                x_c_1 = x + (width//2)
                y_c_1 = x + (height//2)
                print('bottom left corner calibration complete')
                print('hold led near left hip')
            if counter == 800:
                x_c_2 = x + (width//2)
                y_c_2 = x + (height//2)
                print(x_c_1)
                print(x_c_2)
                print(y_c_1)
                print(y_c_2)
                print('top right corner calibration complete')

def make_histogram(cluster):
    """
    Count the number of pixels in each cluster
    :param: KMeans cluster
    :return: numpy histogram
    """
    numLabels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    hist, _ = np.histogram(cluster.labels_, bins=numLabels)
    hist = hist.astype('float32')
    hist /= hist.sum()
    return hist


def make_bar(height, width, color):
    """
    Create an image of a given color
    :param: height of the image
    :param: width of the image
    :param: BGR pixel values of the color
    :return: tuple of bar, rgb values, and hsv values
    """
    bar = np.zeros((height, width, 3), np.uint8)
    bar[:] = color
    red, green, blue = int(color[2]), int(color[1]), int(color[0])
    hsv_bar = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
    hue, sat, val = hsv_bar[0][0]
    return bar, (red, green, blue), (hue, sat, val)


def sort_hsvs(hsv_list):
    """
    Sort the list of HSV values
    :param hsv_list: List of HSV tuples
    :return: List of indexes, sorted by hue, then saturation, then value
    """
    bars_with_indexes = []
    for index, hsv_val in enumerate(hsv_list):
        bars_with_indexes.append((index, hsv_val[0], hsv_val[1], hsv_val[2]))
    bars_with_indexes.sort(key=lambda elem: (elem[1], elem[2], elem[3]))
    return [item[0] for item in bars_with_indexes]

def calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2):
    global lower_thresh_player_1
    global upper_thresh_player_1
    global lower_thresh_player_2
    global upper_thresh_player_2
    global lower_thresh_player_3
    global upper_thresh_player_3
    cv2.rectangle(frame, (x_c_1, y_c_1), (x_c_2, y_c_2), (0, 255, 0), 3)
    print(x_c_1)
    print(x_c_2)
    print(y_c_1)
    print(y_c_2)
    calibration_frame = frame[y_c_1:y_c_2, x_c_1:x_c_2]
    cal_hsv = cv2.cvtColor(calibration_frame, cv2.COLOR_BGR2HSV)
    img = cal_hsv
    height, width, _ = np.shape(img)

    # reshape the image to be a simple list of RGB pixels
    image = img.reshape((height * width, 3))

    # we'll pick the 5 most common colors
    num_clusters = 3
    clusters = KMeans(n_clusters=num_clusters)
    clusters.fit(image)

    # count the dominant colors and put them in "buckets"
    histogram = make_histogram(clusters)
    # then sort them, most-common first
    combined = zip(histogram, clusters.cluster_centers_)
    combined = sorted(combined, key=lambda x: x[0], reverse=True)

    # finally, we'll output a graphic showing the colors in order
    bars = []
    hsv_values = []
    for index, rows in enumerate(combined):
        bar, rgb, hsv = make_bar(100, 100, rows[1])
        print(f'Bar {index + 1}')
        print(f'  RGB values: {rgb}')
        print(f'  HSV values: {hsv}')
        hsv_values.append(hsv)
        bars.append(bar)

    print(cal_hsv.shape)
    h_val = cal_hsv[:,:,0]
    s_val = cal_hsv[:,:,1]
    v_val = cal_hsv[:,:,2]
    h_val.sort()
    s_val.sort()
    v_val.sort()
    #discard outliers
    print(h_val.shape)
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
    print(hsv_avg)
    lower_thresh_player = np.array([int(avg_h)-10,int(avg_s)-10,int(avg_v)-10])
    upper_thresh_player = np.array([int(avg_h)+10,255,255])
    print(lower_thresh_player)
    print(upper_thresh_player)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if counter <= 800:
        get_calibration_frames(frame)
    elif counter == 801:
        calibrate(frame, x_c_1, y_c_1, x_c_2, y_c_2)
    elif counter > 801 and counter < 830:
        print('center shirt in box and stay still')
        cv2.rectangle(frame, (x_c_1, y_c_1), (x_c_2, y_c_2), (0, 255, 0), 3)
    else:
    	track_player(frame, lower_thresh_player, upper_thresh_player)


    counter = counter+1
    cv2.imshow('calibrating frame', frame)
    cv2.resizeWindow('calibrating frame', 600,600)
    #print(counter)
    # Display the resulting frames
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

