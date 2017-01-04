from Tokenizer import Tokenizer
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from JackTokens import JackTokens as JTok
from xml.etree import ElementTree
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

EXPRESSION = "expression"
SYMBOL = "symbol"
TERM = "term"
INTEGER_CONSTANT = "integerConstant"
STRING_CONSTANT = "stringConstant"
KEYWORD = "keyword"
IDENTIFIER = "identifier"
SUBROUTINE_CALL = "subroutineCall"

class CompilationEngine:
    operators = {'+':'+','-':'-', '*':'*', '/':'/','&':'&amp;','|':'|','<':'&lt;','>':'&gt;','=':'='}

    def __init__(self, source):  # TODO activate parsing?
        self.outFileName = source[:-5] + ".xml"
        self.outFile = open(self.outFileName, 'w')
        # Create Tokenizer
        self.tokenizer = Tokenizer(source)
        self.tokenizer.has_more_tokens()
        self.tokenizer.advance()
        # Close file stream

    def next(self):
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def is_op(self, symbol):
        return symbol in self.operators

    def compile_expression(self,caller):
        """
        Compiles an expression.
        :param caller:
        :return:
        """
        self.compile_term(SubElement(caller,TERM))
        while self.tokenizer.current_type is JTok.SYMBOL and self.is_op(self.tokenizer.symbol()):
            SubElement(caller,SYMBOL).text = self.operators[self.tokenizer.symbol()]
            self.next()
            self.compile_term(SubElement(caller,TERM))

    def compile_expressionList(self,caller):
        if (self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() == ")"):
            return
        self.compile_expression(SubElement(caller,EXPRESSION))
        while self.tokenizer.current_type is JTok.SYMBOL and self.tokenizer.symbol() == ",":
            SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
            self.next()
            self.compile_expression(SubElement(caller,EXPRESSION))

    def compile_subroutineCall(self,caller,first_token):
        """
        First token, the indentifier must be sent manually
        :param caller:
        :param first_token:
        :return:
        """
        SubElement(caller, 'identifier').text = first_token
        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
        if self.tokenizer.symbol() == '.':
            self.next()

            SubElement(caller, 'identifier').text = self.tokenizer.identifier()
            self.next()

            SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
        self.next()
        # if self.tokenizer.symbol() != ")":
        self.compile_expressionList(SubElement(caller, "expressionList"))
        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
        self.next()


    def compile_term(self,caller):
        type = self.tokenizer.token_type()
        if type is JTok.INT_CONST:
            SubElement(caller, INTEGER_CONSTANT).text = str(self.tokenizer.intVal())

        elif type is JTok.STRING_CONST:
            SubElement(caller, STRING_CONSTANT).text = self.tokenizer.string_val()

        elif type is JTok.KEYWORD:
            SubElement(caller, KEYWORD).text = self.tokenizer.key_word()

        elif type is JTok.IDENTIFIER:
            name = self.tokenizer.identifier()
            self.next()

            type = self.tokenizer.token_type()
            if type is JTok.SYMBOL and (self.tokenizer.symbol() == '.' or self.tokenizer.symbol() == "("):
                self.compile_subroutineCall(SubElement(caller, SUBROUTINE_CALL),name)
                return
            elif type is JTok.SYMBOL and self.tokenizer.symbol() == '[':
                SubElement(caller, IDENTIFIER).text = name
                SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
                self.next()
                self.compile_expression(SubElement(caller, EXPRESSION))
                SubElement(caller, SYMBOL).text = self.tokenizer.symbol()

            else:
                SubElement(caller, IDENTIFIER).text = name
                return

        elif type is JTok.SYMBOL:
            if self.tokenizer.symbol() == '(': #
                SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
                self.next()
                self.compile_expression(SubElement(caller, EXPRESSION))
                SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
            elif self.tokenizer.symbol() in {'-','~'}:
                SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
                self.next()
                self.compile_term(SubElement(caller,TERM))
                return
        self.next()

    def compile_do(self, caller):
        """
        format : 'do' subroutineCall ';'
        :param caller:
        :return:
        """

        SubElement(caller, 'keyword').text = self.tokenizer.key_word()
        self.next()

        name = self.tokenizer.identifier()
        self.next()

        self.compile_subroutineCall(SubElement(caller, 'subroutineCall'),name)

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set ';'
        self.next()

    def compile_let(self, caller):
        """
        format : 'let' varName ( '[' expression ']' )? '=' expression ';'
        :param caller:
        :return:
        """
        SubElement(caller, 'keyword').text = self.tokenizer.key_word()  # set 'let' as text
        self.next()

        SubElement(caller, 'identifier').text = self.tokenizer.identifier()  # varName
        self.next()

        if self.tokenizer.symbol() == '[':
            SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set '['
            self.next()

            self.compile_expression(SubElement(caller, 'expression'))

            SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set ']'
            self.next()

        # If there is no expression to compile:
        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set '='
        self.next()

        self.compile_expression(SubElement(caller, 'expression'))

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set ';'
        self.next()


    def compile_return(self, caller):
        """
        format : 'return' expression? ';'
        :param caller:
        :return:
        """
        SubElement(caller,KEYWORD).text = self.tokenizer.identifier()
        self.next()

        if self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() == ";":
            SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
            self.next()
            return

        self.compile_expression(SubElement(caller,EXPRESSION))
        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
        self.next()

    def compile_while(self, caller):
        """
        format : 'while' '(' expression ')' '{' statements '}'
        :param caller:
        :return:
        """
        SubElement(caller, 'keyword').text = self.tokenizer.key_word()  # set 'while' as text
        self.next()

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set '('
        self.next()

        self.compile_expression(SubElement(caller, 'expression'))

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set ')'
        self.next()

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set '{'
        self.next()

        self.compile_statements(SubElement(caller, 'statements'))

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set '}'
        self.next()


    def compile_statements(self, caller):
        """

        :param caller:
        :return:
        """
        STATEMENTS = {'do','while','let','return','if'}
        while(self.tokenizer.token_type() is JTok.KEYWORD and self.tokenizer.key_word() in STATEMENTS):
            if self.tokenizer.key_word() == 'do':
                self.compile_do(SubElement(caller, 'doStatement'))
            elif self.tokenizer.key_word() == 'while':
                self.compile_while(SubElement(caller, 'whileStatement'))
            elif self.tokenizer.key_word() == 'let':
                self.compile_let(SubElement(caller, 'letStatement'))
            elif self.tokenizer.key_word() == 'return':
                self.compile_return(SubElement(caller, 'returnStatement'))
            elif self.tokenizer.key_word() == 'if':
                self.compile_if(SubElement(caller, 'ifStatement'))

    def compile_if(self, caller):
        """
        format : 'if' '(' expression ')' '{' statements '}'
        ( 'else' '{' statements '}' )?
        :param caller:
        :return:
        """
        SubElement(caller,
                   'keyword').text = self.tokenizer.key_word()  # set 'if' as text
        self.next()

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set '('
        self.next()

        self.compile_expression(SubElement(caller, 'expression'))

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set ')'
        self.next()

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set '{'
        self.next()

        self.compile_statements(SubElement(caller, 'statements'))

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set '}'
        self.next()

        if self.tokenizer.token_type() is JTok.KEYWORD and self.tokenizer.key_word() == 'else':
            SubElement(caller,
                       'symbol').text = self.tokenizer.symbol()  # set '{'
            self.next()

            self.compile_statements(SubElement(caller, 'statements'))

            SubElement(caller,
                       'symbol').text = self.tokenizer.symbol()  # set '}'
            self.next()

    def compile_var_dec(self, caller):
        """
        format: 'var' type varName ( ',' varName)* ';'
        :param caller:
        :return:
        """

        SubElement(caller, 'keyword').text = self.tokenizer.key_word()  # set var as keyword
        self.next()

        self.compile_list_of_vars(caller)

    def compile_class(self):
        return

    def compile_list_of_vars(self,caller):
        """
        Helper method to compile lists of variables according to
        type varName (',' varName)*
        :param caller:
        :return:
        """
        self.compile_type(caller)

        SubElement(caller, 'identifier').text = self.tokenizer.identifier()  # set var name  as identifier
        self.next()

        while self.tokenizer.symbol() != ';':
            SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set ','
            self.next()

            SubElement(caller, 'identifier').text = self.tokenizer.identifier()  # set var name
            self.next()

        SubElement(caller, 'symbol').text = self.tokenizer.symbol()  # set ';'
        self.next()


    def compile_classVarDec(self,caller):
        """

        :param caller:
        :return:
        """
        SubElement(caller,KEYWORD).text = self.tokenizer.key_word()
        self.next()

        self.compile_list_of_vars(caller)



    def compile_type(self,caller):
        """
        Compiles a tag according to type, for variables
        :param caller:
        :return:
        """
        tag = KEYWORD if self.tokenizer.token_type() is JTok.KEYWORD else IDENTIFIER
        text = self.tokenizer.key_word() if tag is KEYWORD else self.tokenizer.identifier()
        SubElement(caller, tag).text = text
        self.next()

    def compile_subroutine(self,caller):
        return

    def compile_parameterList(self,caller):
        """

        :param caller:
        :return:
        """
        if self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() == ")":
            return

        self.compile_type(caller)

        SubElement(caller,IDENTIFIER).text = self.tokenizer.identifier()
        self.next()
        while self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() == ",":
            SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
            self.next()

            self.compile_type(caller)

            SubElement(caller, IDENTIFIER).text = self.tokenizer.identifier()
            self.next()



def main():
    tk = Tokenizer('Mytestfor10.jack')
    while(tk.has_more_tokens()):
        tk.advance()
        print(tk.token_type(),tk.current_token)
    ce = CompilationEngine('Mytestfor10.jack')
    root = Element('classVarDec')
    ce.compile_classVarDec(root)
    print()
    print(prettify(root))



if __name__ == main():
    main()