#threading https://stackoverflow.com/questions/13180941/how-to-kill-a-while-loop-with-a-keystroke


import threading as th
import time
import keyboard

speed=1
keep_going = True
status = 'fast'
def key_capture_thread():
    global speed
    global status
    global keep_going
    a = keyboard.read_key()
    if a== "1":
        speed=1
        status='fast'
    if a== "2":
        speed=2
        status='medium'
    if a== "3":
        speed=3
        status='slow'
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()



def do_stuff():
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    i=0
    global status
    global speed
    while keep_going:
        print('still going ' + status + '... ')
        time.sleep(speed/3)
        i=i+1
        print (speed)
    print ("exit")

do_stuff()


