#!/bin/bash

name=$1
port=$2
while true
do
	conn=`netstat -an|grep -i established|grep $port|wc -l`
	echo "the connections is : $conn"
	pid=`ps -ef|grep $name|grep -v grep|awk '{print $2}'`

	while [ $conn -eq 0 ]
	do
		conn=`netstat -an|grep -i established|grep $port|wc -l`
		sleep 0.1
	done	

	cpu_idle=`top -b -n 3|grep Cpu|tail -1 |awk '{print $8}'`
	echo $cpu_idle
	
	if [ $((conn%1000)) -lt 200 ]
	then
		uptime
		vmstat
		pmap -d $pid|tail -1

		rx=`cat /sys/class/net/eno1/statistics/rx_bytes`
		rxp=`cat /sys/class/net/eno1/statistics/rx_packets`
		tx=`cat /sys/class/net/eno1/statistics/tx_bytes`
		txp=`cat /sys/class/net/eno1/statistics/tx_packets`
		sleep 1
		rx2=`cat /sys/class/net/eno1/statistics/rx_bytes`
		rxp2=`cat /sys/class/net/eno1/statistics/rx_packets`
		tx2=`cat /sys/class/net/eno1/statistics/tx_bytes`
		txp2=`cat /sys/class/net/eno1/statistics/tx_packets`

		tbps=`expr $tx2 - $tx`
		tpps=`expr $txp2 - $txp`
		rbps=`expr $rx2 - $rx`
		rpps=`expr $rxp2 - $rxp`

		tkps=`expr $tbps  / 1024`
		rkps=`expr $rbps  / 1024`
		echo "upload speed eno1 is : $tkps kb/s; download speed eno1 is $rkps kb/s"
		echo -e "upload speed eno1 is : $tpps packets/s; download speed eno1 is $rpps packets/s\n\n"
	fi

done	
