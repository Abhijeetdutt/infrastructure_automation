#!/bin/ksh

sleep 10 &
pid[0]=$!

trap "kill ${pid[0]} ; exit 1" INT
wait
