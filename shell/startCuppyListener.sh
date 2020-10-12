cd /home/pi

NBR_RUNNING=`ps -ef |grep cuppyListen|wc -l`

if [ $NBR_RUNNING -lt 2 ]; then
	nohup python /home/pi/projects/cuppy/cuppyRPi/cuppyListen.py -e alzow1um5gjqs.iot.us-east-1.amazonaws.com -r /home/pi/projects/IoTCerts/root-CA.crt -c /home/pi/projects/IoTCerts/cuppyRPi.cert.pem -k /home/pi/projects/IoTCerts/cuppyRPi.private.key &
fi

