import ply.yacc as yacc
from tabulate import tabulate
from lex import tokens


# AST
class Expr: pass


class BinOp(Expr):
    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op


class Number(Expr):
    def __init__(self, value, type=None):
        self.value = value
        self.type = type


class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = []
        self.leaf = leaf
        self.type = None
        self.scope_variables = set()


def p_prog(p):
    """prog : buildClassOrFunc"""
    p[0] = p[1]


# buildClassOrFunc
def p_buildClassOrFunc(p):
    """buildClassOrFunc : classDecl
    | funcDef"""
    p[0] = p[1]


# class declaration
def p_classDecl(p):
    """classDecl : CLASS ID LEFTBRACE visibilityMemberDeclArr RIGHTBRACE """
    p[0] = ('class', p[2], p[4])


# visibilityMemberDeclArr
def p_visibilityMemberDeclArr(p):
    """visibilityMemberDeclArr : visibilityMemberDecl visibilityMemberDeclArr
    | """
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


# visibilityMemberDecl
def p_visibilityMemberDecl(p):
    """visibilityMemberDecl : visibility memberDecl"""
    p[0] = (p[1], p[2])


# visibility
def p_visibility(p):
    """visibility : PUBLIC
    | PRIVATE
    | """
    if len(p) > 1:
        p[0] = p[1]
    else:
        p[0] = ''


# member declaration
def p_memberDecl(p):
    """memberDecl : memberFuncDecl
    | memberVarDecl"""
    p[0] = p[1]


# member function declaration
def p_memberFuncDecl(p):
    """memberFuncDecl : FUNCTION ID COLON LEFTPARENTHESES fParams RIGHTPARENTHESES ARROW returnType SEMICOLON
    | CONSTRUCTOR COLON LEFTPARENTHESES fParams RIGHTPARENTHESES SEMICOLON"""
    if p[1] == 'constructor':
        p[0] = Node('constructor', children=[p[6]])
    else:
        p[0] = Node('function', children=[Node(p[2]), p[5], p[9]])


#  member variable declaration
def p_memberVarDecl(p):
    """memberVarDecl : ATTRIBUTE ID COLON type arraySizeArr SEMICOLON"""
    p[0] = ('attribute', p[2], p[4], p[5])


# array size array
def p_arraySizeArr(p):
    """arraySizeArr : arraySize arraySizeArr
    | """
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


# function definition
def p_funcDef(p):
    """funcDef : funcHead funcBody"""
    p[0] = ('function_def', p[1], p[2])


# funcHead
def p_funcHead(p):
    """funcHead : FUNCTION idsrArr ID LEFTPARENTHESES fParams RIGHTPARENTHESES ARROW returnType
    | FUNCTION ID SR CONSTRUCTOR LEFTPARENTHESES fParams RIGHTPARENTHESES"""
    if p[4] == 'constructor':
        p[0] = ('funcHead', 'constructor', p[6])
    else:
        p[0] = ('funcHead', p[3], p[5], p[8])


# idsrArr
def p_idsrArr(p):
    """idsrArr : ID SR idsrArr
    | """
    if len(p) > 1:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = []


# funcBody
def p_funcBody(p):
    """funcBody : LEFTBRACKET localVarDeclOrStmtArr RIGHTBRACKET"""
    p[0] = p[2]


# localVarDeclOrStmt array
def p_localVarDeclOrStmtArr(p):
    """localVarDeclOrStmtArr : localVarDeclOrStmt localVarDeclOrStmtArr
    | """
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


# localVarDeclOrStmt
def p_localVarDeclOrStmt(p):
    """localVarDeclOrStmt : localVarDecl
    | statement"""
    p[0] = p[1]


# localVarDecl
def p_localVarDecl(p):
    """localVarDecl : LOCALVAR ID COLON type arraySizeArr SEMICOLON
    | LOCALVAR ID COLON type LEFTPARENTHESES aParams RIGHTPARENTHESES SEMICOLON"""
    if len(p) == 6:
        p[0] = Node('localVar', children=[Node(p[2]), Node(p[4]), p[5]])
    else:
        p[0] = Node('localVar', children=[Node(p[2]), Node(p[4]), p[6]])


# statement
def p_statement(p):
    """statement : assignStat SEMICOLON
    | IF LEFTPARENTHESES relExpr RIGHTPARENTHESES THEN statBlock ELSE statBlock SEMICOLON
   | WHILE LEFTPARENTHESES relExpr RIGHTPARENTHESES statBlock SEMICOLON
   | READ LEFTPARENTHESES variable RIGHTPARENTHESES SEMICOLON
   | WRITE LEFTPARENTHESES expr RIGHTPARENTHESES SEMICOLON
   | RETURN LEFTPARENTHESES expr RIGHTPARENTHESES SEMICOLON
   | functionCall SEMICOLON"""
    p[0] = p[1] if len(p) == 2 else (p[1], p[3]) if len(p) == 4 else (p[1], p[3], p[5], p[7]) if len(p) == 8 else (
        p[1], p[2], p[4]) if p[1] == 'if' or p[1] == 'while' else (p[1], p[3], p[5], p[8])


# assign statement
def p_assignStat(p):
    """assignStat : variable ASSIGN expr"""
    p[0] = ('assign', p[1], p[3])


# statement block
def p_statBlock(p):
    """statBlock : LEFTBRACE statementArr RIGHTBRACE
    | statement"""
    if len(p) == 4:
        p[0] = Node('statBlock', children=p[2])
    else:
        p[0] = Node('statBlock', children=[p[1]])


# statement array
def p_statementArr(p):
    """statementArr : statement statementArr
    | """
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


# expression
def p_expr(p):
    """expr : arithExpr
    | relExpr"""
    p[0] = p[1]


# relational expression
def p_relExpr(p):
    """relExpr : arithExpr relOp arithExpr"""
    p[0] = (p[2], p[1], p[3])


# arithmetic expression
def p_arithExpr(p):
    """arithExpr : term arithExprtail"""
    p[0] = p[1] + p[2]


# arithmetic expression tail
def p_arithExprtail(p):
    """arithExprtail : addOp term arithExprtail
    | """
    if len(p) > 2:
        p[0] = (p[1], p[2], p[3])
    else:
        p[0] = ''


# term
def p_term(p):
    """term : factor termTail"""
    p[0] = p[1] + p[2]


# term tail
def p_termTail(p):
    """termTail : multOp factor termTail
    | """
    if len(p) > 2:
        p[0] = (p[1], p[2], p[3])
    else:
        p[0] = ''


# Rule for factor
def p_factor(p):
    """factor : variable
    | functionCall
    | INTLIT
    | FLOATLIT
    | LEFTPARENTHESES arithExpr RIGHTPARENTHESES
    | NOT factor
    | sign factor"""
    if p[1] == '(':
        p[0] = p[2]
    elif len(p) > 2:
        p[0] = (p[1], p[2])
    else:
        p[0] = p[1]


# variable
def p_variable(p):
    """variable : idnestArr ID indiceArr"""
    p[0] = (p[2], p[1], p[3])


# idnestArr
def p_idnestArr(p):
    """idnestArr : idnest indiceArr
    | """
    if len(p) > 1:
        p[0] = (p[1], p[2])
    else:
        p[0] = ''


# indiceArr
def p_indiceArr(p):
    """indiceArr : indice indiceArr
    | """
    if len(p) > 1:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = ''


# function call
def p_functionCall(p):
    """functionCall : idnestArr ID LEFTPARENTHESES aParams RIGHTPARENTHESES"""
    p[0] = (p[1], p[2], p[4])


# indices
def p_indice(p):
    """indice : LEFTBRACE arithExpr RIGHTBRACE"""
    p[0] = p[2]


# return type
def p_returnType(p):
    """returnType : type
    | VOID"""
    p[0] = Node('returnType', children=[Node(p[1])])


# function parameters
def p_fParams(p):
    """fParams : ID COLON type arraySizeArr fParamsTailArr
    | """
    if len(p) > 2:
        p[0] = (p[1], p[3], p[4], p[5])
    else:
        p[0] = ''


# function parameters tail
def p_fParamsTailArr(p):
    """fParamsTailArr : fParamsTail fParamsTailArr
    | """
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = ''


# additional parameters in function call
def p_aParams(p):
    """aParams : expr aParamsTailArr
    | """
    if len(p) > 1:
        p[0] = (p[1], p[2])
    else:
        p[0] = ''


# additional parameters tail in function call
def p_aParamsTailArr(p):
    """aParamsTailArr : expr aParamsTailArr
    | """
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = ''


# relational operators
def p_relOp(p):
    """relOp : EQ
    | NEQ
    | LT
    | GT
    | LEQ
    | GEQ"""
    p[0] = p[1]


# additive operators
def p_addOp(p):
    """addOp : ADD
    | SUB
    | OR"""
    p[0] = p[1]


# multiplicative operators
def p_multOp(p):
    """multOp : MUL
    | DIV
    | AND"""
    p[0] = p[1]


# type
def p_type(p):
    """type : INTEGER
    | FLOAT
    | ID"""
    p[0] = p[1]


# array size
def p_arraySize(p):
    """arraySize : LEFTBRACE INTLIT RIGHTBRACE
    | LEFTBRACE RIGHTBRACE"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = ''


# sign
def p_sign(p):
    """sign : ADD
    | SUB"""
    p[0] = p[1]


# idnest
def p_idnest(p):
    """idnest : ID idnestTail"""
    if len(p) > 2:
        p[0] = (p[1], p[2])
    else:
        p[0] = p[1]


# idnestTail
def p_idnestTail(p):
    """idnestTail :
    | LEFTBRACE arithExpr RIGHTBRACE idnestTail
    | LEFTPARENTHESES aParams RIGHTPARENTHESES idnestTail
    | DOT"""
    if len(p) == 2:
        p[0] = ''
    elif len(p) == 4:
        p[0] = p[2] + p[3]
    else:
        p[0] = p[1] + p[2] + p[3] + p[4]


# fParamsTail
def p_fParamsTail(p):
    """fParamsTail : COMMA ID COLON type arraySizeArr fParamsTail
    | """
    if len(p) > 2:
        p[0] = [(p[2], p[4], p[5])] + p[6]
    else:
        p[0] = []


# empty production
def p_empty(p):
    """ empty : """
    pass


# syntax errors
def p_error(p):
    if p:
        print(f"Syntax error at {p.value}, line {p.lineno}, position {p.lexpos}")
    else:
        print("Syntax error at EOF")


# Build the parser
parser = yacc.yacc()



# Print Symbol Table
f = open('Test1.txt', 'r')
program = f.read()

result = parser.parse(program)


# Print Symbol Table
def print_ast(node, indent=0):
    if isinstance(node, Node):
        print("  " * indent + f"{node.type}")
        for child in node.children:
            print_ast(child, indent + 1)
    elif isinstance(node, BinOp):
        print("  " * indent + f"BinOp: {node.op}")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    elif isinstance(node, Number):
        print("  " * indent + f"Num: {node.value}")


print_ast(result)


def check_variable_declaration(node, current_scope):
    if node.type == 'localVar':
        variable_name = node.children[0].leaf
        if variable_name in current_scope:
            print(f"Error: Variable '{variable_name}' already declared in the current scope.")
        else:
            current_scope.add(variable_name)
            node.type = node.children[1].type  # Set the variable type in the AST node


def check_variable_usage(node, current_scope):
    if node.type == 'variable':
        variable_name = node.children[0].leaf
        if variable_name not in current_scope:
            print(f"Error: Variable '{variable_name}' used before declaration.")
        else:
            # Set the variable type in the AST node
            node.type = current_scope[variable_name]


def check_class_instantiation(node, current_scope):
    if node.type == 'class':
        class_name = node.children[0].leaf
        if class_name not in current_scope:
            print(f"Error: Class '{class_name}' used before declaration.")
        else:
            node.type = class_name


def check_function_declaration(node, current_scope):
    if node.type == 'function':
        function_name = node.children[0].leaf
        if function_name not in current_scope:
            print(f"Error: Function '{function_name}' is already declared.")
        else:
            node.type = function_name


def check_attribute_declaration(node, current_scope):
    if node.type == 'attribute':
        attribute_name = node.children[0].leaf
        if attribute_name not in current_scope:
            print(f"Error: Attribute '{attribute_name}' is already declared.")
        else:
            node.type = attribute_name


def perform_semantic_analysis(node, current_scope=None):
    if current_scope is None:
        current_scope = set()

    if isinstance(node, Node):
        for child in node.children:
            perform_semantic_analysis(child, current_scope.copy())

        # Perform specific semantic checks based on node type
        if node.type == 'localVar':
            check_variable_declaration(node, current_scope)
        elif node.type == 'variable':
            check_variable_usage(node, current_scope)
        elif node.type == 'class':
            check_class_instantiation(node, current_scope)
        elif node.type == 'attribute':
            check_attribute_declaration(node, current_scope)
        elif node.type == 'function':
            check_function_declaration(node, current_scope)


perform_semantic_analysis(result)
