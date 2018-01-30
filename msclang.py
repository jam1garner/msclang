from msc import *
from argparse import ArgumentParser
from pycparser import c_parser, c_ast, parse_file
import re
import math
import struct

#Add to this as you see reaasonable 
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

#Note if you add to this, please only add not replace to support backwards compatibility
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

class FileRefs:
    def __init__(self, functions=[], globalVariables=[], globalVariableTypes={}):
        self.functions = functions
        self.globalVariables = globalVariables
        self.globalVariableTypes = globalVariableTypes

def removeComments(text):
    text = re.sub(
       '(?:\\/\\*(?=(?:[^"]*"[^"]*")*[^"]*$)(.|\\n)*?\\*\\/)|(?:\\/\\/(?=(?:[^"]*"[^"]*")*[^"]*$).*)', 
       '', 
       text
    )
    return text

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
    "&&"  : 0x16,
    "||"  : 0x17,
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
    "|"  : 0x17,
    "&&"  : 0x16,
    "||"  : 0x17,
    "^"  : 0x19,
    "<<" : 0x1a,
    ">>" : 0x1b
}

floatOperations = list(range(0x3a,0x46)) + [0x38]

class Label:
    def __init__(self, name=None):
        self.name = name

    def __str__(self):
        if self.name:
            return self.name+":"
        else:
            return "Label "+hex(id(self))+":"

#This is to get around the fact python will throw an exception on
#int('0900', 0) but not int('0900'). Sucks but whatever...
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

def isCommandFloat(cmd):
    global refs, localVars, localVarTypes
    if cmd.command in floatOperations or (cmd.command == 0xA and type(cmd.parameters[0]) == float):
        return True
    if cmd.command == 0xb:
        if cmd.parameters[0] == 0 and localVarTypes[localVars[cmd.parameters[1]]] == "float":
            return True
        if cmd.parameters[0] == 1 and refs.globalVariableTypes[refs.globalVariables[cmd.parameters[1]]] == "float":
            return True
    return False

def compileNode(node, loopParent=None, parentLoopCondition=None):
    global refs, localVars, localVarTypes

    nodeOut = []

    if isinstance(node, list):
        for i in node:
            nodeOut += compileNode(i, loopParent, parentLoopCondition)
        return nodeOut
    elif not isinstance(node, c_ast.Node):
        raise ValueError("That's no node that's a "+str(type(node)))

    def getLastCommand():
        if len(nodeOut) > 0:
            i = 1
            while i <= len(nodeOut):
                if type(nodeOut[-i]) == Command:
                    return nodeOut[-i]
                i += 1

    def addArg():
        if len(nodeOut) > 0:
            i = 1
            while i <= len(nodeOut):
                if type(nodeOut[-i]) == Command and not nodeOut[-i].command in range(0x2f,0x32) and not nodeOut[-i].command in range(0x38,0x40): 
                    nodeOut[-1].pushBit = True
                    return
                elif type(nodeOut[-i]) == Command and not nodeOut[-i].command in range(0x38,0x40):
                    while i <= len(nodeOut):
                        if type(nodeOut[-i]) == Command and nodeOut[-i].command == 0x2e:
                            nodeOut[-i].pushBit = True
                            return
                        i += 1
                i += 1

    t = type(node)

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
            if node.type.type.names[-1] == "float" and not isCommandFloat(getLastCommand()):
                nodeOut.append(Command(0x38, [0]))
            elif node.type.type.names[-1] != "float" and isCommandFloat(getLastCommand()):
                nodeOut.append(Command(0x39, [0]))
            nodeOut.append(Command(0x1C, [0, localVarNum]))
    elif t == c_ast.Constant:
        if node.type == "int" or node.type == "bool":
            newValue = toInt(node.value) & 0xFFFFFFFF
            nodeOut.append(Command(0xD if newValue <= 0xFFFF else 0xA, [newValue]))
        elif node.type == "float":
            nodeOut.append(Command(0xA, [float(node.value.rstrip('f'))]))
        elif node.type == "string":
            if not node.value[1:-1] in msc.strings:
                msc.strings.append(node.value[1:-1])
            nodeOut.append(Command(0xD, [msc.strings.index(node.value[1:-1])]))
    elif t == c_ast.Assignment:
        nodeOut += compileNode(node.rvalue, loopParent, parentLoopCondition)
        addArg()
        if type(node.lvalue) != c_ast.ID:
            raise CompilerError("Error at %s: Left hand side of assignment operation must be variable."%str(node.coord))
        try:
            varScope,varType,varIndex = resolveVariable(node.lvalue.name)
        except CompilerError:
            raise CompilerError("Error at %s: Left hand side of assignment operation must be a valid reference to a variable."%str(node.coord))
        
        if varType == "float" and not isCommandFloat(getLastCommand()):
                nodeOut.append(Command(0x38, [0]))
        elif varType != "float" and isCommandFloat(getLastCommand()):
                nodeOut.append(Command(0x39, [0]))
        
        if varType == "float":
            operation = assignmentOperationsFloat[node.op]
        else:
            operation = assignmentOperationsInt[node.op]
        nodeOut.append(Command(operation,[varScope,varIndex]))
    elif t == c_ast.UnaryOp:
        if node.op == "!":
            nodeOut += compileNode(node.expr, loopParent, parentLoopCondition)
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
            nodeOut += compileNode(node.expr, loopParent, parentLoopCondition)
            addArg()
            op = 0x3E if isCommandFloat(nodeOut[-1]) else 0x13
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
            op = 0x8 if isCommandFloat(getLastCommand()) else 0x6
            nodeOut.append(Command(op))
    elif t == c_ast.BinaryOp:
        nodeOut += compileNode(node.left, loopParent, parentLoopCondition)
        addArg()
        pos = len(nodeOut)
        isFloat1 = isCommandFloat(getLastCommand())
        nodeOut += compileNode(node.right, loopParent, parentLoopCondition)
        addArg()
        isFloat2 = isCommandFloat(getLastCommand())
        isFloat = isFloat1 or isFloat2
        cmd = binaryOperationsFloat[node.op] if isFloat else binaryOperationsInt[node.op]
        if not cmd in range(0x16, 0x1C) and isFloat:
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
        #TODO: optimize ifNot scenario
        nodeOut += compileNode(node.cond, loopParent, parentLoopCondition)
        addArg()
        ifFalseLabel = Label()
        if node.iffalse != None:
            endLabel = Label()
        nodeOut.append(Command(0x34, [ifFalseLabel]))
        nodeOut += compileNode(node.iftrue, loopParent, parentLoopCondition)
        if node.iffalse != None:
            nodeOut.append(Command(0x36, [endLabel]))
        nodeOut.append(ifFalseLabel)
        if node.iffalse != None:
            nodeOut += compileNode(node.iffalse, loopParent, parentLoopCondition)
            nodeOut.append(endLabel)
    elif t == c_ast.Compound:
        for i in node.block_items:
            nodeOut += compileNode(i, loopParent, parentLoopCondition)
    elif t == c_ast.While:
        loopTop = Label()
        endLabel = Label()
        conditionLabel = Label()
        nodeOut.append(Command(0x4, [conditionLabel]))
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
        if name == "printf":
            for arg in node.args.exprs:
                nodeOut += compileNode(arg, loopParent, parentLoopCondition)
                addArg()
            nodeOut.append(Command(0x2c, [len(node.args.exprs)]))
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
            for arg in node.args.exprs:
                nodeOut += compileNode(arg, loopParent, parentLoopCondition)
                addArg()
            nodeOut += funcPtr
            nodeOut.append(Command(0x2f, [len(node.args.exprs)]))
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
    for node in func.body.block_items:
        script += compileNode(node)
    script.insert(0, Command(2, [argCount, len(localVars)]))
    script.append(Command(3))
    return script

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

def writeToFile(msc):
    global refs, args
    currentPos = 0x10
    for script in msc.scripts:
        currentPos += script.size()

    maxStringLength = 0
    for string in msc.strings:
        if len(string) > maxStringLength:
            maxStringLength = len(string)
    if maxStringLength % 0x10 != 0:
        maxStringLength += 0x10 - (maxStringLength % 0x10)

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

    for script in msc.scripts:
        for cmd in script:
            if type(cmd) == Command:
                for i in range(len(cmd.parameters)):
                    if type(cmd.parameters[i]) == float:
                        cmd.parameters[i] = struct.unpack('>L', struct.pack('>f', cmd.parameters[i]))[0]
                fileBytes += cmd.write()

    if len(fileBytes) % 0x10 != 0:
        fileBytes += b'\x00' * (0x10 - (len(fileBytes) % 0x10))

    for i in range(len(msc.scripts)):
        fileBytes += struct.pack('<L',refs.scriptPositions[i])

    if len(fileBytes) % 0x10 != 0:
        fileBytes += b'\x00' * (0x10 - (len(fileBytes) % 0x10))

    for string in msc.strings:
        fileBytes += string.encode('utf-8')
        fileBytes += b'\x00' * (maxStringLength - len(string))

    if len(fileBytes) % 0x10 != 0:
        fileBytes += b'\x00' * (0x10 - (len(fileBytes) % 0x10))

    filename = 'output.mscsb' if args.filename == None else args.filename
    with open(filename, 'wb') as f:
        f.write(fileBytes)

def compileString(fileText):
    global args, msc, refs
    parser = c_parser.CParser()
    text = removeComments(fileText)
    ast = parser.parse(text, filename='<none>')
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
        else:
            raise CompilerError("Error at %s: unsupported statement, structure or declaration. Use --ignore-invalid to avoid this error." % str(decl.coord))

    for decl in ast.ext:
        if isinstance(decl, c_ast.FuncDef):
            newScript = MscScript()
            newScript.cmds = compileScript(decl)
            msc.scripts.append(newScript)
    resolveReferences(msc)
    writeToFile(msc)

def compileFile(filepath):
    with open(filepath, 'r') as f:
        return compileString(f.read())

def main(arguments):
    global args
    args = arguments
    for file in args.files:
        b = compileFile(file)

if __name__ == "__main__":
    parser = ArgumentParser(description="Compile msC to MSC bytecode")
    parser.add_argument('files', metavar='files', type=str, nargs='+',
                        help='files to compile')
    parser.add_argument('-o', dest='filename', help='Filename to output to')
    main(parser.parse_args())