from msc import *
from argparse import ArgumentParser
from pycparser import c_parser, c_ast, parse_file
import re
import math

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
    "|"  : 0x17,
    "^"  : 0x19,
    "<<" : 0x1a,
    ">>" : 0x1b
}

floatOperations = list(range(0x3a,0x46)) + [0x38]

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

def compileNode(node):
    global refs, localVars, localVarTypes, depth
    if not isinstance(node, c_ast.Node):
        raise ValueError("That's no node")

    depth += 1
    nodeOut = []

    def addArgs(amt=1):
        if len(nodeOut) >= amt:
            for i in range(amt):
                nodeOut[-(i+1)].pushBit = True

    t = type(node)

    if t == c_ast.Decl:
        if not node.name in localVars:
            localVarNum = len(localVars)
            localVars.append(node.name)
            localVarTypes[node.name] = node.type.type.names[-1]
        else:
            localVarNum = localVars.index(node.name)

        if node.init != None:
            nodeOut += compileNode(node.init)
            addArgs()
            nodeOut.append(Command(0x1C, [0, localVarNum]))
    elif t == c_ast.Constant:
        if node.type == "int" or node.type == "bool":
            newValue = toInt(node.value) & 0xFFFFFFFF
            nodeOut.append(Command(0xD if newValue <= 0xFFFF else 0xA, [newValue]))
        elif node.type == "float":
            nodeOut.append(Command(0xA, [float(node.value.rstrip('f'))]))
        elif node.type == "string":
            if not node.value in msc.strings:
                msc.strings.append(node.value)
            nodeOut.append(Command(0xD, [msc.strings.index(node.value)]))
    elif t == c_ast.Assignment:
        nodeOut += compileNode(node.rvalue)
        addArgs()
        if type(node.lvalue) != c_ast.ID:
            raise CompilerError("Error at %s: Left hand side of assignment operation must be variable."%str(node.coord))
        try:
            varScope,varType,varIndex = resolveVariable(node.lvalue.name)
        except CompilerError:
            raise CompilerError("Error at %s: Left hand side of assignment operation must be a valid reference to a variable."%str(node.coord))
        
        if varType == "float":
            operation = assignmentOperationsFloat[node.op]
        else:
            operation = assignmentOperationsInt[node.op]
        nodeOut.append(Command(operation,[varScope,varIndex]))
    elif t == c_ast.UnaryOp:
        if node.op == "!":
            nodeOut += compileNode(node.expr)
            addArgs()
            nodeOut.append(Command(0x2b))
        elif node.op == "~":
            nodeOut += compileNode(node.expr)
            addArgs()
            nodeOut.append(Command(0x18))
        elif node.op == "p++":
            if type(node.expr) != c_ast.ID:
                CompilerError("Error at %s: Cannot increment non variable."%str(node.coord))
            varScope,varType,varIndex = resolveVariable(node.expr.name)
            op = 0x3F if varType == "float" else 0x14
            nodeOut.append(Command(op, [varScope,varIndex], False))
        elif node.op == "p--":
            if type(node.expr) != c_ast.ID:
                CompilerError("Error at %s: Cannot decrement non variable."%str(node.coord))
            varScope,varType,varIndex = resolveVariable(node.expr.name)
            op = 0x40 if varType == "float" else 0x15
            nodeOut.append(Command(op, [varScope,varIndex], False))
        elif node.op == "-":
            nodeOut += compileNode(node.expr)
            addArgs()
            op = 0x3E if isCommandFloat(nodeOut[-1]) else 0x13
            nodeOut.append(Command(op))
        elif node.op == "&":
            if type(node.expr) == c_ast.ID:
                nodeOut.append(Command(0xA,[node.expr.name]))
            else:
                raise CompilerError("Error at %s: The addressing of non-functions is not allowed."%str(node.coord))
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
        nodeOut += compileNode(node.expr)
        addArgs()
        if node.to_type.type.type.names[-1] == "float":
            nodeOut.append(Command(0x38))
        else:
            nodeOut.append(Command(0x39))
    elif t == c_ast.Return:
        if node.expr == None:
            nodeOut.append(Command(0x7))
        else:
            nodeOut += compileNode(node.expr)
            addArgs()
            op = 0x8 if isCommandFloat(nodeOut[-1]) else 0x6
            nodeOut.append(Command(op))
    elif t == c_ast.BinaryOp:
        nodeOut += compileNode(node.left)
        addArgs()
        pos = len(nodeOut)
        isFloat1 = isCommandFloat(nodeOut[-1])
        nodeOut += compileNode(node.right)
        addArgs()
        isFloat2 = isCommandFloat(nodeOut[-1])
        isFloat = isFloat1 or isFloat2
        cmd = binaryOperationsFloat[node.op] if isFloat else binaryOperationsInt[node.op]
        if not cmd in range(0x16, 0x1C) and isFloat:
            if not isFloat1:
                nodeOut.insert(pos, Command(0x38))
            if not isFloat2:
                nodeOut.append(Command(0x38))
        nodeOut.append(Command(cmd))
    else:
        node.show()
        print(node)
        print(node.__slots__)
        print()

    return nodeOut

def compileScript(func):
    global msc, refs, localVars, localVarTypes, depth
    localVars = [x.name for x in func.decl.type.args.params] if func.decl.type.args != None else []
    localVarTypes = dict([(x.name, x.type.type.names[-1]) for x in func.decl.type.args.params] if func.decl.type.args != None else [])
    argCount = len(localVars)
    script = []
    for node in func.body.block_items:
        depth = -1
        script += compileNode(node)
    script.insert(0, Command(2, [argCount, len(localVars)]))
    script.append(Command(3))
    for i in script:
        print(i)
    return script

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
            compileScript(decl)

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
    main(parser.parse_args())