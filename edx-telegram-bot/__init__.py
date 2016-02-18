import os
import sys
import subprocess
from decorators import singleton

# class run(object):
#     def __init__(self):
#         print "++"*88
#         p = subprocess.Popen([sys.executable,"%s/edx_telegram_bot.py" % os.path.dirname(os.path.realpath(__file__))],
#                                   stdout=subprocess.PIPE,
#                                  stderr=subprocess.STDOUT)
#         print p.__dict__
#
# run()

#
# class ProcessManager(object):
#
#     __PROCESS = None
#
#     @staticmethod
#     def set_process(args):
#         print "++"*88
#         print getattr(ProcessManager.__PROCESS)
#
#         # Sets singleton process
#         if ProcessManager.__PROCESS is None:
#             p = subprocess.Popen(args)
#             ProcessManager.__PROCESS = p;
#         # else: exception handling
#
#     @staticmethod
#     def kill_process():
#
#         # Kills process
#         if ProcessManager.__PROCESS is None:
#             # exception handling
#             print "process hasn't found"
#         else:
#             ProcessManager.__PROCESS.kill()
#
# ProcessManager.set_process([sys.executable,"%s/edx_telegram_bot.py" % os.path.dirname(os.path.realpath(__file__))])
