
from machine import UART, Pin
from utime import sleep_ms
LED = machine.Pin(25, machine.Pin.OUT)

while (True):
    LED.toggle()
    print("Hello World!")
    sleep_ms(500)
    