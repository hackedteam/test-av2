__author__ = 'zeno'
import os

def test_vm_agent_shell():
    os.system("python ../AVAgent/av_agent.py -m test_vm -p test -f tests_integration/av_agent.procedures.yaml")