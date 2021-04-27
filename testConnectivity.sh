#!/bin/ksh

unset IFS
for e in $(cat environment.lst | grep cwl | grep '^cmwl.*1@')
do
        scp dat.lst $e:~/ >/dev/null
        echo "validation connectivity from $e"
        ssh $e "unset IFS
for i in \$(cat dat.lst);
do
IFS=:
eval 'array=(\$i)'
ip_addr=\${array[0]}
port=\${array[1]}
echo exit | telnet \$ip_addr \$port
done"
done
