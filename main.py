# local main.py on each end device 

app_key = '4867A28A1DD189110D1A60B05D438AEC'

# Regional LoRaWAN settings. You may need to modify these depending on your region.
# If you are using AU915: Australia
band='AU915'
channels='8-15'

# If you are using US915
# band='US915'
# channels='8-15'
# 
# If you are using EU868
# band='EU868'
# channels='0-2'




from machine import UART, Pin
from utime import sleep_ms
# allow the voltage to be stable
sleep_ms(5000)

from sys import exit

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

configure_regional_settings(band=band, DR='0', channels=channels)

join_the_things_network()


# Send example data
print("sending test messages")
while True:
    send_message("Hello World!")
