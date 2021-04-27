#!/usr/bin/python

class Solution :

        def __init__(self,action,param_file,server_name):
                global info
                with open(param_file,"r") as f :
                        info=json.load(f)

                global jvm_dict
                jvm_dict = {}
                for sn in server_name :
                        if sn in info :
                                jvm_dict[sn] = info[sn]
                        else :
                                sys.exit('[ ' + ctime(time()) + ' ] ' + ' No data available for : '  + sn + ' in ' + param_file)
                print('[ ' + ctime(time()) + ' ] ' + action + ' execution started...')

        def curr_status(self,jvmdata):
                cmd='ssh ' + jvm_dict[jvmdata][2]  + ' ". ./.profile>/dev/null; cd ' + jvm_dict[jvmdata][9] + '; ./' + jvm_dict[jvmdata][10] + '" 2>/dev/null'
                process = subprocess.Popen(cmd.strip(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (result, error) = process.communicate()
                rc = process.wait()
                if result == 'UP' and rc != 0:
                        print ('[ ' + ctime(time()) + ' ] ' + ' Error: failed to execute command: ', cmd)
                        print ('[ ' + ctime(time()) + ' ] ' + error.strip())
                return result.strip()

        def ping_jvm(self,jvmdata):
                current_status=self.curr_status(jvmdata)
                print('[ ' + ctime(time()) + ' ] ' + jvmdata + ' ping status ' + current_status)

        def stop_jvm(self,jvmdata):
                current_status=self.curr_status(jvmdata)
                if current_status == 'DOWN' :
                        print('[ ' + ctime(time()) + ' ] ' + jvmdata + ' already down.')
                elif current_status == 'UP' :
                        print('[ ' + ctime(time()) + ' ] ' + 'stopping ' + jvmdata + '.')
                        cmd='OPSYS_OprunScript1 ' + jvm_dict[jvmdata][5] + ' ' + jvm_dict[jvmdata][6] + ' ' + jvm_dict[jvmdata][11] + ' ' + jvm_dict[jvmdata][                           12]
                        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        (result, error) = process.communicate()
                        rc = process.wait()
                        if rc != 0:
                                print ('[ ' + ctime(time()) + ' ] ' + ' Error: failed to execute command: ', cmd)
                                print ('[ ' + ctime(time()) + ' ] ' + error.strip())

                        if self.curr_status(jvmdata) == 'DOWN' :
                                print('[ ' + ctime(time()) + ' ] ' + jvmdata + ' is successfully brought down')
                        else :
                                print('[ ' + ctime(time()) + ' ] ' + jvmdata + ' failed while bringing up')
                else :
                        print('[ ' + ctime(time()) + ' ] ' + jvmdata + ' is in unknown state, check with administrator')

        def start_jvm(self,jvmdata):
                current_status=self.curr_status(jvmdata)
                if current_status == 'UP' :
                        print('[ ' + ctime(time()) + ' ] ' + jvmdata + ' is already up.')
                elif current_status == 'DOWN' :
                        print('[ ' + ctime(time()) + ' ] ' + 'starting ' + jvmdata + '.')
                        cmd='OPSYS_OprunScript1 ' + jvm_dict[jvmdata][7] + ' ' + jvm_dict[jvmdata][8] + ' ' + jvm_dict[jvmdata][11] + ' ' + jvm_dict[jvmdata][                           12]
                        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        (result, error) = process.communicate()
                        rc = process.wait()
                        if rc != 0:
                                print ('[ ' + ctime(time()) + ' ] ' + ' Error: failed to execute command: ', cmd)
                                print ('[ ' + ctime(time()) + ' ] ' + error.strip())

                        if self.curr_status(jvmdata) == 'UP' :
                                print('[ ' + ctime(time()) + ' ] ' + jvmdata + ' is successfully brought up')
                        else :
                                print('[ ' + ctime(time()) + ' ] ' + jvmdata + ' failed while bringing up')
                else :
                        print('[ ' + ctime(time()) + ' ] ' + jvmdata + ' is in unknown state, check with administrator')


        def printme(self,jvmdata):
                data = {"servername" : jvmdata,
                        "region" : jvm_dict[jvmdata][0],
                        "type" : jvm_dict[jvmdata][1],
                        "machine" : jvm_dict[jvmdata][2],
                        "url" : jvm_dict[jvmdata][3],
                        "stop_job" : jvm_dict[jvmdata][4],
                        "stop_job_rec" : jvm_dict[jvmdata][5],
                        "start_job" : jvm_dict[jvmdata][6],
                        "start_job_rec" : jvm_dict[jvmdata][7],
                        "script_path" : jvm_dict[jvmdata][8],
                        "ping_script" : jvm_dict[jvmdata][9] }

                print(data)

        def execute(self,func_name,func_args):

                pool = ThreadPool()
                results = pool.map(func_name, func_args)
                pool.close()
                pool.join()

if __name__ == '__main__' :

        import subprocess,sys,os
        from time import time, ctime
        from multiprocessing import Process, current_process, Lock, Manager
        from multiprocessing.dummy import Pool as ThreadPool
        import json,argparse

        parser = argparse.ArgumentParser(description='pass the parameter file name')
        parser.add_argument('--paramfile', metavar='paramfile', required=True,
                        help='paramfile : cm.json | rpl.json | info.json')
        parser.add_argument('--servername',  metavar='servername', required=True,
                        help='servername : CM11-Server | CM11-Server,CM12-Server,CM13-Server')
        parser.add_argument('--action',  metavar='action', required=True,
                        help='action : stop | start | restart | ping')
        parser.add_argument('--parallel', metavar='parallel', required=True,
                        help='parallel : yes | no')

        args = parser.parse_args()

        param_file = str(args.paramfile)
        server_name = list(map(str,str(args.servername).split(',')))
        parallel = str(args.parallel)
        action = str(args.action)

        solution = Solution(action,param_file,server_name)

        if action == 'stop' :
                if parallel == 'yes' :
                        solution.execute(solution.stop_jvm,jvm_dict.keys())
                elif parallel == 'no' :
                        for sn in server_name :
                                if sn in info :
                                        solution.stop_jvm(sn)

        elif action == 'start' :
                if parallel == 'yes' :
                        solution.execute(solution.start_jvm,jvm_dict.keys())
                elif parallel == 'no' :
                        for sn in server_name :
                                if sn in info :
                                        solution.start_jvm(sn)

        elif action == 'restart' :
                if parallel == 'yes' :
                        solution.execute(solution.stop_jvm,jvm_dict.keys())
                        solution.execute(solution.start_jvm,jvm_dict.keys())
                elif parallel == 'no' :
                        for sn in server_name :
                                if sn in info :
                                        solution.stop_jvm(sn)
                                        solution.start_jvm(sn)
        elif action == 'ping' :
                if parallel == 'yes' :
                        solution.execute(solution.ping_jvm,jvm_dict.keys())
                elif parallel == 'no' :
                        for sn in server_name :
                                if sn in info :
                                        solution.ping_jvm(sn)
        else :
                sys.exit('[ ' + ctime(time()) + ' ] ' + ' invalid action.')
