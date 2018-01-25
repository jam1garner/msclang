#**************************************************************************#
# This file is part of pymsc which is released under MIT License. See file #
# LICENSE or go to https://github.com/jam1garner/pymsc/blob/master/LICENSE #
# for full license details.                                                #
#**************************************************************************#
from sys import version_info
isPython3 = version_info >= (3,)
assert isPython3 #If this fails switch to python 3
import struct, tempfile

MSC_MAGIC = b'\xB2\xAC\xBC\xBA\xE6\x90\x32\x01\xFD\x02\x00\x00\x00\x00\x00\x00'

COMMAND_IDS = {
    "nop"            : 0x0,
    "begin"          : 0x2,
    "end"            : 0x3,
    "jump"           : 0x4,
    "jump4"          : 0x4,
    "jump5"          : 0x5,
    "return_6"       : 0x6,
    "return_7"       : 0x7,
    "return_8"       : 0x8,
    "return_9"       : 0x9,
    "pushInt"        : 0xa,
    "pushVar"        : 0xb,
    "error_C"        : 0xc,
    "pushShort"      : 0xd,
    "addi"           : 0xe,
    "subi"           : 0xf,
    "multi"          : 0x10,
    "divi"           : 0x11,
    "modi"           : 0x12,
    "negi"           : 0x13,
    "i++"            : 0x14,
    "i--"            : 0x15,
    "bitAnd"         : 0x16,
    "bitOr"          : 0x17,
    "bitNot"         : 0x18,
    "bitXor"         : 0x19,
    "leftShift"      : 0x1a,
    "rightShift"     : 0x1b,
    "setVar"         : 0x1c,
    "i+="            : 0x1d,
    "i-="            : 0x1e,
    "i*="            : 0x1f,
    "i/="            : 0x20,
    "i%="            : 0x21,
    "i&="            : 0x22,
    "i|="            : 0x23,
    "i^="            : 0x24,
    "equals"         : 0x25,
    "notEquals"      : 0x26,
    "notEqual"       : 0x26,
    "lessThan"       : 0x27,
    "lessOrEqual"    : 0x28,
    "greater"        : 0x29,
    "greaterOrEqual" : 0x2a,
    "not"            : 0x2b,
    "printf"         : 0x2c,
    "sys"            : 0x2d,
    "try"            : 0x2e,
    "unk_2E"         : 0x2e,
    "callFunc"       : 0x2f,
    "callFunc2"      : 0x30,
    "callFunc3"      : 0x31,
    "push"           : 0x32,
    "pop"            : 0x33,
    "if"             : 0x34,
    "ifNot"          : 0x35,
    "else"           : 0x36,
    "error_37"       : 0x37,
    "intToFloat"     : 0x38,
    "floatToInt"     : 0x39,
    "addf"           : 0x3a,
    "subf"           : 0x3b,
    "multf"          : 0x3c,
    "divf"           : 0x3d,
    "negf"           : 0x3e,
    "f++"            : 0x3f,
    "f--"            : 0x40,
    "floatVarSet"    : 0x41,
    "float+="        : 0x42,
    "float-="        : 0x43,
    "float*="        : 0x44,
    "float/="        : 0x45,
    "floatEqual"          : 0x46,
    "floatNotEqual"       : 0x47,
    "floatLess"           : 0x48,
    "floatLessOrEqual"    : 0x49,
    "floatGreater"        : 0x4a,    
    "floatGreaterOrEqual" : 0x4b,
    "error_4c"       : 0x4c,
    "exit"           : 0x4d,
    "byte"           : 0xFFFE,
    "long"           : 0xFFFF
}

COMMAND_NAMES = {}
for k, v in COMMAND_IDS.items():
    if not v in COMMAND_NAMES:
        COMMAND_NAMES[v] = k
        
COMMAND_FORMAT = {
    0x0 : '',
    0x2 : 'HH',
    0x3 : '',
    0x4 : 'I',
    0x5 : 'I',
    0x6 : '',
    0x7 : '',
    0x8 : '',
    0x9 : '',
    0xa : 'I',
    0xb : 'BH',
    0xc : '',
    0xd : 'H',
    0xe : '',
    0xf : '',
    0x10 : '',
    0x11 : '',
    0x12 : '',
    0x13 : '',
    0x14 : 'BH',
    0x15 : 'BH',
    0x16 : '',
    0x17 : '',
    0x18 : '',
    0x19 : '',
    0x1a : '',
    0x1b : '',
    0x1c : 'BH',
    0x1d : 'BH',
    0x1e : 'BH',
    0x1f : 'BH',
    0x20 : 'BH',
    0x21 : 'BH',
    0x22 : 'BH',
    0x23 : 'BH',
    0x24 : 'BH',
    0x25 : '',
    0x26 : '',
    0x27 : '',
    0x28 : '',
    0x29 : '',
    0x2a : '',
    0x2b : '',
    0x2c : 'B',
    0x2d : 'BB',
    0x2e : 'I',
    0x2f : 'B',
    0x30 : 'B',
    0x31 : 'B',
    0x32 : '',
    0x33 : '',
    0x34 : 'I',
    0x35 : 'I',
    0x36 : 'I',
    0x38 : 'B',
    0x39 : 'B',
    0x3a : '',
    0x3b : '',
    0x3c : '',
    0x3d : '',
    0x3e : '',
    0x3f : 'BH',
    0x40 : 'BH',
    0x41 : 'BH',
    0x42 : 'BH',
    0x43 : 'BH',
    0x44 : 'BH',
    0x45 : 'BH',
    0x46 : '',
    0x47 : '',
    0x48 : '',
    0x49 : '',
    0x4a : '',
    0x4b : '',
    0x4c : '',
    0x4d : '',
    0xFFFE : 'B',
    0xFFFF : 'I'
}

COMMAND_STACKPOPS = {
    0x0 : lambda params: 0,
    0x2 : lambda params: 0,
    0x3 : lambda params: 0,
    0x4 : lambda params: 0,
    0x5 : lambda params: 0,
    0x6 : lambda params: 1,
    0x7 : lambda params: 0,
    0x8 : lambda params: 1,
    0x9 : lambda params: 0,
    0xa : lambda params: 0,
    0xb : lambda params: 0,
    0xc : lambda params: 0,
    0xd : lambda params: 0,
    0xe : lambda params: 2,
    0xf : lambda params: 2,
    0x10 : lambda params: 2,
    0x11 : lambda params: 2,
    0x12 : lambda params: 2,
    0x13 : lambda params: 1,
    0x14 : lambda params: 0,
    0x15 : lambda params: 0,
    0x16 : lambda params: 2,
    0x17 : lambda params: 2,
    0x18 : lambda params: 1,
    0x19 : lambda params: 2,
    0x1a : lambda params: 2,
    0x1b : lambda params: 2,
    0x1c : lambda params: 1,
    0x1d : lambda params: 1,
    0x1e : lambda params: 1,
    0x1f : lambda params: 1,
    0x20 : lambda params: 1,
    0x21 : lambda params: 1,
    0x22 : lambda params: 1,
    0x23 : lambda params: 1,
    0x24 : lambda params: 1,
    0x25 : lambda params: 2,
    0x26 : lambda params: 2,
    0x27 : lambda params: 2,
    0x28 : lambda params: 2,
    0x29 : lambda params: 2,
    0x2a : lambda params: 2,
    0x2b : lambda params: 1,
    0x2c : lambda params: params[0],
    0x2d : lambda params: params[0],
    0x2e : lambda params: 0,
    0x2f : lambda params: params[0] + 1,
    0x30 : lambda params: params[0] + 1,
    0x31 : lambda params: params[0] + 1,
    0x32 : lambda params: -1,
    0x33 : lambda params: 1,
    0x34 : lambda params: 1,
    0x35 : lambda params: 1,
    0x36 : lambda params: 0,
    0x37 : lambda params: 0,
    0x38 : lambda params: 0,
    0x39 : lambda params: 0,
    0x3a : lambda params: 2,
    0x3b : lambda params: 2,
    0x3c : lambda params: 2,
    0x3d : lambda params: 2,
    0x3e : lambda params: 1,
    0x3f : lambda params: 0,
    0x40 : lambda params: 0,
    0x41 : lambda params: 1,
    0x42 : lambda params: 1,
    0x43 : lambda params: 1,
    0x44 : lambda params: 1,
    0x45 : lambda params: 1,
    0x46 : lambda params: 2,
    0x47 : lambda params: 2,
    0x48 : lambda params: 2,
    0x49 : lambda params: 2,
    0x4a : lambda params: 2,
    0x4b : lambda params: 2,
    0x4c : lambda params: 0,
    0x4d : lambda params: 0,
    0xFFFE : lambda params: 0,
    0xFFFF : lambda params: 0
}

TYPE_SIZES = {
    'B' : 1,
    'H' : 2,
    'I' : 4
}

def getSizeFromFormat(formatString):
    s = 0
    for char in formatString:
        s += TYPE_SIZES[char]
    return s

def disassembleCommands(rawCommands, startOffset):
    pos = 0
    commands = []
    while pos < len(rawCommands):
        newCommand = Command()
        newCommand.read(rawCommands, pos)
        newCommand.commandPosition = startOffset + pos
        commands.append(newCommand)
        pos += (1 + newCommand.paramSize)
    return commands

#Thanks Triptych https://stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except
def _RepresentsInt(s):
    try:
        int(s, 0)
        return True
    except:
        return False

def _RepresentsFloat(s):
    try:
        float(s.rstrip('f'))
        return True
    except:
        return False

def parseCommands(text, refs={}, mscStrings=[]):
    lines = text.replace(', ',',').split('\n')
    lines = [line.strip() for line in lines if line.strip() != '']
    lines = [line.split('#')[0] for line in lines if line.split('#')[0] != '']
    splitCommands = [[split for split in line.split(' ') if split != ''] for line in lines]
    cmds = []
    labels = {}
    aliases = {}
    currentPos = 0
    for i,splitCommand in enumerate(splitCommands):
        cmd = Command()
        if splitCommand[0][-1] == ':':
            labels[splitCommand[0][0:-1]] = currentPos
        elif splitCommand[0] == '.alias':
            params = splitCommand[1].split(',')
            aliases[params[1]] = int(params[0], 0)
        else:
            if splitCommand[0][-1] == '.':
                cmd.pushBit = True
                splitCommand[0] = splitCommand[0][0:-1]
            cmd.command = COMMAND_IDS[splitCommand[0]]
            currentPos += getSizeFromFormat(COMMAND_FORMAT[cmd.command]) + 1
            if len(splitCommand) > 1 and not ((cmd.command == 0xA or cmd.command == 0xD) and splitCommand[1][0] == '"'):
                cmd.parameters = [param for param in splitCommand[1].split(',')]
            elif (cmd.command == 0xA or cmd.command == 0xD) and splitCommand[1][0] == '"':
                printString = splitCommand[1][1:]
                for s in splitCommand[2:]:
                    printString += " "+s
                if printString[-1] == '"':
                    printString = printString[:-1]
                cmd.parameters = [len(mscStrings)]
                mscStrings.append(printString)

            cmds.append(cmd)
    labelNames = labels.keys()
    aliasNames = aliases.keys()
    for cmd in cmds:
        for i in range(len(cmd.parameters)):
            if cmd.parameters[i] in labelNames:
                cmd.parameters[i] = labels[cmd.parameters[i]]
            elif cmd.parameters[i] in aliasNames:
                cmd.parameters[i] = aliases[cmd.parameters[i]]
            elif cmd.parameters[i] in refs:
                cmd.parameters[i] = refs[cmd.parameters[i]]
            elif _RepresentsInt(cmd.parameters[i]):
                cmd.parameters[i] = int(cmd.parameters[i], 0)
            elif _RepresentsFloat(cmd.parameters[i]):
                cmd.parameters[i] = struct.unpack('>L', struct.pack('>f', float(cmd.parameters[i].rstrip('f'))))[0]
    return cmds

class Command:
    def __init__(self, command=0, parameters=[], pushBit=False):
        self.command = command
        self.parameters = parameters
        self.pushBit = pushBit
        self.paramSize = 0
        self.commandPosition = 0
        self.debugString = None

    def __len__(self):
        return getSizeFromFormat(COMMAND_FORMAT[self.command]) + 1

    def read(self, byteBuffer, pos):
        self.command = int(byteBuffer[pos]) & 0x7F
        self.pushBit = (int(byteBuffer[pos]) & 0x80) != 0
        if self.command in COMMAND_NAMES:
            self.paramSize = getSizeFromFormat(COMMAND_FORMAT[self.command])
            self.parameters = list(struct.unpack('>'+COMMAND_FORMAT[self.command], byteBuffer[pos+1:pos+1+self.paramSize]))
        else:
            self.parameters = [self.command]
            self.command = 0xFFFE #unknown command, display as "byte X"

    def write(self, endian='>'):
        if self.command in [0xFFFE, 0xFFFF]:
            returnBytes = bytes()
        else:
            returnBytes = bytes([self.command | (0x80 if self.pushBit else 0x0)])
        for i,paramChar in enumerate(COMMAND_FORMAT[self.command]):
            returnBytes += struct.pack(endian+paramChar, self.parameters[i] & 0xffffffff)
        return returnBytes

    def strParams(self):
        params = ""
        for i in range(len(self.parameters)):
            if isinstance(self.parameters[i], int):
                params += hex(self.parameters[i])
            else:
                params += str(self.parameters[i])
            if i != len(self.parameters) - 1:
                params += ', '
        return params

    def __str__(self):
        if self.pushBit:
            temp = ' -> '
        else:
            temp = '    '

        com = "{0:0{1}x}".format(self.commandPosition,8).upper()+':'+temp+' '+COMMAND_NAMES[self.command]+' '
        if len(com) < 37:
            com += (37 - len(com)) * ' '
        if self.debugString != None:
            return com+self.strParams()+'   #'+self.debugString
        return com+self.strParams()

class MscScript:
    def __init__(self):
        self.cmds = []
        self.name = 'Unnamed Script'
        self.bounds = [0,0]
        self._iterationPosition = 0

    def __getitem__(self, key):
        return self.cmds[key]

    def __iter__(self):
        return self

    def __next__(self):
        if self._iterationPosition >= len(self.cmds):
            self._iterationPosition = 0
            raise StopIteration
        else:
            self._iterationPosition += 1
            return self.cmds[self._iterationPosition - 1]

    def next(self):
        return self.__next__()

    def __str__(self):
        returnVal = ""
        for command in self.cmds:
            returnVal += str(command) + "\n"
        return returnVal

    def __len__(self):
        return len(self.cmds)

    def read(self, f, start, end):
        self.bounds = [start - 0x30, end - 0x30]
        f.seek(start)
        self.cmds = disassembleCommands(f.read(end - start), start - 0x30)

    def getInstructionText(self, index):
        if index < 0 or index >= len(self.cmds):
            return ""
        else:
            return str(cmds[index])

    def getIndexOfInstruction(self, location):
        for i in range(len(self.cmds)):
            cmd = self.cmds[i]
            if cmd.commandPosition == location:
                return i
        return None

    def getInstructionOfIndex(self, index):
        return cmd[index].commandPosition

    def getCommand(self, location):
        cmdIndex = self.getIndexOfInstruction(location)
        if cmdIndex != None:
            return self.cmds[cmdIndex]
        return None

    def offset(self, offset):
        for cmd in self.cmds:
            if cmd.command in [0x4, 0x5, 0x2e, 0x34, 0x35, 0x36]:
                cmd.parameters[0] += offset

    def setStart(self, start):
        self.bounds[0] = start
        i = start
        for cmd in self.cmds:
            cmd.commandPosition = i
            i += len(cmd)

    def size(self):
        s = 0
        for cmd in self.cmds:
            if type(cmd) == Command:
                s += (0 if cmd.command in [0xFFFE, 0xFFFF] else 1) + getSizeFromFormat(COMMAND_FORMAT[cmd.command])
        return s

def readInt(f, endian):
    try:
        return struct.unpack(endian+'L', f.read(4))[0]
    except struct.error as e:
        print('pos - '+str(f.tell()))
        print(e.with_traceback)
        raise e

class MscFile:
    def __init__(self):
        self.scripts = []
        self.strings = []
        self.symbols = {}
        self.entryPoint = 0
        self.stringSize = 0
        self.unk = 0
        self._iterationPosition = 0

    def __getitem__(self, key):
        return self.scripts[key]

    def __iter__(self):
        return self

    def __next__(self):
        if self._iterationPosition >= len(self.scripts):
            self._iterationPosition = 0
            raise StopIteration
        else:
            self._iterationPosition += 1
            return self.scripts[self._iterationPosition - 1]

    def next(self):
        return self.__next__()

    def __str__(self):
        returnVal = ""
        for script in self.scripts:
            returnVal += (' ' * 20) + script.name + '\n' + ('-' * 50) + '\n'
            for command in script:
                returnVal += str(command) + "\n"
        return returnVal

    def __len__(self):
        return len(self.scripts)

    def readFromFile(self, f, headerEndianess = '<'):
        f.seek(0x10)
        entriesOffset = readInt(f, headerEndianess) + 0x30
        endOfScripts = entriesOffset
        if entriesOffset % 0x10 != 0:
            entriesOffset += 0x10 - (entriesOffset % 0x10)
        self.entryPoint = readInt(f, headerEndianess)
        entryCount = readInt(f, headerEndianess)
        self.unk = readInt(f, headerEndianess)
        self.stringSize = readInt(f, headerEndianess)
        stringCount = readInt(f, headerEndianess)
        scriptOffsets = []
        f.seek(entriesOffset)
        for i in range(entryCount):
            scriptOffsets.append(readInt(f, headerEndianess) + 0x30)
        sortedScriptOffsets = scriptOffsets
        sortedScriptOffsets.sort()
        if f.tell() % 0x10 != 0:
            f.seek(0x10 - (f.tell() % 0x10), 1)
        for i in range(stringCount):
            self.strings.append(f.read(self.stringSize).decode('utf-8').replace('\x00',''))
        for j in scriptOffsets:
            i = sortedScriptOffsets.index(j)
            start = sortedScriptOffsets[i]
            if i != len(scriptOffsets) - 1:
                end = sortedScriptOffsets[i+1]
            else:
                end = endOfScripts
            newScript = MscScript()
            newScript.name = 'script_%i' % i
            if i == self.entryPoint:
                newScript.name = 'Entrypoint Script'
            newScript.read(f, start, end)
            self.scripts.append(newScript)
        return self

    def readFromBytes(self, b, headerEndianess='>'):
        with tempfile.SpooledTemporaryFile(mode='w+b') as f:
            f.write(b)
            f.seek(0)
            self.readFromFile(f, headerEndianess)

    def getScriptAtLocation(self, location):
        for script in self.scripts:
            if script.bounds[0] <= location and script.bounds[1] > location:
                return script

    def addDebugStrings(self):
        for script in self.scripts:
            for i in range(len(script)):
                try:
                    if script[i].command == 0x2C and script[i].parameters[0] > 0:
                        script[i].debugString = self.strings[script[i-1].parameters[0]]
                except:
                    script[i].debugString = None

    def addScriptNames(self):
        for script in self.scripts:
            for i,command in enumerate(script):
                if command.command in range(0x2f, 0x31):
                    scriptName = None
                    print(command)
                    for j in range(i - 1, -1, -1):
                        print(j)
                        if script[j].pushBit:
                            print(str(j)+' has pushBit')
                            if script[j].command in (0xa, 0xd):
                                thisScript = self.getScriptAtLocation(script[j].parameters[0])
                                scriptNum = self.scripts.index(thisScript)
                                print("script_"+str(scriptNum))
                                command.parameters.insert(0, "script_"+str(scriptNum))
                            break
