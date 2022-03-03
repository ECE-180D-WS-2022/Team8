from email import message
from pynput import keyboard
import time as t 
import paho.mqtt.client as mqtt
import threading
import ctypes
import speech_recognition as sr

GOAL_STOVE = 60
GOAL_CUTTING = 60
IDEAL_SPIN = 1
IDEAL_CUT = 1
FLAG_START = '01'
FLAG_CUTTING = '02'
FLAG_STOVE = '03'
FLAG_POUR = '04'
FLAG_FLIP = '05'
STOP = '00'


MESSAGE = '10'

FLAG_SCORE = '99'

#BOARD POSITIONS
CUTTING = 1
STOVE = -1
#BOARD POSITIONS

##CONST GLOBALS

#globals
position = 0
in_cooking = 0
key_prev = keyboard.Key.up
start = t.time()
end = t.time()
diff = end - start
total_stove = 0
total_cutting = 0
flag_player = 0
flag_opponent = 0
flag_received = 0
score = 0
message_received = ''
speed = 1
prev_pos = 1
#globals

# class thread_with_exception(threading.Thread):
#     def __init__(self, name):
#         threading.Thread.__init__(self)
#         self.name = name
             
#     def run(self):
#         global speed
 
#         # target function of the thread class
#         try:
#             speed = 1
#             i = 0
#             while(GOAL_STOVE>i):
#                 i = i+speed
#                 t.sleep(1)
#                 print("                           "+str(i), end="\r")
#         finally:
#             print('ended')
          
#     def get_id(self):
 
#         # returns id of the respective thread
#         if hasattr(self, '_thread_id'):
#             return self._thread_id
#         for id, thread in threading._active.items():
#             if thread is self:
#                 return id
  
#     def raise_exception(self):
#         thread_id = self.get_id()
#         res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
#               ctypes.py_object(SystemExit))
#mqtt interaction
def task(time):
    global speed
    speed, i = 0, 0
    while (time > i):
        i = i + speed
        t.sleep(1)
    return
def on_connect(client, userdata, flags, rc):
    global flag_player
    global flag_opponent
    print("Connection returned result: "+str(rc))
    
# Subscribing in on_connect() means that if we lose the connection and
# reconnect then subscriptions will be renewed.
# client.subscribe("ece180d/test")
# The callback of the client when it disconnects.
    txt = '0'
    while(flag_player == 0):
        r = sr.Recognizer()
        print("Which player are you playing as, 1 or 2?")
        with sr.Microphone(device_index=1) as source:
            audio = r.listen(source,phrase_time_limit = 2)
        try:
            txt = r.recognize_google(audio)
            txt = str(txt)
            print("You said " + txt)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        if txt.lower() == 'one' or txt.lower() == 'won' or txt.lower() == '1':
            flag_player = 1
            flag_opponent = 2
        elif txt.lower() == 'two' or txt.lower() == 'to' or txt.lower() == 'too' or txt.lower() == '2':
            flag_player = 2
            flag_opponent = 1
    client.subscribe(str(flag_player)+'Team8', qos=1)
    #subscribing to mqtt to receive IMU data
    #messages must only be received once hence qos is 2
    client.subscribe(str(flag_player)+'Team8A',qos=2)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')
def on_message(client, userdata, message):
    global flag_received
    global in_cooking
    global speed
    global message_received
    global spins
    global chops
    
    temporary = str(message.payload)
    message_received = temporary[4:-2]
    flag_received = temporary[2:3]
    #score flag received
    if (str(flag_received) == str(FLAG_STOVE) and position == STOVE):
        speed = int(message_received)
    elif (str(flag_received) == str(FLAG_CUTTING) and position == CUTTING):
        speed = int(message_received)
    elif str(flag_received) == str(FLAG_SCORE):
        if in_cooking == 2:
            if 1000-float(score) > 1000-float(message_received):
                print('You are better than the other idiot sandwich. Congration.')
                print('Your score: '+str(float(score))+'\n'+"Your opponent's score: " + str(float(message_received)))
            else:
                print('You lost. Try a little harder next time would ya?')
                print('Your score: '+str(float(score))+'\n'+"Your opponent's score: " + str(float(message_received)))
            client.loop_stop()
            client.disconnect()
    elif flag_received == str(MESSAGE):
        print(str(message_received))
def on_press(key):
    #global variables declared
    global position
    global in_cooking
    global spins
    global key_prev
    global chops
    global start
    global end
    global diff
    global prev_pos
    
    #choose which board
    if in_cooking == 0:
        if key == keyboard.Key.left and prev_pos == CUTTING:
            position = STOVE
            prev_pos = STOVE
            return False
        elif key == keyboard.Key.right and prev_pos == STOVE:
            position = CUTTING
            prev_pos = CUTTING
            return False
        else:
            position = 0
        print('press left to go to stove, right to go to chopping board')
 
    #given cooking = 1, stove
    elif position == STOVE:
        if key == keyboard.Key.up:
            key_prev = keyboard.Key.up
            start = t.time()
            return False
        elif key == keyboard.Key.right:
            if key_prev == keyboard.Key.up:
                key_prev = keyboard.Key.right
                return False
            else:
                print('wrong key')
        elif key == keyboard.Key.down:
            if key_prev == keyboard.Key.right:
                key_prev = keyboard.Key.down
                return False
            else:
                print('wrong key')
        elif key == keyboard.Key.left:
            if key_prev == keyboard.Key.down:
                key_prev = keyboard.Key.left
                end = t.time()
                diff = end-start
                #timing of spins
                if diff < IDEAL_SPIN * 1.1 and diff > IDEAL_SPIN * 0.9:
                    spins = spins + 1.5
                    print("Good job! Perfect Spin!                              ")
                elif diff < IDEAL_SPIN * 1.2 and diff > IDEAL_SPIN * 0.8:
                    spins = spins + 1
                    print("Okay job! Great Spin!                                ")
                elif diff < IDEAL_SPIN * 2 and diff > IDEAL_SPIN * 0.5:
                    spins = spins + 0.2
                    print("That was not a great spin, try to equalize your pace!")
                else:
                    print("You're an idiot sandwich. Try again.                 ")
                print(spins)
                return False
            else:
                print("wrong key                                                ")
                return False

    #given cooking = 1, cutting      
    elif position ==  CUTTING:
        if key == keyboard.Key.up:
            key_prev = keyboard.Key.up
            start = t.time()
            return False
        elif key == keyboard.Key.down:
            if key_prev == keyboard.Key.up:
                key_prev = keyboard.Key.down
                end = t.time()
                diff = end-start
                #timing of cut
                if diff < IDEAL_CUT * 1.1 and diff > IDEAL_CUT * 0.9:
                    chops = chops + 1.5
                    print("Good job! Perfect Cut!                              ")
                elif diff < IDEAL_CUT * 1.2 and diff > IDEAL_CUT * 0.8:
                    chops = chops + 1
                    print("Okay job! Great Cut!                                ")
                elif diff < IDEAL_CUT * 2 and diff > IDEAL_CUT * 0.5:
                    chops = chops + 0.2
                    print("That was not a great cut, try to equalize your pace!")
                else:
                    print("You're an idiot sandwich. Try again.                ")
                print(chops)
                return False
            else:
                print("wrong key                                               ")
                return False
        else:
            print("wrong key                                                   ")
            return False
#
#GAME STARTS HERE
#GAME STARTS HERE
#GAME STARTS HERE
#
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
##CONST GLOBALS
def main():
    global score
    global in_cooking
    global prev_pos
    #wait for player selection
    while(flag_player==0):
        pass
    t.sleep(1)
    print('Welcome to Cooking Papa!')
    #publish again in case of second to enter lobby
    r = sr.Recognizer()
    print('Say Practice to practice and Fight to play against an opponent')
    txt = '0'
    while txt.lower() != 'practice' or txt.lower() != 'fight':
        with sr.Microphone(device_index=1) as source:
            audio = r.listen(source,phrase_time_limit = 2)
        try:
            txt = r.recognize_google(audio)
            txt = str(txt)
            print("You said " + txt)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
    if txt.lower() == 'practice':
        flag_received = 99
    elif txt.lower() == 'fight':
        flag_received = 0
        client.publish(str(flag_opponent)+'Team8',str(FLAG_START)+'gamestart',qos=1)
    while(flag_received==0):
        pass
    client.publish(str(flag_opponent)+'Team8', str(FLAG_START)+'gamestart',qos=1)
    t.sleep(2)
    r = sr.Recognizer()
    txt = '0'
    print("Say Ready to begin")
    while txt.lower() != 'ready':
        with sr.Microphone(device_index=1) as source:
            audio = r.listen(source,phrase_time_limit = 2)
        try:
            txt = r.recognize_google(audio)
            txt = str(txt)
            print("You said " + txt)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
    print("Let's Begin, Timer starts in...")
    print("3")
    t.sleep(1)
    print("2")
    t.sleep(1)
    print("1")
    t.sleep(1)
    print("GO!")
    start_game = t.time()    
    while(in_cooking != 2):
        print('Press left to go to stove, Press right to go to chopping board')
        print('You must first spin, then chop')
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
        in_cooking = 1
        if position == STOVE:
            #ask IMU for stove classifier data
            r = sr.Recognizer()
            print("Say spoon to start stirring")
            txt = '0'
            while txt.lower() != 'spoon':
                with sr.Microphone(device_index=1) as source:
                    audio = r.listen(source,phrase_time_limit = 2)
                try:
                    txt = r.recognize_google(audio)
                    txt = str(txt)
                    print("You said " + txt)
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
            client.publish(str(flag_player)+'Team8B', str(FLAG_STOVE), qos=1)
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the stove', qos = 1)
            task(GOAL_STOVE)
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        elif position == CUTTING:
            #ask IMU for cutting classifier data
            r = sr.Recognizer()
            print("Say knife to start stirring")
            txt = '0'
            while txt.lower() != 'knife':
                with sr.Microphone(device_index=1) as source:
                    audio = r.listen(source,phrase_time_limit = 2)
                try:
                    txt = r.recognize_google(audio)
                    txt = str(txt)
                    print("You said " + txt)
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
            client.publish(str(flag_player)+'Team8B', str(FLAG_CUTTING), qos=1)
            client.publish(str(flag_opponent)+'Team8',str(MESSAGE) + 'Your opponent is at the stove', qos = 1)
            task(GOAL_CUTTING)
            client.publish(str(flag_player)+'Team8B', str(STOP), qos=1)
        in_cooking = 0
        if total_cutting >= GOAL_CUTTING and total_stove >= GOAL_STOVE:
            in_cooking = 2
    #ending conditions for the game
    end_game = t.time()
    score = end_game-start_game
    print('Your time was: ' + str(score))
    client.publish(str(flag_opponent)+'Team8', str(FLAG_SCORE)+str(score), qos=1)
    print("waiting for opponent's time...")
    while True:
        pass
main()
