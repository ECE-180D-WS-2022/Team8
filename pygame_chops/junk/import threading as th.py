#threading https://stackoverflow.com/questions/13180941/how-to-kill-a-while-loop-with-a-keystroke


import threading as th
import time
import keyboard

speed=1
keep_going = True
def key_capture_thread():
    global speed
    global keep_going
    a = keyboard.read_key()
    if a== "1":
        speed=1
    if a== "2":
        speed=2
    if a== "3":
        speed=3
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()



def do_stuff():
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    i=0
    while keep_going:
        print('still going...')
        time.sleep(speed/3)
        i=i+1
        print (speed)
    print ("Schleife beendet")

do_stuff()


