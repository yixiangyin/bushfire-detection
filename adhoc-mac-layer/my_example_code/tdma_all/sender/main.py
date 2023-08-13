from sx1262 import SX1262
import machine
import random
import time

rtc = machine.RTC()
time.sleep(4)
file = open("config.txt", "r")
ID = file.read(1) # assume one digit ID
file.close()
counter = 1
filename = ID+"_sender_output.txt"
random.seed(int(ID))
# seconds is [-2] set to 0
t = [1000, 1, 1, 1, 1, 0,0,0]

# randomizeing the start time
# time.sleep(2*random.random())
def append(name, s):
  f = open(name, "a")
  f.write(s)
  f.close()

def append_received(name, msg, err, timestamp):
  """
  timestamp is a string
  """
  f = open(name, "a")
  f.write("receive,")
  f.write(str(timestamp))
  f.write(",")
  if (len(msg)>0):
    f.write(msg)
  else:
    f.write("empty!!!")
  f.write(",")
  f.write(err)
  f.write("\n")
  f.close()
def append_sent(name, msg, timestamp):
  """
  timestamp is a string
  """
  f = open(name, "a")
  f.write("send,")
  f.write(str(timestamp))
  f.write(",")
  f.write(msg)
  f.write("\n")
  f.close()
def print_sent(msg, timestamp):
  print(str(timestamp), "sent:", msg)
def print_recv(msg, err, timestamp):
  print(str(timestamp), "recv:", msg, "with error code", err)



sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

# LoRa
sx.begin(freq=915, bw=125.0, sf=7, cr=5, syncWord=0x12,
  power=-5, currentLimit=60.0, preambleLength=8,
  implicit=False, implicitLen=0xFF,
  crcOn=True, txIq=False, rxIq=False,
  tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

# mac control 
delay_interval = 2 # in seconds
# delay_min = 9.96 
# delay_variant = delay_interval-delay_min # in seconds
timeout_for_tdma = 1000 # 100ms won't work
# 0 -> normal, 1 -> tdma
mode = 0
# 0 means send every 10 seconds
# schedule info
number_of_ED = 10
slot_time = 1 # seconds
schedule = None # not defined 

# setting for Random access protocol
delay_interval = 4 # in seconds
delay_min = 2
delay_variant = delay_interval-delay_min # in seconds
# mac control end
counter = 1
while True:
    if mode==0:
      # normal mode: send every 2 seconds
      while True:
        # avoid sending too fast
        delay = delay_min + random.random() * delay_variant
        time.sleep(delay)
        string = ID+" "+str(counter)
        # print(str(rtc.datetime()),"sent", string)
        print_sent(string, rtc.datetime()[4:7])
        append_sent(filename, string, str(rtc.datetime()[4:7]))
        sx.send(bytes(string, 'utf-8'))
        msg, err = sx.recv(0, True, timeout_for_tdma)
        # print("received", msg)
        error = SX1262.STATUS[err]
        print_recv(msg, error, rtc.datetime()[4:7])
        
        append_received(filename, msg, error, rtc.datetime()[4:7])
        if len(msg) > 0 and err==0:
          msg = msg.decode("utf-8") 
          msg = msg.split(",")
          if msg[0] == "tdma" and msg[1]==ID:
            mode = 1
            print("change to tdma")
            # sync time
            t[-2] = int(msg[2])
            rtc.datetime(tuple(t))
            # update schedule
            schedule = int(msg[3])
            # number_of_ED=int(msg[2])
            # print(rtc.datetime())
            counter+=1
            break
        counter+=1
    if mode==1:
      while mode==1:
        # avoid sending too fast
        time.sleep(slot_time)
        string = ID+" "+str(counter)
        while True:
          cur_second = int(rtc.datetime()[6])
          # print("%:", cur_second%number_of_ED, cur_second, number_of_ED)
          if (cur_second%number_of_ED==schedule): 
            # print(str(rtc.datetime()),"sent", string)
            print_sent(string, rtc.datetime()[4:7])
            append_sent(filename, string, str(rtc.datetime()[4:7]))
            sx.send(bytes(string, "utf-8"))
            msg, err = sx.recv(0, True, timeout_for_tdma)
            error = SX1262.STATUS[err]
            print_recv(msg, error, rtc.datetime()[4:7])
            append_received(filename, msg, error, str(rtc.datetime()[4:7]))
            if err==0 and len(msg) > 0:
              msg = msg.decode("utf-8") 
              msg = msg.split(",")
              if msg[0] == "normal":
                mode = 0
                print(str(rtc.datetime()),"change to normal mode")
            break
          time.sleep(slot_time)
        counter+=1
