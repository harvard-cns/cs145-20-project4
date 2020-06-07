#! /bin/bash

for s in {2..16}
do
    ~/mininet/util/m h$s ./apps/traffic-gen/bin/tg-server -p 5050 > ./apps/traffic-gen/log/server_$p.log &
done

sleep 5

~/mininet/util/m h1 ./apps/traffic-gen/bin/tg-client -c ./apps/traffic-gen/exampleConfig1
