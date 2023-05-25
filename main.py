
# Open the configuration file
with open("config.txt", "r") as file:
    # Read the contents of the file
    file_contents = file.read()

# Split the file contents by lines
lines = file_contents.split("\n")

# Initialize variables
id = None
appKey = None

# Iterate over the lines
for line in lines:
    line = line.strip()
    # Split each line by ':' to separate the key and value
    key_value = line.split(":")
    key = key_value[0]
    value = key_value[1]
    # Remove any leading/trailing whitespace from the key and value
    key = key.strip()
    value = value.strip()

    # Check the key and assign the value accordingly
    if key == "id":
        id = int(value)
    elif key == "appKey":
        appKey = value
    # elif key == "DR":
    #     DR = value
    # elif key == "channels":
    #     channels = value
DR = '6'
# Print the id and appKey
print("id:", id)
print("appKey:", appKey)
print("dr:", DR)
# print("channels:", channels)
 
        
app_key = appKey

####### settings
# Regional LoRaWAN settings. You may need to modify these depending on your region.
# If you are using AU915: Australia
band = 'AU915'
channels = '65' # different: 8,9,10,11
# DR = '0' # different: 2,3,4,5
out_file = "dataChannelDR.csv"
# If you are using US915
# band='US915'
# channels='8-15'
# 
# If you are using EU868
# band='EU868'
# channels='0-2'
######## end settings
from machine import UART, Pin
from sys import exit
from utime import sleep_ms
# allow the voltage to be stable
sleep_ms(5000)


uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
join_EUI = None   # These are populated by this script
device_EUI = None

### Function Definitions

def receive_uart():
    '''Polls the uart until all data is dequeued'''
    rxData=bytes()
    while uart1.any()>0:
        rxData += uart1.read(1)
        sleep_ms(2)
    return rxData.decode('utf-8')

def send_AT(command):
    '''Wraps the "command" string with AT+ and \r\n'''
    buffer = 'AT' + command + '\r\n'
    uart1.write(buffer)
    sleep_ms(300)

def test_uart_connection():
    '''Checks for good UART connection by querying the LoRa-E5 module with a test command'''
    send_AT('') # empty at command will query status
    data = receive_uart()
    if data == '+AT: OK\r\n' : print('LoRa radio is ready\n')
    else:
        print('LoRa-E5 detected\n')
        exit()

def get_eui_from_radio():
    '''Reads both the DeviceEUI and JoinEUI from the device'''
    send_AT('+ID=DevEui')
    data = receive_uart()
    device_EUI = data.split()[2]

    send_AT('+ID=AppEui')
    data = receive_uart()
    join_EUI = data.split()[2]

    print(f'JoinEUI: {join_EUI}\n DevEUI: {device_EUI}')
    
def set_app_key(app_key):
    if app_key is None:
        print('\nGenerate an AppKey on cloud.thethings.network and enter it at the top of this script to proceed')
        exit()

    send_AT('+KEY=APPKEY,"' + app_key + '"')
    receive_uart()
    print(f' AppKey: {app_key}\n')


def configure_regional_settings(band=None, DR='0', channels=None):
    ''' Configure band and channel settings'''
    
    send_AT('+DR=' + band)
    send_AT('+DR=' + DR)
    send_AT('+CH=NUM,' + channels)
    send_AT('+MODE=LWOTAA')
    receive_uart() # flush
    
    send_AT('+DR')
    data = receive_uart()
    print(data)


def join_the_things_network():
    '''Connect to The Things Network. Exit on failure'''
    send_AT('+JOIN')
    data = receive_uart()
    print(data)

    status = 'not connected'
    while status == 'not connected':
        data = receive_uart()
        if len(data) > 0: print(data)
        if 'joined' in data.split():
            status = 'connected'
        if 'failed' in data.split():
            print('Join Failed')
            exit()
        
        sleep_ms(1000)
        
def send_message(message):
    '''Send a string message'''
    send_AT('+MSG="' + message + '"')

    done = False
    while not done:
        data = receive_uart()
        if 'Done' in data or 'ERROR' in data:
            done = True
        if len(data) > 0: print(data)
        sleep_ms(1000)
        
def send_hex(message):
    send_AT('+MSGHEX="' + message + '"')

    done = False
    while not done:
        data = receive_uart()
        if 'Done' in data or 'ERROR' in data:
            done = True
        if len(data) > 0: print(data)
        sleep_ms(1000)



##########################################################
#        
# The main program starts here
#
##########################################################

test_uart_connection()

get_eui_from_radio()

set_app_key(app_key)

configure_regional_settings(band=band, DR=DR, channels=channels)

join_the_things_network()

import time

# Send example data
print("sending test messages")
# file = open(out_file, "w")


for i in range(0,6):
  for ch in range(8,16):
    count = 0
    res = []
    while count < 1:
    # send_AT('+DR='+band)
        start = time.time()
        send_AT('+DR='+str(i))
        send_AT('+CH=NUM,'+str(ch))
        # send_AT('+CH=NUM')
        send_message(str(count))
        res.append(time.time()-start)
        # print("send",count)
        # file.write(str(count)+"\n")
        # file.flush()
        count+=1
    print("channels: "+str(ch) + ","+ "DR: "+str(i)+" # of msg:",len(res),", avg msg time:",sum(res)/len(res))


