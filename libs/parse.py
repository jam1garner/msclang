from string import ascii_letters,digits

types = [
    "int",
    "float",
    "bool",
    "void"
]

constants = {
    "false"   : 0,
    "true"    : 1,
    "NULL"    : 0,
    "null"    : 0,
    "NULLPTR" : 0xFFFFFFFF,
    "PI"      : 0x40490FDB
}

controlFlowKeywords = [
    "if",
    "else",
    "while",
    "do",
    "for",
    "break",
    "return"
]

keywords = types + list(constants.keys()) + controlFlowKeywords

class TextBlock:
    validNameChars = list(ascii_letters + digits + '_')

    def __init__(self, text):
        self.children = []
        self.text = text
        self.readPosition = 0
        self.textLength = len(text)

    def readChar(self):
        if self.readPosition >= self.textLength:
            return None
        self.readPosition += 1
        return self.text[self.readPosition - 1]

    def readNext(self):
        if self.readPosition >= self.textLength:
            return None
        return self.text[self.readPosition]

    def eof(self):
        return self.readPosition >= self.textLength

    def readUntil(self,terminator):
        termPos = self.text.find(terminator, self.readPosition)
        if termPos == -1:
            return None
        readPos = self.readPosition
        self.readPosition = termPos
        return self.text[readPos:termPos]

    def readUntilClosed(self,start,end):
        pos = self.readPosition
        level = 1
        while self.readPosition < self.textLength:
            c = self.readChar()
            if c == end:
                level -= 1
            elif c == start:
                level += 1

            if level == 0:
                self.readPosition -= 1
                return self.text[pos:self.readPosition]
        return None

    def charCountUntil(self,terminator):
        termPos = self.text.find(terminator, self.readPosition)
        if termPos == -1:
            return None
        return termPos

    def skipWhitespace(self):
        while self.text[self.readPosition].isspace():
            self.readPosition += 1

    def skip(self,amt):
        self.readPosition += amt

    def readName(self):
        start = self.readPosition
        while self.readPosition < self.textLength:
            if not self.text[self.readPosition] in TextBlock.validNameChars:
                break
            self.readPosition += 1
        return self.text[start:self.readPosition]

    def readNumber(self):
        t = self.readName()
        try:
            return int(t, 0)
        except ValueError:
            try:
                #Cover leading 0 base 10 case
                return int(t)
            except ValueError:
                #Cover invalid number
                raise Exception('Invalid numeric literal "%s"'%t)

    def positionToLineNum(self,pos):
        return self.text[:pos].count('\n') + 1

class Variable:
    def __init__(self, varType=None, name=None, initialValue=None):
        self.type = varType
        self.name = name
        self.initialValue = initialValue

    def __str__(self):
        return "<Variable %s, type=%s, value=%s>" % (self.name,self.type,str(self.initialValue))

    def __repr__(self):
        return str(self)

class TwoValueOperation:
    def __init__(self, operation=None, value1=None, value2=None):
        self.operation = operation
        self.value1 = value1
        self.value2 = value2

class OneValueOperation:
    def __init__(self, operation=None, value1=None):
        self.operation = operation
        self.value1 = value1

class Label:
    def __init__(self, name=None):
        self.name = name

class Type:
    def __init__(self, typeName=None):
        self.typeName = typeName

class FunctionCall:
    def __init__(self, name=None, args=[]):
        self.name = name
        self.args = args

class Parenthesis:
    pass

singleCharOperation = ['+', '-', '*', '/', '%', '^', '|', '&', '>', '<', '=']
doubleCharOperation = {'+' : ['=', '+'], '-' : ['-', '='], '*' : ['='], '/' : ["="], '%' : ["="], '^' : ["="], '|' : ["="], '&' : ["="], '>' : [">", "="], '<' : ["<", "="], '=' : ['='], '!' : ['=']}

class Block(TextBlock):
    def __init__(self, blockText,  variables=[], statements=[]):
        super().__init__(blockText)
        self.statements = statements
        if blockText != "":
            self.read()

    def handleObject(obj):
        pass

    def readControlFlow(word):
        pass

    def readObject(self):
        c = self.readChar()
        if c == None:
            return None
        if c == ':':
            if type(self._currentObj) != str:
                raise Exception('Labels must have a proper name')
            name = self._currentObj
            self._currentObj = None
            return Label(name)
        if c in ['-', '!'] and self._currentObj == None:
            return OneValueOperation(c)
        if c in doubleCharOperation and self.readNext() in doubleCharOperation[c]:
            operation = c + self.readNext()
            if self._currentObj == None:
                raise Exception('Operation %s must be applied to an object' % operation)
            self._currentObj = TwoValueOperation(operation, self._currentObj)

        if c in ascii_letters:
            self.skip(-1)
            word = self.readName()
            if word in constants:
                self.handleObject(constants[word])
            elif word in types:
                self.handleObject(Type(word))
            elif word in controlFlowKeywords:
                self.readControlFlow(word)
            else:
                if _currentObj

        if c == '(':
            if isinstace(self._currentObj, TwoValueOperation):
                
                self._currentObj.value2 = 

        if c in digits:
            self.skip(-1)
            num = self.readNumber()
            self.handleObject(num)

        if c == ';':
            statements.append(self._currentObj)
            self._currentObj = None

    def read(self):
        while not self.eof():
            self.skipWhitespace()
            obj = self.readObject()
            if obj == None:
                break
            #do stuff with object here

class Function(Block):
    def __init__(self, varType, name, arguments=[], blockText="", variables=[], statements=[]):
        super().__init__(blockText, variables, statements)
        self.type = varType
        self.name = name
        self.arguments = arguments
        self.variables = variables
        
        self._currentObj = None

class TopBlock(TextBlock):
    def __init__(self, text):
        super().__init__(text)
        self.globalVariables = []
        self.functions = []
        self.read()

    def read(self):
        while not self.eof():
            self.skipWhitespace()
            
            c = self.readChar()
            if c == None:
                break

            if c.isalpha():
                self.skip(-1)
                varType = self.readName()
                if not varType in types:
                    raise Exception('Only global variable and function definitions are allowed in the highest block.')
                
                self.skipWhitespace()
                
                name = self.readName()
                if name[0].isdecimal():
                    raise Exception('Variable/Function names cannot start with a numeric digit.')
                if name in keywords:
                    raise Exception('Variable/Function name cannot be a keyword.')

                self.skipWhitespace()
                c = self.readChar()
                if c == None:
                    raise Exception('End of file reached mid variable/function declaration.')

                if c != "(" and c != ";":
                    raise Exception('Top level statements must be either a variable or function declaration. Variable declarations may not be assignments.')
                if c == "(":
                    #Function declaration
                    argumentText = self.readUntil(")")
                    if argumentText == None:
                        raise Exception('Function declaration arguments not closed')
                    argumentList = [i.rstrip(' ').lstrip(' ') for i in argumentText.split(",")]
                    
                    arguments = []
                    if argumentList != ['']:
                        for a in argumentList:
                            parts = [i for i in a.split(' ') if not (len(i) == 0 or i.isspace())]
                            
                            if len(parts) != 2:
                                raise Exception("All function declaration arguments should be in format '[type] [name]'")
                            if not parts[0] in types:
                                raise Exception("Type '%s' is not a valid type" % parts[0])
                            if parts[1] in keywords:
                                raise Exception("Function argument names cannot be '%s' (a reserved keyword)." % parts[1])
                            if parts[1][0].isdecimal():
                                raise Exception("Function argument name '%s' is not a valid name as variable names cannot start with a number." % parts[1])

                            arguments.append(Variable(parts[0], parts[1]))

                    self.skip(1)#Close parenthesis
                    self.skipWhitespace()
                    c = self.readChar()
                    if c == None:
                        raise Exception('End of file reached before function code block.')
                    if c != "{":
                        raise Exception('Function declaration must be followed by a code block.')
                    blockText = self.readUntilClosed("{","}")
                    if blockText == None:
                        raise Exception('End of file reached before function "%s" was closed' % name)
                    func = Function(varType, name, arguments, blockText)
                    print("\nNew function - type(%s), name('%s'), arguments: %s code:\n%s\n"%(varType,name,str(arguments),blockText))
                    self.functions.append(func)
                    self.skip(1)#Close code block "}"
                    
                if c == ";":
                    #Variable declaration
                    newVariable = Variable(varType, name)
                    print("New global variable - %s"%(str(newVariable)))
                    self.globalVariables.append(newVariable)
