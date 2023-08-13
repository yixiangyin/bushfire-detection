from sx1262 import SX1262
import time
import machine
rtc = machine.RTC()
time.sleep(2)

filename = "receiver_output.txt"

def append(name, s):
    f = open(name, "a")
    f.write(s)
    f.close()
sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

def print_sent(msg, timestamp):
  print(str(timestamp), "sent:", msg)
def print_recv(msg, err, timestamp):
  print(str(timestamp), "recv:", msg, "with error code", err)

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
# def free_resource(device_id):

# LoRa
sx.begin(freq=915, bw=125.0, sf=7, cr=5, syncWord=0x12,
  power=-5, currentLimit=60.0, preambleLength=8,
  implicit=False, implicitLen=0xFF,
  crcOn=True, txIq=False, rxIq=False,
  tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

# mac
# tdma:number_of_ED,slot_time(s)
tdma_bcast_msg = "tdma"
tdma=False
number_of_ED = 1
set_of_ED = set()
# number_of_ED = set()
# list of id in tdma
set_of_ED_in_tdma = set()
# available channel
available_channel = {str(i) for i in range(10)}
# map from ED ID to occupied channel
id_to_channel = {} # its size will be the number of tdma ED in the network
# mac end
append(filename, "\n")
# f = open(filename)
while True:
    try:
      # blocking
      msg, err = sx.recv()
      error = SX1262.STATUS[err]
      print_recv(msg, error, rtc.datetime()[4:7])
      append_received(filename, msg, error, str(rtc.datetime()[4:7]))
      # print("finish recv")
      if len(msg) > 0 and err == 0:
        msg = msg.decode("utf-8")
        msg = msg.split(" ")
        device_id = msg[0]
        device_msg = msg[1]
        set_of_ED.add(device_id) # keep track of all the number of EDs
        # fire alarm
        if (int(device_msg) == 2):
          # turn into tdma
          p = available_channel.pop()
          # tdma,id,time(seconds),schedule
          send_msg = [tdma_bcast_msg, device_id, str(rtc.datetime()[6]), p]
          send_msg = ",".join(send_msg)
          # turn to tdma now!
          sx.send(bytes(send_msg, "utf-8"))
          append_sent(filename, send_msg, rtc.datetime()[4:7])
          print_sent(send_msg, rtc.datetime()[4:7])
          # print("sent", send_msg)
          # record which ED has been turned to tdma and which channel each ED has
          set_of_ED_in_tdma.add(device_id)
          id_to_channel[device_id] = p
          # print("sent tdma command")
          
          while len(set_of_ED_in_tdma)<len(set_of_ED):
            # send control msg to other ED to turn to tdma
            msg, err = sx.recv()
            error = SX1262.STATUS[err]
            append_received(filename, msg, error, str(rtc.datetime()[4:7]))
            print_recv(msg, error, rtc.datetime()[4:7])
            if len(msg) > 0 and err == 0:
              msg = msg.decode("utf-8")
              msg = msg.split(" ")
              device_id = msg[0]
              device_msg = msg[1]
              set_of_ED.add(device_id)
              if (device_id not in set_of_ED_in_tdma):
                p = available_channel.pop()
                # tdma,id,time(seconds),schedule
                send_msg = [tdma_bcast_msg, device_id, str(rtc.datetime()[6]), p]
                send_msg = ",".join(send_msg)
                # turn to tdma now!
                sx.send(bytes(send_msg, "utf-8"))
                append_sent(filename, send_msg, rtc.datetime()[4:7])
                print_sent(send_msg, rtc.datetime()[4:7])
                # print("sent", send_msg)
                # record which ED has been turned to tdma and which channel each ED has
                set_of_ED_in_tdma.add(device_id)
                id_to_channel[device_id] = p 
          print("informed all EDs to turn to tdma mode")
        if (int(device_msg)==5):
          # turn into normal mode
          # some ED has requested to change back
          send_msg = ["normal", device_id]
          send_msg = ",".join(send_msg)
          sx.send(bytes(send_msg, "utf-8"))
          print_sent(send_msg, rtc.datetime()[4:7])
          append_sent(filename, send_msg, rtc.datetime()[4:7])
          # free the resources
          available_channel.add(id_to_channel[device_id])
          # print("free resources", id_to_channel[msg[0]])
          id_to_channel.pop(device_id)
          set_of_ED_in_tdma.remove(device_id)
          # append_sent(filename, send_msg, rtc.datetime()[4:7])
          while len(set_of_ED_in_tdma)>0:
            # send control msg to other ED to turn to normal
            msg, err = sx.recv()
            error = SX1262.STATUS[err]
            append_received(filename, msg, error, str(rtc.datetime()[4:7]))
            print_recv(msg, error, rtc.datetime()[4:7])
            if len(msg) > 0 and err == 0:
              msg = msg.decode("utf-8")
              msg = msg.split(" ")
              device_id = msg[0]
              device_msg = msg[1]
              set_of_ED.add(device_id)
              if (device_id in set_of_ED_in_tdma):
                send_msg = ["normal", device_id]
                send_msg = ",".join(send_msg)
                sx.send(bytes(send_msg, "utf-8"))
                append_sent(filename, send_msg, rtc.datetime()[4:7])
                print_sent(send_msg, rtc.datetime()[4:7])
                # free the resources
                available_channel.add(id_to_channel[device_id])
                # print("free resources", id_to_channel[msg[0]])
                id_to_channel.pop(device_id)
                set_of_ED_in_tdma.remove(device_id)
          print("informed all EDs to turn to normal mode")
    except Exception as e:
      append(filename, "Error occured: "+str(e))
      print(f"Error occurred: {e}")
    # append(filename, )
    # append(filename, msg+ "," + error + "\n")
    # o = str(rtc.datetime()[4:7]) + ",send ack to "+msg[0]+"\n"
    # append(filename, o)
    # print(o)


