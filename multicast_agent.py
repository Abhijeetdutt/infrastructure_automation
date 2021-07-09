import socket
import sys
import requests
import json
import os
import ConfigParser
import logging

'''
Data common for requests urls
'''

def pushData():

        config = ConfigParser.RawConfigParser()
        config.read("./config.ini")

        osUser = config.get('AGENT_DATA','osUser')
        weblogicUrl = config.get('AGENT_DATA','weblogicUrl')
        jolokiaUrl = config.get('AGENT_DATA','jolokiaUrl')
        instanceName = config.get('AGENT_DATA','instanceName')

        LOG_LEVEL = "logging." + str(config.get('AGENT_DATA','debugLevel'))
        LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = "./monitoring.log",
                                level = logging.INFO,
                                format = LOG_FORMAT,
                                filemode = 'w')
        monLogger = logging.getLogger()

        '''
        Get URLs
        '''

        statusUrl = weblogicUrl + '/awsi_uams/services/UAMSLoginService?wsdl'
        osUrl = jolokiaUrl + '/jolokia/read/java.lang:type=OperatingSystem'
        heapUrl = jolokiaUrl + '/jolokia/read/java.lang:type=Memory/HeapMemoryUsage'
        threadUrl = jolokiaUrl + '/jolokia/read/com.bea:ServerRuntime=' + instanceName + ',Name=ThreadPoolRuntime,Type=ThreadPoolRuntime/HoggingThreadCount,PendingUserRequestCount,StuckThreadCount,CompletedRequestCount,ExecuteThreadTotalCount,ExecuteThreadIdleCount,StandbyThreadCount,Throughput'
        gcUrl = jolokiaUrl + '/jolokia/read/java.lang:name=*,type=GarbageCollector'
#       applicationUrl = jolokiaUrl + '/jolokia/read/com.bea:Type=ApplicationRuntime,*'

        '''
        Fetch Response
        '''

        status = "RUNNING" if "wsdlsoap:address" in requests.get(statusUrl).content else "DOWN"
        osInfo = requests.get(osUrl)
        heap = requests.get(heapUrl)
        threads = requests.get(threadUrl)
        gc = requests.get(gcUrl)
#       application = requests.get(applicationUrl)

        '''
        Manipulate Data
        '''

        heapPct = heap.json()['value']['used'] * 100 / heap.json()['value']['max']
        dateStr = str(os.popen("date -d \"$(ps -eo user,lstart,args | grep " + osUser + " | grep weblogic.Server | grep -v grep | awk '{ for(i=2;i<=6;i++) print $i}')\" \"+%Y/%m/%d %H:%M:%S\"").read().strip('\n')) if status == "RUNNING" else "NA"

        '''
        Status & Uptime
        '''

        monLogger.info("Status & uptime is pushed in database")
        print(" STATUS                    : " + status)
        monLogger.debug(" STATUS                    : " + status)
        print(" RUNNING SINCE             : " + str(dateStr))
        monLogger.debug(" RUNNING SINCE             : " + str(dateStr))

        '''
        OS Data
        '''

        monLogger.info("OS data is pushed in database")
        print(" PROCESS CPU LOAD          : " + str(osInfo.json()['value']['ProcessCpuLoad']))
        monLogger.debug(" PROCESS CPU LOAD          : " + str(osInfo.json()['value']['ProcessCpuLoad']))
        print(" SYSTEM LOAD AVERAGE       : " + str(osInfo.json()['value']['SystemLoadAverage']))
        monLogger.debug(" SYSTEM LOAD AVERAGE       : " + str(osInfo.json()['value']['SystemLoadAverage']))
        print(" SYSTEM CPU LOAD           : " + str(osInfo.json()['value']['SystemCpuLoad']))
        monLogger.debug(" SYSTEM CPU LOAD           : " + str(osInfo.json()['value']['SystemCpuLoad']))
        print(" HEAP %                    : " + str(heapPct))
        monLogger.debug(" HEAP %                    : " + str(heapPct))

        '''
        [[ NOT WORKING ]] Garbage collection

        monLogger.info("Garbage collection data is pushed to database")
        print(" GC COLLECTION TIME        : " + str(gc.json()['value']['java.lang:name=G1 Young Generation,type=GarbageCollector']['LastGcInfo']['CollectionTime']))
        monLogger.debug(" GC COLLECTION TIME        : " + str(gc.json()['value']['CollectionTime']))
        print(" GC COLLECTION COUNT       : " + str(gc.json()['value']['CollectionCount']))
        monLogger.debug(" GC COLLECTION COUNT       : " + str(gc.json()['value']['CollectionCount']))
        '''

        '''
        Thread Pool Runtime Data
        '''

        monLogger.info("ThreadPoolRuntime Data is pushed in database")
        print(" COMPLETED REQUEST COUNT   : " + str(threads.json()['value']['CompletedRequestCount']))
        monLogger.debug(" COMPLETED REQUEST COUNT   : " + str(threads.json()['value']['CompletedRequestCount']))
        print(" EXECUTING THREAD COUNT    : " + str(threads.json()['value']['ExecuteThreadTotalCount']))
        monLogger.debug(" EXECUTING THREAD COUNT    : " + str(threads.json()['value']['ExecuteThreadTotalCount']))
        print(" EXECUTE THREAD IDLE COUNT : " + str(threads.json()['value']['ExecuteThreadIdleCount']))
        monLogger.debug(" EXECUTE THREAD IDLE COUNT : " + str(threads.json()['value']['ExecuteThreadIdleCount']))
        print(" STUCK THREAD COUNT        : " + str(threads.json()['value']['StuckThreadCount']))
        monLogger.debug(" STUCK THREAD COUNT        : " + str(threads.json()['value']['StuckThreadCount']))
        print(" HOGGING THREAD COUNT      : " + str(threads.json()['value']['HoggingThreadCount']))
        monLogger.debug(" HOGGING THREAD COUNT      : " + str(threads.json()['value']['HoggingThreadCount']))
        print(" STANDBY THREAD COUNT      : " + str(threads.json()['value']['StandbyThreadCount']))
        monLogger.debug(" STANDBY THREAD COUNT      : " + str(threads.json()['value']['StandbyThreadCount']))
        print(" PENDING THREAD COUNT      : " + str(threads.json()['value']['PendingUserRequestCount']))
        monLogger.debug(" PENDING THREAD COUNT      : " + str(threads.json()['value']['PendingUserRequestCount']))
        print(" THROUGHPUT                : " + str(threads.json()['value']['Throughput']))
        monLogger.debug(" THROUGHPUT                : " + str(threads.json()['value']['Throughput']))

        '''
        Application Runtime Data jolokia/read/com.bea:Type=ApplicationRuntime,*
        print(" APPLICATION DATA : " + str(application.json()['value']['ApplicationName']))
        '''

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('tbscwl1', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.listen(1)
while True:
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()

        try:
                print >>sys.stderr, 'connection from', client_address
                while True:
                        data = connection.recv(16)
                        print >>sys.stderr, 'received "%s"' % data
                        if data:
                                print >>sys.stderr, 'sending acknowledgement'
                                connection.sendall("ACKNOWLEDGED")
                                pushData()
                        else:
                                print >>sys.stderr, 'no more data from', client_address
                                break

        finally:
                connection.close()
