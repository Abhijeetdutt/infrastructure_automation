#!/usr/local/bin/python

'''
        Developed by @Abhijeet Pandey
        @ 14 April 2019

        Purpose - Returns Status For Turbo Charging Daemons
'''

import sys
import os
import thread
import cx_Oracle;
import threading
import subprocess
import datetime
import time
from multiprocessing import Process, current_process, Lock, Manager

timenow = datetime.datetime.now();
time_format = timenow.strftime("%Y/%m/%d %H:%M:%S")

process_information = {
        "" : " " )
        }

'''
        Help :
'''

if not len(sys.argv) > 1 :
        for key in process_information :
                print ("\t" + str(key))

        sys.exit()

site = sys.argv[1]
process_2_check = sys.argv[2]

site_information = {
        "TBS" : ("PROP_FILE","DB_CONN_STR"),
        }

def initialize():

        global user
        user = list()
        global host
        host = list()
        global process
        process = list()
        global status_process
        global active_process
        active_process = list()
        global results
        results = list()
        global status_process_splitted
        global final_up
        final_up = list()
        global final_up_time
        final_up_time = list()
        global final_up_runs_on
        final_up_runs_on = list()
        global final_up_status
        final_up_status = list()
        global final_down
        final_down = list()
        global final_down_time
        final_down_time = list()
        global final_down_runs_on
        final_down_runs_on = list()
        global final_down_status
        final_down_status = list()

        for line in open(site_information[site][0]):
                if line.startswith(process_2_check) > 0 :
                        line_output=line.split(',')
                        process.append(line_output[0].strip())
                        host.append(line_output[1].strip())
                        user.append(line_output[2].strip())

def print_process( l, elements ):
        data = {"username" : user[elements],
                "hostname" : host[elements],
                "pre_commands" : "\"[[ \$(ps -ef | grep '"+ str(process_information[process_2_check][0]) + str(process[elements]) + str(process_information[process_2_check][1]) +"'| grep -v grep | wc -l) == \"1\" ]] && print " + str(process[elements]) + ",UP,\$(ps -ef | grep '"+ str(process_information[process_2_check][0]) + str(process[elements]) + str(process_information[process_2_check][1]) +"'| grep -v grep | awk '{print \$5}'),\$(whoami)@\$(hostname)|| print " + str(process[elements]) + ",DOWN,NA,\$(whoami)@\$(hostname)\"",
                "post_commands" : "print \"" + str(process[elements]) + ",DOWN,NA," + user[elements] + "@" + host[elements] + "\""
                }

        command = "ssh {username}@{hostname} {pre_commands} 2>/dev/null || {post_commands}"

        try:
                status_process=subprocess.check_output(command.format(**data),shell=True)
        except  subprocess.CalledProcessError as e:
                status_process=str(process[elements]) + ",DOWN,NA," + str(data["username"]) + "@" + str(data["hostname"]);

        l.acquire()
        try:
                final_status.append(status_process)
        finally:
                l.release()


def check_db():

        connection = cx_Oracle.connect(site_information[site][1]) ;
        cursor = connection.cursor();
        querystring=("select distinct ")
        cursor.execute(querystring)
        for result in cursor:
                active_process.append(str(result[0]).strip())
        cursor.close()
        connection.close()

        active_process.sort()

def insert_db(query_string):

        connection = cx_Oracle.connect('') ;
        cursor = connection.cursor();
        sql = "insert into ... values (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany("""
                        insert into tc_monitoring values (:1, :2, :3, :4, :5, :6, :7, sysdate)""" ,query_string)
        connection.commit()
        cursor.close()
        connection.close()

if __name__ == '__main__' :
        with Manager() as manager:
                initialize()
                lock = Lock()

                final_status = manager.list()

                processes = []
                for elements in range(0,len(process)):
                        process_id = Process(target=print_process, args=(lock,elements))
                        processes.append(process_id)
                        process_id.start()

                for proc in processes:
                        proc.join()

                check_db()

                datestr="(TO_DATE('" + time_format + "','yyyy/mm/dd hh24:mi:ss'))"

                for final_elements in range(0,len(process)):
                        if final_status[final_elements].split(',')[1].strip() == "UP" :
                                final_up.append(final_status[final_elements].split(',')[0].strip())
                                final_up_status.append(final_status[final_elements].split(',')[1].strip())
                                final_up_time.append(final_status[final_elements].split(',')[2].strip())
                                final_up_runs_on.append(final_status[final_elements].split(',')[3].strip())

                        if final_status[final_elements].split(',')[1].strip() == "DOWN" :
                                final_down.append(final_status[final_elements].split(',')[0].strip())
                                final_down_status.append(final_status[final_elements].split(',')[1].strip())
                                final_down_time.append(final_status[final_elements].split(',')[2].strip())
                                final_down_runs_on.append(final_status[final_elements].split(',')[3].strip())

                        # START YOUR CODE HERE. MR. ABHIJEET
        for final_elements in range(0,len(process)):
                output = []
                for instance in range(0,len(process)):
                        if final_up.count(process[instance]) > 0 :
                                index_of=final_up.index(process[instance])
                                if active_process.count(process[instance][-4:]) > 0 :
                                        output.append(['',str(process[instance]),str(final_up_runs_on[index_of]),str(process_information[process_2_check][2]),str(final_up_time[index_of]),str(final_up_status[index_of]),'ACTIVE'])
                                else :
                                        output.append(['',str(process[instance]),str(final_up_runs_on[index_of]),str(process_information[process_2_check][2]),str(final_up_time[index_of]),str(final_up_status[index_of]),'SHADOW'])
                        else :
                                index_of=final_down.index(process[instance])
                                output.append(['TBS',str(process[instance]),str(final_down_runs_on[index_of]),str(process_information[process_2_check][2]),str(final_down_time[index_of]),str(final_down_status[index_of]),'null'])


        ha_information = {
                "BUNDLE" : "1",
                "AGENT" : "1",
                "ONE_UP_ONE_ACTIVE" : "2",
                "MANY_UP_MANY_ACTIVE" : "1",
                "MONITORED_ONLY" : "1",
                "PROXY_SERVER" : "2"
        }

        #       EXCEPTION - QUORUM

        if process_2_check == "QUORUM" or process_2_check == "AVM" :
                multiplicity = 1

        #print("final_up : " + str(len(final_up)))
        #print(multiplicity)
        #print("total : " + str(len(process)))

        verify_status= float(len(final_up))*int(multiplicity) / len(process)

        #print(verify_status)

        if verify_status == 1.0 :
                summary = "ALL_UP"
        else :
                if verify_status == 0.0 :
                        summary = "ALL_DOWN"
                else :
                        summary = "PARTIALLY_UP"

        result = str(len(final_up)) + "/" +  str(len(process))

        output.append(['TBS',str(process_2_check),str(result),str(process_information[process_2_check][2]),'SUMMARY',str(summary),'null'])

        insert_db(output)
