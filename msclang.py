from msc import *
from argparse import ArgumentParser
# Try and install pycparser if it's not found 
try:
    from pycparser import c_parser, c_ast, parse_file
except ImportError:
    if input("Pycparser not found, install with pip? (y/n)").startswith('y'):
        try:
            import pip
        except ImportError:
            import sys
            sys.stderr.write("Error: Neither pycparser nor pip found\n")
            quit()
        else:
            pip.main(['install', 'pycparser'])
            import pycparser
    else:
        quit()
import re
import math
import struct
from subprocess import Popen, PIPE
import os.path
from xml_info import MscXmlInfo, VariableLabel, getXmlInfoPath

# Add to this as you see reasonable
global_constants = {
    "NULL"          : 0,
    "false"         : 0,
    "true"          : 1,
    "NULL_FUNC_PTR" : 0xFFFFFFFF,
    "M_E"           : math.e,
    "M_LOG2E"       : math.log2(math.e),
    "M_LOG10E"      : math.log10(math.e),
    "M_LN2"         : math.log(2),
    "M_LN10"        : math.log(10),
    "M_PI"          : math.pi,
    "M_PI_2"        : math.pi / 2,
    "M_PI_4"        : math.pi / 4,
    "M_1_PI"        : 1 / math.pi,
    "M_2_PI"        : 2 / math.pi,
    "M_2_SQRTPI"    : 2 / math.sqrt(math.pi),
    "M_SQRT2"       : math.sqrt(2),
    "M_SQRT1_2"     : 1 / math.sqrt(2)
}

# Note if you add to this, please only add not replace to support backwards compatibility
syscalls = {
    "sys_0" : 0,
    "sys_1" : 1,
    "sys_2" : 2,
    "sys_3" : 3,
    "sys_4" : 4,
    "sys_5" : 5,
    "sys_6" : 6,
    "sys_7" : 7,
    "sys_8" : 8,
    "sys_9" : 9,
    "sys_A" : 10,
    "sys_B" : 11,
    "sys_C" : 12,
    "sys_D" : 13,
    "sys_E" : 14,
    "sys_F" : 15,
    "sys_10" : 16,
    "sys_11" : 17,
    "sys_12" : 18,
    "sys_13" : 19,
    "sys_14" : 20,
    "sys_15" : 21,
    "sys_16" : 22,
    "sys_17" : 23,
    "sys_18" : 24,
    "sys_19" : 25,
    "sys_1A" : 26,
    "sys_1B" : 27,
    "sys_1C" : 28,
    "sys_1D" : 29,
    "sys_1E" : 30,
    "sys_1F" : 31,
    "sys_20" : 32,
    "sys_21" : 33,
    "sys_22" : 34,
    "sys_23" : 35,
    "sys_24" : 36,
    "sys_25" : 37,
    "sys_26" : 38,
    "sys_27" : 39,
    "sys_28" : 40,
    "sys_29" : 41,
    "sys_2A" : 42,
    "sys_2B" : 43,
    "sys_2C" : 44,
    "sys_2D" : 45,
    "sys_2E" : 46,
    "sys_2F" : 47,
    "sys_30" : 48,
    "sys_31" : 49,
    "sys_32" : 50,
    "sys_33" : 51,
    "sys_34" : 52,
    "sys_35" : 53,
    "sys_36" : 54,
    "sys_37" : 55,
    "sys_38" : 56,
    "sys_39" : 57,
    "sys_3A" : 58,
    "sys_3B" : 59,
    "sys_3C" : 60,
    "sys_3D" : 61,
    "sys_3E" : 62,
    "sys_3F" : 63,
    "sys_40" : 64,
    "sys_41" : 65,
    "sys_42" : 66,
    "sys_43" : 67,
    "sys_44" : 68,
    "sys_45" : 69,
    "sys_46" : 70,
    "sys_47" : 71,
    "sys_48" : 72,
    "sys_49" : 73,
    "sys_4A" : 74,
    "sys_4B" : 75,
    "sys_4C" : 76,
    "sys_4D" : 77
}

class CompilerError(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class PreprocessorError(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class FileRefs:
    def __init__(self, functions=[], globalVariables=[], globalVariableTypes={},functionTypes={}):
        self.functions = functions
        self.globalVariables = globalVariables
        self.globalVariableTypes = globalVariableTypes
        self.functionTypes = functionTypes

def removeComments(text):
    text = re.sub(
       '(?:\\/\\*(?=(?:[^"]*"[^"]*")*[^"]*$)(?:.|\\n)*?\\*\\/)|(?:\\/\\/(?=(?:[^"]*"[^"]*")*[^"]*$).*)', 
       '',
       text
    )
    return text

# Define a bunch of dictionaries to help resolve text to commands
assignmentOperationsInt = {
    "="  : 0x1c,
    "+=" : 0x1d,
    "-=" : 0x1e,
    "*=" : 0x1f,
    "/=" : 0x20,
    "%=" : 0x21,
    "&=" : 0x22,
    "|=" : 0x23,
    "^=" : 0x24
}

assignmentOperationsFloat = {
    "="  : 0x41,
    "+=" : 0x42,
    "-=" : 0x43,
    "*=" : 0x44,
    "/=" : 0x45,
    "%=" : 0x21,
    "&=" : 0x22,
    "|=" : 0x23,
    "^=" : 0x24
}

binaryOperationsInt = {
    "+"  : 0xe,
    "-"  : 0xf,
    "*"  : 0x10,
    "/"  : 0x11,
    "%"  : 0x12,
    "==" : 0x25,
    "!=" : 0x26,
    "<"  : 0x27,
    "<=" : 0x28,
    ">"  : 0x29,
    ">=" : 0x2a,
    "&"  : 0x16,
    "|"  : 0x17,
    "^"  : 0x19,
    "<<" : 0x1a,
    ">>" : 0x1b
}

binaryOperationsFloat = {
    "+"  : 0x3a,
    "-"  : 0x3b,
    "*"  : 0x3c,
    "/"  : 0x3d,
    "==" : 0x46,
    "!=" : 0x47,
    "<"  : 0x48,
    "<=" : 0x49,
    ">"  : 0x4a,
    ">=" : 0x4b,
    "&"  : 0x16,
    "%"  : 0x12,
    "|"  : 0x17,
    "&&"  : 0x16,
    "||"  : 0x17,
    "^"  : 0x19,
    "<<" : 0x1a,
    ">>" : 0x1b
}

operationOpposite = {
    0x26 : 0x25,
    0x25 : 0x26,
    0x2a : 0x27,
    0x29 : 0x28,
    0x28 : 0x29,
    0x27 : 0x2a
}

floatOperations = list(range(0x3a,0x46)) + [0x38]
FLOAT_RETURN_SYSCALLS = [0x08, 0x0a, 0x0f, 0x11, 0x13, 0x15, 0x17, 0x1b, 0x25, 0x28, 0x2b, 0x2c, 0x2f, 0x32, 0x34, 0x35, 0x3d, 0x3f, 0x40, 0x45]

class Label:
    def __init__(self, name=None):
        self.name = name

    def __str__(self):
        if self.name:
            return self.name+":"
        else:
            return "Label "+hex(id(self))+":"

# This is to get around the fact python will throw an exception on
# int('0900', 0) but not int('0900'). Sucks but whatever...
def toInt(i):
    try:
        return int(i,0)
    except:
        return int(i)

#Returns variable scope, type and index in a tuple
def resolveVariable(name):
    global refs, localVars, localVarTypes
    if name in localVars:
        varScope = 0
        varType = localVarTypes[name]
        varIndex = localVars.index(name)
    elif name in refs.globalVariables:
        varScope = 1
        varType = refs.globalVariableTypes[name]
        varIndex = refs.globalVariables.index(name)
    else:
        raise CompilerError("Invalid reference")
    return (varScope,varType,varIndex)

_C_ESCAPES = {
    "\\" : "\\",
    "n" : "\n",
    "a" : "\a",
    "b" : "\b",
    "f" : "\f",
    "r" : "\r",
    "t" : "\t",
    "v" : "\v",
    "'" : "'",
    '"' : '"',
    "?" : "?",
    "0" : "\0"
}

_OCTAL_CHARS = range(ord("0"), ord("8"))

def apply_c_escapes(string):
    new_string = ""
    n = 0
    while n < len(string):
        if string[n] == "\\":
            n += 1
            if n < len(string):
                if len(string) > n + 2 and all(ord(string[i]) in _OCTAL_CHARS for i in range(n, n+3)):
                    new_string += chr(int(string[n:n+3], 8))
                    n += 2
                elif string[n] in _C_ESCAPES:
                    new_string += _C_ESCAPES[string[n]]
                elif string[n] == "x":
                    if len(string) > n + 2:
                        new_string += chr(int(string[n+1:n+3], 0x10))
                        n += 2
                    else:
                        raise CompilerError("Invalid hex escape, not enough values")
            else:
                raise CompilerError(f"Error escaping string '{string}'")
        else:
            new_string += string[n]
        n += 1
    return new_string

# Guess if a command returns a float or an int
def isCommandFloat(cmd, lookingFor):
    global refs, localVars, localVarTypes
    if cmd.command == 0x2d and cmd.parameters[1] in FLOAT_RETURN_SYSCALLS:
        return True
    if cmd.command == 0x2d:
        return lookingFor
    if cmd.command == 0x2f:
        if cmd.functionName in refs.functions:
            return (refs.functionTypes[cmd.functionName] == "float")
    if cmd.command in floatOperations or (cmd.command == 0xA and type(cmd.parameters[0]) == float):
        return True
    if cmd.command == 0xb:
        if cmd.parameters[0] == 0 and localVarTypes[localVars[cmd.parameters[1]]] == "float":
            return True
        if cmd.parameters[0] == 1 and refs.globalVariableTypes[refs.globalVariables[cmd.parameters[1]]] == "float":
            return True
    return False

# Take a abstract syntax tree node and recursively compile it
def compileNode(node, loopParent=None, parentLoopCondition=None):
    global refs, localVars, localVarTypes, args, xmlInfo

    nodeOut = []

    if isinstance(node, list):
        for i in node:
            nodeOut += compileNode(i, loopParent, parentLoopCondition)
        return nodeOut
    elif not isinstance(node, c_ast.Node):
        raise ValueError("That's no node that's a "+str(type(node)))

    # Macro for getting the last command (skip any labels)
    def getLastCommand():
        if len(nodeOut) > 0:
            i = 1
            while i <= len(nodeOut):
                if type(nodeOut[-i]) == Command:
                    return nodeOut[-i]
                i += 1

    # Macro for marking the last command as an argument for the current command
    def addArg():
        if len(nodeOut) > 0:
            i = 1
            while i <= len(nodeOut):
                if type(nodeOut[-i]) == Command and not nodeOut[-i].command in range(0x2f,0x32) and not nodeOut[-i].command in range(0x38,0x3a):
                    nodeOut[-i].pushBit = True
                    return
                elif type(nodeOut[-i]) == Command and not nodeOut[-i].command in range(0x38,0x3a):
                    while i <= len(nodeOut):
                        if type(nodeOut[-i]) == Command and nodeOut[-i].command == 0x2e:
                            nodeOut[-i].pushBit = True
                            return
                        i += 1
                i += 1

    t = type(node)

    # Check the type, depending on which type it is compile as it should
    # If an argument needs to be compiled, recursively call compile on the node

    # How to read the following code:
    # 1. read as if t is NodeType
    # 2. addArgs() = the last compiled command should be pushed to the stack
    # 3. being appended to nodeOut is adding it to the compiled version of the node
    # 4. Command(n, l) is defining a comamnd of id n with a list of args l
    #    the definition for Command is in msc.py, a dictionary of command name to id
    #    is also available in msc.py called "COMMAND_IDS" near the top
    if t == c_ast.Decl:
        if not node.name in localVars:
            localVarNum = len(localVars)
            localVars.append(node.name)
            localVarTypes[node.name] = node.type.type.names[-1]
        else:
            localVarNum = localVars.index(node.name)
        if node.init != None:
            nodeOut += compileNode(node.init, loopParent, parentLoopCondition)
            addArg()
            if node.type.type.names[-1] == "float" and not isCommandFloat(getLastCommand(), True):
                nodeOut.append(Command(0x38, [0]))
            elif node.type.type.names[-1] != "float" and isCommandFloat(getLastCommand(), False):
                nodeOut.append(Command(0x39, [0]))
            nodeOut.append(Command(0x1C, [0, localVarNum]))
    elif t == c_ast.Constant:
        if node.type == "int" or node.type == "bool":
            newValue = toInt(node.value) & 0xFFFFFFFF
            nodeOut.append(Command(0xD if newValue <= 0xFFFF and args.usePushShort else 0xA, [newValue]))
        elif node.type == "float" or node.type == "double":
            nodeOut.append(Command(0xA, [float(node.value.rstrip('f'))]))
        elif node.type == "string":
            string = apply_c_escapes(node.value[1:-1])
            if not string in msc.strings:
                msc.strings.append(string)
            nodeOut.append(Command(0xD, [msc.strings.index(string)]))
    elif t == c_ast.Assignment:
        nodeOut += compileNode(node.rvalue, loopParent, parentLoopCondition)
        addArg()
        if type(node.lvalue) != c_ast.ID:
            raise CompilerError("Error at %s: Left hand side of assignment operation must be variable."%str(node.coord))
        try:
            varScope,varType,varIndex = resolveVariable(node.lvalue.name)
        except CompilerError:
            raise CompilerError("Error at %s: Left hand side of assignment operation must be a valid reference to a variable."%str(node.coord))

        if args.autocast:
            if varType == "float" and not isCommandFloat(getLastCommand(), True):
                    nodeOut.append(Command(0x38, [0]))
            elif varType != "float" and isCommandFloat(getLastCommand(), False):
                    nodeOut.append(Command(0x39, [0]))

        if varType == "float":
            operation = assignmentOperationsFloat[node.op]
        else:
            operation = assignmentOperationsInt[node.op]
        nodeOut.append(Command(operation,[varScope,varIndex]))
    elif t == c_ast.TernaryOp:
        if (type(node.iftrue) == c_ast.TernaryOp and type(node.iffalse) == c_ast.Constant and
            node.iffalse.type == "int" and int(node.iffalse.value, 0) == 0 and
            type(node.iftrue.iftrue) == c_ast.Constant and node.iftrue.iftrue.type == "int" and
            int(node.iftrue.iftrue.value, 0) == 1 and type(node.iftrue.iffalse) == c_ast.Constant and
            node.iftrue.iffalse.type == "int" and int(node.iftrue.iffalse.value, 0) == 0):
            # If tail end ternary combination is possible
            endLabel = Label()
            isFalseLabel = Label()
            nodeOut += compileNode(node.cond, loopParent, parentLoopCondition)
            addArg()
            nodeOut.append(Command(0x34, [isFalseLabel]))
            nodeOut += compileNode(node.iftrue.cond, loopParent, parentLoopCondition)
            addArg()
            nodeOut.append(Command(0x34, [isFalseLabel]))
            nodeOut.append(Command(0xD if args.usePushShort else 0xA, [1], True))
            nodeOut.append(Command(0x36, [endLabel]))
            nodeOut.append(isFalseLabel)
            nodeOut.append(Command(0xD if args.usePushShort else 0xA, [0], True))
            nodeOut.append(endLabel)
        else:
            endLabel = Label()
            isFalseLabel = Label()
            nodeOut += compileNode(node.cond, loopParent, parentLoopCondition)
            addArg()
            nodeOut.append(Command(0x34, [isFalseLabel]))
            nodeOut += compileNode(node.iftrue, loopParent, parentLoopCondition)
            addArg()
            nodeOut.append(Command(0x36, [endLabel]))
            nodeOut.append(isFalseLabel)
            nodeOut += compileNode(node.iffalse, loopParent, parentLoopCondition)
            addArg()
            nodeOut.append(endLabel)
    elif t == c_ast.UnaryOp:
        if node.op == "!":
            nodeOut += compileNode(node.expr, loopParent, parentLoopCondition)
            lastCommand = getLastCommand()
            if lastCommand.command in operationOpposite:
                lastCommand.command = operationOpposite[lastCommand.command]
            else:
                addArg()
                nodeOut.append(Command(0x2b))
        elif node.op == "~":
            nodeOut += compileNode(node.expr, loopParent, parentLoopCondition)
            addArg()
            nodeOut.append(Command(0x18))
        elif node.op == "p++":
            if type(node.expr) != c_ast.ID:
                CompilerError("Error at %s: Cannot increment non variable."%str(node.coord))
            varScope,varType,varIndex = resolveVariable(node.expr.name)
            op = 0x3F if varType == "float" else 0x14
            nodeOut.append(Command(op, [varScope,varIndex]))
        elif node.op == "p--":
            if type(node.expr) != c_ast.ID:
                CompilerError("Error at %s: Cannot decrement non variable."%str(node.coord))
            varScope,varType,varIndex = resolveVariable(node.expr.name)
            op = 0x40 if varType == "float" else 0x15
            nodeOut.append(Command(op, [varScope,varIndex]))
        elif node.op == "-":
            if type(node.expr) == c_ast.Constant:
                node = node.expr
                if node.type == "int":
                    newValue = (-toInt(node.value)) & 0xFFFFFFFF
                    nodeOut.append(Command(0xD if newValue <= 0xFFFF and args.usePushShort else 0xA, [newValue]))
                elif node.type == "float" or node.type == "double":
                    nodeOut.append(Command(0xA, [-float(node.value.rstrip('f'))]))
            else:
                nodeOut += compileNode(node.expr, loopParent, parentLoopCondition)
                addArg()
                op = 0x3E if isCommandFloat(getLastCommand(), False) else 0x13
                nodeOut.append(Command(op))
        elif node.op == "&":
            if type(node.expr) == c_ast.ID:
                nodeOut.append(Command(0xA,[node.expr.name]))
            else:
                raise CompilerError("Error at %s: The addressing of non-functions is not allowed."%str(node.coord))
        elif node.op == "sizeof":
            nodeOut.append(Command(0xD,[0x4]))
        else:
            raise CompilerError("Operation %s not supported" % node.op)
    elif t == c_ast.ID:
        try:
            varScope,varType,varIndex = resolveVariable(node.name)
            nodeOut.append(Command(0xb,[varScope,varIndex]))
        except CompilerError:
            if node.name in global_constants:
                nodeOut.append(Command(0xA, [global_constants[node.name]]))
            elif node.name in refs.functions:
                nodeOut.append(Command(0xA, [node.name]))
            else:
                raise CompilerError("Error at %s: Invalid reference."%str(node.coord))
    elif t == c_ast.Cast:
        nodeOut += compileNode(node.expr, loopParent, parentLoopCondition)
        addArg()
        if node.to_type.type.type.names[-1] == "float":
            nodeOut.append(Command(0x38,[0]))
        else:
            nodeOut.append(Command(0x39,[0]))
    elif t == c_ast.Return:
        if node.expr == None:
            nodeOut.append(Command(0x7))
        else:
            nodeOut += compileNode(node.expr, loopParent, parentLoopCondition)
            addArg()
            nodeOut.append(Command(0x6))
    elif t == c_ast.BinaryOp:
        if node.op in ["&&", "||"]:
            nodeOut += compileNode(node.left, loopParent, parentLoopCondition)
            addArg()
            if node.op == "||":
                endOrLabel, trueLabel, falseLabel = Label(), Label(), Label()
                nodeOut.append(Command(0x35, [trueLabel]))
                nodeOut += compileNode(node.right, loopParent, parentLoopCondition)
                addArg()
                nodeOut.append(Command(0x34, [falseLabel]))
                nodeOut.append(trueLabel)
                nodeOut.append(Command(0xD if args.usePushShort else 0xA, [1]))
                addArg()
                nodeOut.append(Command(0x36, [endOrLabel]))
                nodeOut.append(falseLabel)
                nodeOut.append(Command(0xD if args.usePushShort else 0xA, [0]))
                addArg()
                nodeOut.append(endOrLabel)
            else:
                endAndLabel, falseLabel = Label(), Label()
                nodeOut.append(Command(0x34, [falseLabel]))
                nodeOut += compileNode(node.right, loopParent, parentLoopCondition)
                addArg()
                nodeOut.append(Command(0x34, [falseLabel]))
                nodeOut.append(Command(0xD if args.usePushShort else 0xA, [1]))
                addArg()
                nodeOut.append(Command(0x36, [endAndLabel]))
                nodeOut.append(falseLabel)
                nodeOut.append(Command(0xD if args.usePushShort else 0xA, [0]))
                addArg()
                nodeOut.append(endAndLabel)
        else:
            nodeOut += compileNode(node.left, loopParent, parentLoopCondition)
            addArg()
            pos = len(nodeOut)
            isFloat1 = isCommandFloat(getLastCommand(), False)
            nodeOut += compileNode(node.right, loopParent, parentLoopCondition)
            addArg()
            isFloat2 = isCommandFloat(getLastCommand(), isFloat1)
            isFloat = isFloat1 or isFloat2
            cmd = binaryOperationsFloat[node.op] if isFloat else binaryOperationsInt[node.op]
            if not cmd in range(0x16, 0x1C) and isFloat and args.autocast:
                if not isFloat1:
                    nodeOut.insert(pos, Command(0x38,[0]))
                if not isFloat2:
                    nodeOut.append(Command(0x38,[0]))
            nodeOut.append(Command(cmd))
    elif t == c_ast.Goto:
        nodeOut.append(Command(0x4,[node.name]))
    elif t == c_ast.Label:
        nodeOut.append(Label(node.name))
        nodeOut += compileNode(node.stmt, loopParent, parentLoopCondition)
    elif t == c_ast.If:
        nodeOut += compileNode(node.cond, loopParent, parentLoopCondition)
        isIfNot = False
        lastCommand = getLastCommand()
        if lastCommand != None and lastCommand.command == 0x2b:
            nodeOut.remove(getLastCommand())
            isIfNot = True
        addArg()
        ifFalseLabel = Label()
        if node.iffalse != None:
            endLabel = Label()
        nodeOut.append(Command(0x35 if isIfNot else 0x34, [ifFalseLabel]))
        nodeOut += compileNode(node.iftrue, loopParent, parentLoopCondition)
        if node.iffalse != None:
            nodeOut.append(Command(0x36, [endLabel]))
        nodeOut.append(ifFalseLabel)
        if node.iffalse != None:
            nodeOut += compileNode(node.iffalse, loopParent, parentLoopCondition)
            nodeOut.append(endLabel)
    elif t == c_ast.Compound:
        if node.block_items != None:
            for i in node.block_items:
                nodeOut += compileNode(i, loopParent, parentLoopCondition)
    elif t == c_ast.While:
        loopTop = Label()
        endLabel = Label()
        conditionLabel = Label()
        nodeOut.append(Command(0x36, [conditionLabel]))
        nodeOut.append(loopTop)
        nodeOut += compileNode(node.stmt, endLabel, conditionLabel)
        nodeOut.append(conditionLabel)
        nodeOut += compileNode(node.cond, loopParent, parentLoopCondition)
        addArg()
        nodeOut.append(Command(0x35, [loopTop]))
        nodeOut.append(endLabel)
    elif t == c_ast.DoWhile:
        loopTop = Label()
        endLabel = Label()
        conditionLabel = Label()
        nodeOut.append(loopTop)
        nodeOut += compileNode(node.stmt, endLabel, conditionLabel)
        nodeOut.append(conditionLabel)
        nodeOut += compileNode(node.cond, loopParent, parentLoopCondition)
        addArg()
        nodeOut.append(Command(0x35, [loopTop]))
        nodeOut.append(endLabel)
    elif t == c_ast.For:
        for decl in node.init.decls:
            nodeOut += compileNode(decl, loopParent, parentLoopCondition)
        loopTop = Label()
        endLabel = Label()
        conditionLabel = Label()
        nodeOut.append(loopTop)
        nodeOut += compileNode(node.stmt, endLabel, conditionLabel)
        nodeOut.append(conditionLabel)
        nodeOut += compileNode(node.next, endLabel, conditionLabel)
        nodeOut += compileNode(node.cond, loopParent, parentLoopCondition)
        addArg()
        nodeOut.append(Command(0x35, [loopTop]))
        nodeOut.append(endLabel)
    elif t == c_ast.Break:
        nodeOut.append(Command(0x4, [loopParent]))
    elif t == c_ast.Continue:
        nodeOut.append(Command(0x4, [parentLoopCondition]))
    elif t == c_ast.Switch:
        if type(node.cond) == c_ast.ID:
            compiledVariable = compileNode(node.cond,loopParent, parentLoopCondition)
        else:
            raise CompilerError("Error at %s: Switch statements must have a variable as the condition"%str(node.coord))
        blockEnd = Label()
        for i in node.stmt.block_items:
            nextStatement = Label()
            if type(i) == c_ast.Case:
                nodeOut += compileNode(i.expr, loopParent, parentLoopCondition)
                addArg()
                nodeOut += compiledVariable
                addArg()
                nodeOut.append(Command(0x25,[],True))
                nodeOut.append(Command(0x34,[nextStatement]))
                nodeOut += compileNode(i.stmts, blockEnd, parentLoopCondition)
                nodeOut.append(nextStatement)
            elif type(i) == c_ast.Default:
                nodeOut += compileNode(i.stmts, blockEnd, parentLoopCondition)
            else:
                CompilerError("Error at %s: Switch statements cannot have anything but cases and defaults"%str(i.coord))
        nodeOut.append(blockEnd)
    elif t == c_ast.FuncCall:
        name = None if type(node.name) != c_ast.ID else node.name.name
        if name == None and type(node.name) == c_ast.StructRef:
            syscallName = node.name.name.name
            methodName = node.name.field.name
            syscallInfo = xmlInfo.getSyscall(syscallName)
            if syscallInfo != None:
                methodInfo = syscallInfo.getMethod(methodName)
                if methodInfo == None:
                    raise CompilerError("Syscall {}, method {} is not defined".format(syscallName, methodName))
                nodeOut.append(Command(0xA, [methodInfo.id], pushBit=True))
                if node.args != None:
                    for arg in node.args.exprs:
                        nodeOut += compileNode(arg, loopParent, parentLoopCondition)
                        addArg()
                    nodeOut.append(Command(0x2d, [len(node.args.exprs) + 1, syscallInfo.id]))
                else:
                    nodeOut.append(Command(0x2d, [1, syscallInfo.id]))
            else:
                raise CompilerError("Syscall {} not found".format(syscallName))
        elif name == "printf":
            for arg in node.args.exprs:
                nodeOut += compileNode(arg, loopParent, parentLoopCondition)
                addArg()
            nodeOut.append(Command(0x2c, [len(node.args.exprs)]))
        elif name == "set_main":
            if len(node.args.exprs) == 0:
                raise CompilerError("Error at %s: set_main requires at least 1 argument (function pointer)"%str(node.coord))
            funcPtr = compileNode(node.args.exprs[0], loopParent, parentLoopCondition)
            funcArgs = node.args.exprs[1:]
            for arg in funcArgs:
                nodeOut += compileNode(arg, loopParent, parentLoopCondition)
                addArg()
            nodeOut += funcPtr
            addArg()
            nodeOut.append(Command(0x30, [len(funcArgs)]))
        elif name == "callFunc3":
            if len(node.args.exprs) == 0:
                raise CompilerError("Error at %s: callFunc3 requires at least 1 argument (function pointer)"%str(node.coord))
            funcPtr = compileNode(node.args.exprs[0], loopParent, parentLoopCondition)
            funcArgs = node.args.exprs[1:]
            for arg in funcArgs:
                nodeOut += compileNode(arg, loopParent, parentLoopCondition)
                addArg()
            nodeOut += funcPtr
            addArg()
            nodeOut.append(Command(0x31, [len(funcArgs)]))
        elif name in syscalls:
            sysNum = syscalls[name]
            for arg in node.args.exprs:
                nodeOut += compileNode(arg, loopParent, parentLoopCondition)
                addArg()
            nodeOut.append(Command(0x2d, [len(node.args.exprs), sysNum]))
        else:
            endLabel = Label()
            if name != None and not name in refs.functions:
                raise CompilerError("Error at %s: function %s does not exist"%(str(node.coord),name))
            elif name != None:
                funcPtr = [Command(0xA, [name], True)]
            elif type(node.name) == c_ast.UnaryOp and node.name.op == "*":
                funcPtr = compileNode(node.name.expr, loopParent, parentLoopCondition)
            nodeOut.append(Command(0x2e, [endLabel]))
            if node.args != None:
                for arg in node.args.exprs:
                    nodeOut += compileNode(arg, loopParent, parentLoopCondition)
                    addArg()
            nodeOut += funcPtr
            addArg()
            functionCallCommand = Command(0x2f, [len(node.args.exprs) if node.args != None else 0])
            functionCallCommand.functionName = name
            nodeOut.append(functionCallCommand)
            nodeOut.append(endLabel)
    else:
        node.show()
        print(node)
        print(node.__slots__)
        print()

    return nodeOut

def compileScript(func):
    global msc, refs, localVars, localVarTypes
    localVars = [x.name for x in func.decl.type.args.params] if func.decl.type.args != None else []
    localVarTypes = dict([(x.name, x.type.type.names[-1]) for x in func.decl.type.args.params] if func.decl.type.args != None else [])
    argCount = len(localVars)
    script = []
    if func.body.block_items != None:
        for node in func.body.block_items:
            script += compileNode(node)
    script.insert(0, Command(2, [argCount, len(localVars)]))
    script.append(Command(3))
    return script

# Fill in function pointers, labels with locations rather than strings
def resolveReferences(msc):
    global refs
    scriptPositions = []
    labelPostions = {}
    namedLabelPositions = []
    currentPos = 0x10
    for i,script in enumerate(msc.scripts):
        namedLabelPositions.append({})
        scriptPositions.append(currentPos)
        for cmd in script.cmds:
            if type(cmd) == Command:
                cmd.commandPosition = currentPos
                currentPos += (0 if cmd.command in [0xFFFE, 0xFFFF] else 1) + getSizeFromFormat(COMMAND_FORMAT[cmd.command])
            elif type(cmd) == Label:
                if cmd.name != None:
                    namedLabelPositions[i][cmd.name] = currentPos
                labelPostions[cmd] = currentPos
    refs.scriptPositions = scriptPositions
    for j,script in enumerate(msc.scripts):
        for cmd in script.cmds:
            if type(cmd) == Command:
                for i,arg in enumerate(cmd.parameters):
                    if type(arg) == str:
                        if arg in namedLabelPositions[j]:
                            cmd.parameters[i] = namedLabelPositions[j][arg]
                        else:
                            cmd.parameters[i] = scriptPositions[refs.functions.index(arg)]
                    elif type(arg) == Label:
                        cmd.parameters[i] = labelPostions[arg]

# Thanks Triptych https://stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except
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

# Write as MSCSB format
def writeToFile(msc):
    global refs, args
    currentPos = 0x10
    for script in msc.scripts:
        currentPos += script.size()

    # Calculate string buffer size based on the longest string
    maxStringLength = 0
    for string in msc.strings:
        if len(string) > maxStringLength:
            maxStringLength = len(string)
    if maxStringLength % 0x10 != 0:
        maxStringLength += 0x10 - (maxStringLength % 0x10)

    # Write file header
    fileBytes = MSC_MAGIC
    fileBytes += struct.pack('<L', currentPos)
    fileBytes += struct.pack('<L', 0x10 if not 'main' in refs.functions else refs.scriptPositions[refs.functions.index('main')])
    fileBytes += struct.pack('<L', len(msc.scripts))
    fileBytes += struct.pack('<L', 0x16)#This probably doesn't matter?
    fileBytes += struct.pack('<L', maxStringLength)
    fileBytes += struct.pack('<L', len(msc.strings))
    fileBytes += struct.pack('<L', 0)
    fileBytes += struct.pack('<L', 0)
    fileBytes += b'\x00' * 0x10

    # Write each script
    for script in msc.scripts:
        for cmd in script:
            if type(cmd) == Command:
                for i in range(len(cmd.parameters)):
                    if type(cmd.parameters[i]) == float:
                        cmd.parameters[i] = struct.unpack('>L', struct.pack('>f', cmd.parameters[i]))[0]
                fileBytes += cmd.write()

    # Write padding
    if len(fileBytes) % 0x10 != 0:
        fileBytes += b'\x00' * (0x10 - (len(fileBytes) % 0x10))

    # Write script positions (may be unused tbh)
    for i in range(len(msc.scripts)):
        fileBytes += struct.pack('<L',refs.scriptPositions[i])

    # Write more padding
    if len(fileBytes) % 0x10 != 0:
        fileBytes += b'\x00' * (0x10 - (len(fileBytes) % 0x10))

    # Write the strings (+ padding)
    for string in msc.strings:
        fileBytes += string.encode('utf-8')
        fileBytes += b'\x00' * (maxStringLength - len(string))

    # Write to file
    filename = 'output.mscsb' if args.filename == None else args.filename
    with open(filename, 'wb') as f:
        f.write(fileBytes)

def compileAST(ast):
    global args, msc, refs
    refs = FileRefs()
    msc = MscFile()
    for decl in ast.ext:
        if isinstance(decl, c_ast.Decl):
            if decl.init != None:
                raise CompilerError("Error at %s: Global Variables cannot have an initial value, instead include the declaration in another function." % str(decl.coord))
            if decl.name in refs.globalVariables:
                raise CompilerError("Error at %s: Global variable %s cannot be redeclared." % (str(decl.coord),decl.name))
            else:
                refs.globalVariables.append(decl.name)
                refs.globalVariableTypes[decl.name] = decl.type.type.names[-1]
        elif isinstance(decl, c_ast.FuncDef):
            if decl.decl.name in refs.functions:
                raise CompilerError("Error at %s: Function %s cannot be redeclared." % (str(decl.coord),decl.name))
            else:
                refs.functions.append(decl.decl.name)
                refs.functionTypes[decl.decl.name] = decl.decl.type.type.type.names[0]
        else:
            raise CompilerError("Error at %s: unsupported statement, structure or declaration. Use --ignore-invalid to avoid this error." % str(decl.coord))

    for decl in ast.ext:
        if isinstance(decl, c_ast.FuncDef):
            newScript = MscScript()
            newScript.cmds = compileScript(decl)
            msc.scripts.append(newScript)
    resolveReferences(msc)
    writeToFile(msc)

# Parse and compile from a string
def compileString(fileText):
    global args, msc, refs
    parser = c_parser.CParser()
    text = removeComments(fileText)
    ast = parser.parse(text, filename='<none>')
    compileAST(ast)

def compileFile(filepath):
    with open(filepath, 'r') as f:
        return compileString(f.read())

def preprocess(filepath):
    global args
    try:
        process = Popen(["cpp" if args.preprocessor == None else args.preprocessor, filepath], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
        if output != None:
            output = output.decode('latin8').replace('\r\n', '\n')
            return output
    except:
        pass

    with open(filepath, 'r') as f:
        return removeComments(f.read())

# Compile contents of the file to a string
def main(arguments):
    global args, xmlInfo
    args = arguments
    # Use path passed by argument if it exists,
    # else use the path found from getXmlInfoPath()
    # if no XmlInfo file is found, xmlPath will be None
    # MscXmlInfo(None) (aka filename=None) will be an empty MscXmlInfo object
    xmlPath = args.xmlPath if args.xmlPath != None else getXmlInfoPath()
    xmlInfo = MscXmlInfo(xmlPath)
    for s in xmlInfo.syscalls:
        syscalls[s.name] = s.id
    for file in args.files:
        if args.filename == None:
            args.filename = os.path.basename(os.path.splitext(file)[0]) + '.mscsb'
        compileString(preprocess(file))

if __name__ == "__main__":
    parser = ArgumentParser(description="Compile msC to MSC bytecode")
    parser.add_argument('files', metavar='files', type=str, nargs='+',
                        help='files to compile')
    parser.add_argument('-o', dest='filename', help='Filename to output to')
    parser.add_argument('-pp', dest='preprocessor', help='Preprocessor to use')
    parser.add_argument('-a', '--autocast', dest='autocast', action='store_true', help='Autocast between int and float types when relevant (Note: don\'t use with decompiled files)')
    parser.add_argument('-i', '--pushInt', dest='usePushShort', action='store_false', help='Disable using pushShort as a space saver')
    parser.add_argument('-x', '--xmlPath', dest='xmlPath', help="Path to load overload MSC xml info")
    main(parser.parse_args())
