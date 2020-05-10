from xml.etree import ElementTree as ET
from enum import Enum
from os.path import exists, abspath, expanduser, join, dirname, realpath
from sys import platform
import os

class VariableLabel:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
        self.methods = []

    def getMethod(self, searchFor):
        if type(searchFor) == str:
            for method in self.methods:
                if method.name == searchFor:
                    return method
        elif type(searchFor) == int:
            for method in self.methods:
                if method.id == searchFor:
                    return method

class MscXmlInfo:
    def __init__(self, filename=None):
        self.globals = []
        self.functions = []
        self.syscalls = []
        if filename != None:
            self.read(filename)

    def read(self, filename):
        labels = ET.parse(filename).getroot()
        for function in labels.find("functions").findall("function"):
            self.functions.append(VariableLabel(
                    int(function.get("id"), 0),
                    function.get("name")
                ))
        for globalNode in labels.find("globals").findall("global"):
            self.globals.append(VariableLabel(
                    int(globalNode.get("id"), 0),
                    globalNode.get("name")
                ))
        for syscall in labels.find("syscalls").findall("syscall"):
            syscallLabel = VariableLabel(
                        int(syscall.get("id"), 0),
                        syscall.get("name")
                    )
            if syscall.find("methods") != None:
                for method in syscall.find("methods").findall("method"):
                    syscallLabel.methods.append(VariableLabel(
                        int(method.get("id"), 0),
                        method.get("name")
                    ))
            self.syscalls.append(syscallLabel)

    def getFunc(self, searchFor):
        if type(searchFor) == str:
            for function in self.functions:
                if function.name == searchFor:
                    return function
        elif type(searchFor) == int:
            for function in self.functions:
                if function.id == searchFor:
                    return function

    def getSyscall(self, searchFor):
        if type(searchFor) == str:
            for syscall in self.syscalls:
                if syscall.name == searchFor:
                    return syscall
        elif type(searchFor) == int:
            for syscall in self.syscalls:
                if syscall.id == searchFor:
                    return syscall

    def getGlobal(self, searchFor):
        if type(searchFor) == str:
            for globalVar in self.globals:
                if globalVar.name == searchFor:
                    return globalVar
        elif type(searchFor) == int:
            for globalVar in self.globals:
                if globalVar.id == searchFor:
                    return globalVar

def getXmlInfoPath():
    # If the user in on a unix system, use $HOME/.mscinfo if it exists
    if platform in ['linux', 'darwin']:
        if exists(abspath(expanduser('~/.mscinfo'))):
            return abspath(expanduser('~/.mscinfo'))
    elif platform.startswith('win'):
        path = join(os.getenv('LOCALAPPDATA'), 'mscinfo.xml')
        if exists(path):
            return path
    __location__ = realpath(join(os.getcwd(), dirname(__file__)))
    path = join(__location__, "mscinfo.xml")
    if exists(path):
        return path
