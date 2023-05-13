# Bushfire detection
This is the repository containing all my resources(code+notes) for my honours project: Bushfire detection with Lora.



## firmware setup
It seems that if the micro-python firmware is not installed properly on pico, we can't connect to the pico on Thonny. To install it, just find the firmware [here for pico](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html), and drag it into pico. In order for pico to appear as a storage device, you have to hold the `bootsel` button while you are plugging in the usb.





## todo
- [ ] develop a script to analyse the json file
- [ ] develop a script to deploy the scripts automatically
- [ ] try to understand what the channel and sf does the device actually use by inspecting the packets, and see how it maps to the regional parameteres.


## idea
- if we can store the appKey on each pico, then we just set the main.py script to read from the file, then the script can be same for all devices, we just need to change the config file inside each of the pico.


## experiment

config:
I run the code for 1 minute on one node. The code and the data is in this [commit](https://github.com/yixiangyin/bushfire-detection/commit/95666583a58986bcf019089b41eddd16a7bb65fb). 
