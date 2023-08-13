# for each of port
# connect using rshell and upload the code to main.py

#!/bin/bash

# List all USB communication ports
ports=$(ls /dev/tty.usbmodem1* 2>/dev/null)

# Check if there are any ports available
if [ -z "$ports" ]; then
    echo "No USB communication ports found."
        exit
        fi
        # Iterate through each port and upload the code to Pico using rshell
for port in $ports; do
  echo "Connecting to $port with rshell..."

  if [ "$port" = "/dev/tty.usbmodem1421201" ]; then
    rshell -p "$port" <<EOF
    cp ../receiver/main.py /pyboard/
    rm /pyboard/*output*
EOF
  else
    rshell -p "$port" <<EOF
    cp ./main.py /pyboard/
    rm /pyboard/*output*
EOF
  fi

done


