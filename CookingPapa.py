from email import message
from pynput import keyboard
import time as t 
import paho.mqtt.client as mqtt
import threading
import ctypes
##CONST GLOBALS

GOAL_STOVE = 1
GOAL_CUTTING = 1
MESSAGE = 10
IDEAL_SPIN = 1
IDEAL_CUT = 1

#BOARD POSITIONS
CUTTING = 1
STOVE = -1
#BOARD POSITIONS

##CONST GLOBALS

#globals
position = 0
in_cooking = 0
spins = 0
chops = 0
key_prev = keyboard.Key.up
start = t.time()
end = t.time()
diff = end - start
total_stove = 0
total_cutting = 0
flag_player = 0
flag_opponent = 0
flag_received = 0
flag_score = 3
score = 0
message_received = ''

#globals

class thread_with_exception(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
             
    def run(self):
 
        # target function of the thread class
        try:
            i = 0
            while(True):
                i = i+1
                t.sleep(1)
                print("                           "+str(i), end="\r")
        finally:
            print('ended')
          
    def get_id(self):
 
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
#mqtt interaction
def on_connect(client, userdata, flags, rc):
    global flag_player
    global flag_opponent
    print("Connection returned result: "+str(rc))
    
# Subscribing in on_connect() means that if we lose the connection and
# reconnect then subscriptions will be renewed.
# client.subscribe("ece180d/test")
# The callback of the client when it disconnects.
    while(flag_player == 0):
        player = input("which player are you playing as, 1 or 2?")
        if str(player) == '1':
            flag_player = 1
            flag_opponent = 2
        elif str(player) == '2':
            flag_player = 2
            flag_opponent = 1
    client.subscribe(str(player)+'Team8', qos=1)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')

def on_message(client, userdata, message):
    global flag_received
    global in_cooking
    global score
    global message_received

    temporary = str(message.payload)
    message_received = temporary[3:-2]
    flag_received = temporary[2]
    #score flag received
    if str(flag_received) == '3':
        if in_cooking == 2:
            client.publish(str(flag_opponent)+'Team8', float(score), qos=1)
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
    
    #choose which board
    if in_cooking == 0:
        if key == keyboard.Key.left:
            position = STOVE
            return False
        elif key == keyboard.Key.right:
            position = CUTTING
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
def main():
    global score
    global in_cooking
    global spins
    global chops
    global total_cutting
    global total_stove
    #wait for player selection
    while(flag_player==0):
        pass
    t.sleep(1)
    client.publish(str(flag_opponent)+'Team8','1gamestart',qos=1)
    print('Welcome to Cooking Papa! Waiting for your opponent to enter the lobby')
    #publish again in case of second to enter lobby
    while(flag_received==0):
        pass
    client.publish(str(flag_opponent)+'Team8','1gamestart',qos=1)
    t.sleep(2)
    txt = input('Type Ready to begin: \n')
    while txt.lower() != 'ready':
        txt = input('Type Ready to begin: \n')
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
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
        in_cooking = 1
        if position == STOVE:
            txt = input('Type spoon to start stirring: \n')
            if txt == 'spoon':
                t2 = thread_with_exception('timer')
                t2.start()
                print('Press up right down left chef')
                while(spins<4):
                    with keyboard.Listener(on_press=on_press)as listener:
                        listener.join()
                spins = 0
                total_stove = total_stove + 1
                print("Total stove times remaining: "+ str(GOAL_STOVE-total_stove))
                t2.raise_exception()
                t2.join()
        elif position == CUTTING:
            txt = input('Type knife to start chopping: \n')
            if txt == 'knife':
                t2 = thread_with_exception('timer')
                t2.start()
                print('Press up and down chef')
                while(chops<6):
                    with keyboard.Listener(on_press=on_press)as listener:
                        listener.join()
                chops = 0
                total_cutting = total_cutting + 1
                print("Total cutting times remaining: "+ str(GOAL_CUTTING-total_cutting))
                t2.raise_exception()
                t2.join()
        in_cooking = 0
        if total_cutting >= GOAL_CUTTING and total_stove >= GOAL_STOVE:
            in_cooking = 2
    #ending conditions for the game
    end_game = t.time()
    score = end_game-start_game
    print('Your time was: ' + str(score))
    client.publish(str(flag_opponent)+'Team8', str(flag_score)+str(score), qos=1)
    print("waiting for opponent's time...")
    while True:
        pass
main()
