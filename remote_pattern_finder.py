class Solution :

        def init__(self) :
                self.currPath  = os.getcwd()

        def fetch_detail(self,login) :

                if "linux" not in platform :
                        print("Only works for Linux machines")
                else :
                        command = 'ssh ' + login + ' " if [[ -n \$(ls ' + dictionary[login][1] + ' 2>/dev/null) ]]; then zgrep \\\"' + dictionary[login][0] + '\\\" ' + dictionary[login][1] + ' | sed \\\"s/^/\$(whoami)@\$(hostname) /g\\\"; fi"'
                        if dictionary[login][2] :
                                print(" [[ DEBUG ]] " + str(command))
                        result = subprocess.check_output(command,shell=True).strip()
                        if result : print(result)


if __name__ == '__main__' :

        import subprocess
        import datetime
        import time
        import sys,os
        from multiprocessing import Process, current_process, Lock, Manager
        from multiprocessing.dummy import Pool as ThreadPool
        import json
        from sys import platform
        import argparse
        from datetime import datetime

        parser = argparse.ArgumentParser(description='pass the parameters - pattern/file_path/environment-sheet')
        parser.add_argument('--env_file', metavar='env_file', required=True,
                        help='env_file : environment_file.txt')
        parser.add_argument('--pattern', metavar='pattern', required=True,
                        help='pattern : "2020-07-28.*Bad"')
        parser.add_argument('--file_path', metavar='file_path', required=True,
                        help='file_path : "2020-07-28.*Bad"')
        parser.add_argument('--debug', metavar='debug',
                        help='debug : "True"')

        args = parser.parse_args()

        envfile = str(args.env_file)
        pattern = str(args.pattern)
        filepath = str(args.file_path)
        debug = False
        if args.debug :
                debug = str(args.debug)

        global dictionary
        dictionary={}

        with open(envfile,'r') as f :
                for login in f :
                        dictionary[login.strip()] = (pattern,filepath,debug)

        solution = Solution()

        print("Executing the program for : " + str(envfile) + "\n")
        print("Start Time =", datetime.now().strftime("%H:%M:%S"))
        print("\nData found : \n")
        pool = ThreadPool(50)
        results = pool.map(solution.fetch_detail, dictionary.keys())
        pool.close()
        pool.join()
        print("\n")
        print("End Time =", datetime.now().strftime("%H:%M:%S"))
        print("\n")
