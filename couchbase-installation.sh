#!/bin/sh

export CB_USER=Administrator
export CB_PASSWORD=password
export CBIMAGE="couchbase:4.6.0"
export CB_AUTH="--user $CB_USER --password $CB_PASSWORD --cluster-name ClusterA --cluster 127.0.0.1:8091"
export CB_CLI="docker exec couchbase -t couchbase-cli"
export HN=`hostname`

#export CLI=docker exec couchbase couchbase-cli
export CLI=/opt/couchbase/bin/couchbase-cli


#regular installation
if [[ ! -f ${CLI} ]]
then
    echo "==========================="
    echo "Installingcouchbase server .."
    echo "==========================="

    curl -O http://packages.couchbase.com/releases/couchbase-release/couchbase-release-1.0-5-x86_64.rpm
    sudo rpm -ivh couchbase-release-1.0-5-x86_64.rpm
    sudo yum install couchbase-server-4.6.*
    sudo rm -rf /etc/yum.repos.d/couchbase-Base.repo
fi


#start couchbase server
echo "==========================="
echo "Rebooting couchbase server .."
echo "==========================="
sudo service couchbase-server stop
sleep 15
ps -ef | grep couchbase
sudo sh -c 'rm -rvf /opt/couchbase/var/lib/couchbase/*'
sudo service couchbase-server start

#docker kill couchbase && docker rm couchbase
#docker run --restart=always -m700M -d --name couchbase -h $HN -p 8091-8094:8091-8094 -p 11210:11210 $CBIMAGE
#echo "==========================="

echo Waiting COUCHBASE to start
until $(curl --output /dev/null --silent --head --fail http://127.0.0.1:8091); do
    printf '.'
    sleep 5
done
sleep 5

#configure cluster settings
echo "==========================="
echo "Configuration .."
echo "==========================="

echo :: Cluster Node ::
${CLI} \
  node-init                       \
  --node-init-hostname=$HN \
  --user Administrator       \
  --password password        \
  --cluster 127.0.0.1:8091   \
  --wait

${CLI} \
  cluster-init              \
  --user Administrator      \
  --password password       \
  --cluster-name ClusterA   \
  --cluster 127.0.0.1:8091  \
  --cluster-ramsize          400 \
  --cluster-index-ramsize    300 \
  --cluster-fts-ramsize      300 \
  --services data

${CLI} \
  setting-cluster           \
  --user Administrator      \
  --password password       \
  --cluster-name ClusterA   \
  --cluster 127.0.0.1:8091  \
  --cluster-username Administrator \
  --cluster-password password \
  --wait

echo :: Bucket ::
${CLI} \
  bucket-create \
  --user Administrator      \
  --password password       \
  --cluster-name ClusterA   \
  --cluster 127.0.0.1:8091  \
  --bucket BUC1             \
  --bucket-type=couchbase   \
  --bucket-ramsize=200      \
  --bucket-replica=1        \
  --bucket-priority=high     \
  --bucket-eviction-policy=fullEviction \
  --enable-flush=1 \
  --wait

${CLI} \
  bucket-create \
  --user Administrator      \
  --password password       \
  --cluster-name ClusterA   \
  --cluster 127.0.0.1:8091  \
  --bucket BUC2             \
  --bucket-type=couchbase   \
  --bucket-ramsize=200      \
  --bucket-replica=1        \
  --bucket-priority=high     \
  --bucket-eviction-policy=fullEviction \
  --enable-flush=1 \
  --wait

#done
echo "==========================="
echo Done
echo "==========================="
