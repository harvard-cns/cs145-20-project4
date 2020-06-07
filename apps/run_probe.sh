#! /bin/bash

~/mininet/util/m h1 python apps/receive.py > report/qlen.txt &

sleep 1

for s in {2..16}
do
    ~/mininet/util/m h$s python apps/send.py 10.0.0.1 1000 &
done

trap stop INT

function stop() {
    pids=$(ps -aux | grep "python apps" | awk '{ print $2 }')
    for pid in $pids
    do
        kill -9 $pid
    done
    exit
}

sleep 1024

