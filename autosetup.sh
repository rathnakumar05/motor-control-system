sudo cp /home/pi/motor-control-system/mcs.service /lib/systemd/system/mcs.service

sudo systemctl enable mcs.service

sudo systemctl start mcs.service
