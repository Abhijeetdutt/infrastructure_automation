#!/usr/bin/env python

__author__ = 'abhijeet pandey'

from subprocess import Popen,PIPE
from os import path
from sys import exit
from datetime import datetime
from time import sleep
from json import load
from kazoo.client import KazooClient
from socket import gethostname as get_current_host_name
from argparse import ArgumentParser as get_args

class ProcCheck:

        def __init__(self,process_name, monitor_interval, start_command):
                self.process_name = process_name
                self.monitor_interval = monitor_interval
                self.start_command = start_command

        def get_process_id(self):
                cmd_to_check_process = "ps -ef | grep " + self.process_name.replace('.','\.') + " |                                                                                                           grep -v grep"
                print(cmd_to_check_process)
                proc = Popen(cmd_to_check_process, stdout=PIPE, stderr=PIPE, shell=True)
                (out, err) = proc.communicate()
                rc = proc.wait()
                if rc == 0 and out and not err:
                        return out.strip().split()[1]
                else:
                        return None

        def start_process(self):
                cmd_to_start_process = self.start_command
                proc = Popen(cmd_to_start_process, stdout=PIPE, stderr=PIPE, shell=True)
                (out, err) = proc.communicate()
                if out and not err:
                        return True
                else:
                        return False

        def monitor(self, proc_id):
                if proc_id:
                        while path.isdir('/proc/{}'.format(proc_id)):
                                sleep(self.monitor_interval)
                        print("process {} with pid {} went down at : {}".format(self.process_name, p                                                                                                          roc_id, str(datetime.now().strftime("%c"))))
                else:
                        print("process {} not running.".format(self.process_name))


class SetHA():

        def __init__(self, process_info, zookeeper_quorum):
                self.process_info = process_info
                self.process_name = process_info['process_name']
                self.monitor_interval = process_info['monitor_interval']
                self.start_command = process_info['start_command']
                self.zookeeper_quorum = zookeeper_quorum

        def create_lock(self):
                zk = KazooClient(hosts=self.zookeeper_quorum)
                zk.start()
                with zk.Lock("/",get_current_host_name()):
                        proc_object = ProcCheck(self.process_name, self.monitor_interval, self.start                                                                                                          _command)
                        proc_id = proc_object.get_process_id()
                        if proc_id is None:
                                proc_status = proc_object.start_process()
                                if proc_status:
                                        proc_id = proc_object.get_process_id()

                        # shall proc_status be False, proc_id will return None again,
                        # which will be handled by ProcCheck.monitor()

                        # as soon as monitor finishes, it will release lock,
                        # allowing the service running on another machine to create lock.
                        proc_object.monitor(proc_id)


if __name__ == '__main__':


        parser = get_args(description='pass the json with process info')
        parser.add_argument('--paramfile', metavar='paramfile', required=True,
                help='paramfile : test.json')
        args = parser.parse_args()
        param_file = str(args.paramfile)

        try:
                with open(param_file) as f:
                        data = load(f)
                process_info = data['process']
                zookeeper_quorum = data['zookeeper']['zookeeper_quorum'] + data['zookeeper']['znode'                                                                                                          ]

        except KeyError as ke:
                exit("[Errno 2] KeyError: {} in {}".format(ke,param_file))

        except Exception as e:
                exit(e)

        begin = SetHA(process_info, zookeeper_quorum)
        begin.create_lock()
