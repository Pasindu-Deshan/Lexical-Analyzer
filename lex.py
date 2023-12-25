import ply.lex as lex
from tabulate import tabulate

# Reserved keywords
reserved = {
    'class': 'CLASS',
    'isa': 'ISA',
    'public': 'PUBLIC',
    'private': 'PRIVATE',
    'function': 'FUNCTION',
    'constructor': 'CONSTRUCTOR',
    'attribute': 'ATTRIBUTE',
    'integer': 'INTEGER',
    'float': 'FLOAT',
    'void': 'VOID',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'read': 'READ',
    'write': 'WRITE',
    'return': 'RETURN',
    'not': 'NOT',
    'or': 'OR',
    'and': 'AND',
    'localVar': 'LOCALVAR',
    'sr': 'SR',
    'arrow': 'ARROW',
    'type': 'TYPE',
    'id': 'ID'
}

# List of token names. This is always required
tokens = [
             'EQ',
             'NEQ',
             'LT',
             'GT',
             'LEQ',
             'GEQ',
             'ADD',
             'SUB',
             'MUL',
             'DIV',
             'ASSIGN',
             'COMMA',
             'SEMICOLON',
             'COLON',
             'LEFTPARENTHESES',
             'RIGHTPARENTHESES',
             'LEFTBRACKET',
             'RIGHTBRACKET',
             'RIGHTBRACE',
             'LEFTBRACE',
             'DOT',
             'EPSILON',
             'INTLIT',
             'FLOATLIT'
         ] + list(reserved.values())

# Regular expression rules for simple tokens
t_ADD = r'\+'
t_SUB = r'\-'
t_MUL = r'\*'
t_DIV = r'/'
t_LEFTPARENTHESES = r'\('
t_RIGHTPARENTHESES = r'\)'
t_EQ = r'=='
t_NEQ = r'!='
t_LT = r'<'
t_GT = r'>'
t_LEQ = r'<='
t_GEQ = r'>='
t_ASSIGN = r'='
t_COMMA = r','
t_SEMICOLON = r';'
t_COLON = r':'
t_LEFTBRACKET = r'\['
t_RIGHTBRACKET = r'\]'
t_LEFTBRACE = r'{'
t_RIGHTBRACE = r'}'
t_DOT = r'\.'
t_EPSILON = r'\ '


# A regular expression rule for FLOATLIT
def t_FLOATLIT(t):
    r'\d+\.\d*|\d*\.\d+'
    t.value = float(t.value)
    return t


# A regular expression rule with some action code
def t_INTLIT(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore_COMMENT = r'\#.*'

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Test File
f = open('Test1.txt', 'r')
program = f.read()

lexer.input(program)

# Print

# Store tokens in a list
tokens_list = []

while True:
    tok = lexer.token()
    if not tok:
        break
    tokens_list.append((tok.type, tok.value, tok.lineno, tok.lexpos))

# Print as a table
headers = ["Token Type", "Value", "Line Number", "Lexical Position"]
print(tabulate(tokens_list, headers=headers, tablefmt="grid"))
