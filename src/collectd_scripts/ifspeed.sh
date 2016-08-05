#!/bin/bash
HOSTNAME="${COLLECTD_HOSTNAME:-`hostname -f`}"
INTERVAL="${COLLECTD_INTERVAL:-600}"
re='^[0-9]+$'
ESC_HOSTNAME=`echo $HOSTNAME | tr . _`
sigma_numerator=0.00
sigma_denominator=0.00
for INT_LIST in `ls /sys/class/net | sort | uniq`
do
 speed=`sudo ethtool $INT_LIST | grep Speed | sed 's/^.*Speed: \([0-9]\+\).*$/\1/'`

 if [[ $speed =~ $re ]] ; then
  table_name=$HOSTNAME/interface-$INT_LIST/if_octets
  rx_tx="rx"
  uSocMsg=`echo "GETVAL $table_name"|sudo socat - UNIX-CLIENT:/var/run/collectd-unixsock`
  rxtx=`echo $uSocMsg|echo ${uSocMsg/*$rx_tx/$rx_tx}`
  values=( $rxtx )

  rxs=(${values[0]//=/ })
  rx=`echo ${rxs[1]}`
  rx=`printf "%f" $rx`

  txs=(${values[1]//=/ })
  tx=`echo ${txs[1]}`
  tx=`printf "%f" $tx`

  ifSpeed=`echo $speed*1000000|bc -l`

  numerator=`echo $rx+$tx|bc -l`
  numerator=`echo $numerator*8*100 |bc -l`
  sigma_numerator=`echo $sigma_numerator+$numerator|bc -l`

  sigma_denominator=`echo $sigma_denominator+$ifSpeed|bc -l`

  val=`echo $numerator/$ifSpeed|bc -l`
  val=`printf "%f" $val`

  time="$(date +%s)"
  table_name=$ESC_HOSTNAME/interface-$INT_LIST/percent-utilization
  echo "PUTVAL $table_name interval=$INTERVAL $time:$val"
 fi
done

time="$(date +%s)"
val=0
if (( $(echo "$sigma_denominator > 0" |bc -l) )); then
  val=`echo $sigma_numerator/$sigma_denominator|bc -l`
fi

if (( $(echo "$sigma_denominator > 0" |bc -l) )); then
  table_name=$HOSTNAME/interface-average/percent-network_utilization
  echo "PUTVAL $table_name interval=$INTERVAL $time:$val"
fi

table_name=$HOSTNAME/interface-average/bytes-total_bandwidth
sigma_denominator=`echo $sigma_denominator/8|bc -l`
echo "PUTVAL $table_name interval=$INTERVAL $time:$sigma_denominator"

table_name=$HOSTNAME/interface-average/bytes-total_bandwidth_used
sigma_numerator=`echo $sigma_numerator/8|bc -l`
sigma_numerator=`echo $sigma_numerator/100|bc -l`
echo "PUTVAL $table_name interval=$INTERVAL $time:$sigma_numerator"
