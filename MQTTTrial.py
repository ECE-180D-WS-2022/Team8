import time as t 
import paho.mqtt.client as mqtt
current_message = '0'
gamestart = '1'
def on_connect(client, userdata, flags, rc):
    print("Connection returned result: "+str(rc))
    gamestart = str(rc)
    client.subscribe('1Team8TrackB',qos=2)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected Disconnect')
    else:
        print('Expected Disconnect')

def on_message(client, userdata, message):
    global current_message
    current_message = str(message.payload)

    
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
while(1):
    print(current_message)