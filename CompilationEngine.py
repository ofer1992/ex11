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
        self.compile_expression(SubElement(caller,EXPRESSION))
        while self.tokenizer.current_type is JTok.SYMBOL and self.tokenizer.symbol() == ",":
            SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
            self.next()
            self.compile_expression(SubElement(caller,EXPRESSION))



    # def compile_return(self,caller):
    #     """
    #     'return' expression? ';'
    #     :return:
    #     """
    #     SubElement(caller,"keyword").text = self.tokenizer.identifier()
    #     self.next()
    #     if self.tokenizer.current_token is JTok.SYMBOL and self.tokenizer.symbol() == ';':
    #         SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
    #     else:
    #         self.compile_expression(SubElement(caller,EXPRESSION))
    #         SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
    #     self.next()

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
        if self.tokenizer.symbol() != ")":
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
            elif type is JTok.SYMBOL and self.tokenizer.symbol() == '[':
                SubElement(caller, IDENTIFIER).text = name
                SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
                self.next()
                self.compile_expression(SubElement(caller, EXPRESSION))
                SubElement(caller, SYMBOL).text = self.tokenizer.symbol()

            else:
                SubElement(caller, IDENTIFIER).text = name

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
        self.next()

    def compile_do(self, caller):
        """
        format : 'do' subroutineCall ';'
        :param caller:
        :return:
        """

        node = SubElement(caller, 'doStatement')  # set sub root tag
        node.text = self.tokenizer.current_token

        self.next()

        child = SubElement(node, 'keyword')
        child.text = self.tokenizer.current_token  # set 'do' as text

        self.next()
        name = self.tokenizer.identifier()
        self.next()
        self.compile_subroutineCall(node,name)

        g1_child = SubElement(node, 'symbol')  # set ';'
        g1_child.text = self.tokenizer.current_token

        self.next()

    def compile_let(self, caller):
        """
        format : 'let' varName ( '[' expression ']' )? '=' expression ';'
        :param caller:
        :return:
        """
        node = SubElement(caller, 'letStatement')  # set sub root tag
        node.text = self.tokenizer.current_token

        self.next()

        child = SubElement(node, 'keyword')
        child.text = self.tokenizer.current_token  # set 'let' as text

        self.next()

        g1_child = SubElement(node, 'identifier')
        g1_child.text = self.tokenizer.current_token  # varName

        self.next()

        if self.tokenizer.current_token == '[':
            g2_child = SubElement(node, 'symbol')  # set '['
            g2_child.text = self.tokenizer.current_token
            self.next()
            self.compile_expression(node)
            g3_child = SubElement(node, 'symbol')  # set ']'
            g3_child.text = self.tokenizer.current_token
            self.next()

        g2_child = SubElement(node, 'symbol')  # set '='
        g2_child.text = self.tokenizer.current_token
        self.next()

        self.compile_expression(node)

        g3_child = SubElement(node, 'symbol')  # set ';'
        g3_child.text = self.tokenizer.current_token

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
        node = SubElement(caller, 'whileStatement')  # set sub root tag
        node.text = self.tokenizer.current_token
        self.next()

        child = SubElement(node, 'keyword')
        child.text = self.tokenizer.current_token  # set 'while' as text

        g1_child = SubElement(node, 'symbol')  # set '('
        g1_child.text = self.tokenizer.current_token
        self.next()

        self.compile_expression(node)

        g2_child = SubElement(node, 'symbol')  # set ')'
        g2_child.text = self.tokenizer.current_token
        self.next()

        g3_child = SubElement(node, 'symbol')  # set '{'
        g3_child.text = self.tokenizer.current_token
        self.next()

        self.compile_statements(node)

        g3_child = SubElement(node, 'symbol')  # set '}'
        g3_child.text = self.tokenizer.current_token
        self.next()

    def compile_statements(self, caller):
        """

        :param caller:
        :return:
        """
        node = SubElement(caller, 'statement')  # set sub root tag
        node.text = self.tokenizer.current_token
        self.next()

        if self.tokenizer.current_token == 'do':
            self.compile_do(node)
        elif self.tokenizer.current_token == 'while':
            self.compile_while(node)
        elif self.tokenizer.current_token == 'let':
            self.compile_let(node)
        elif self.tokenizer.current_token == 'return':
            self.compile_return(node)
        elif self.tokenizer.current_token == 'if':
            self.compile_if(node)

    def compile_if(self, caller):
        """
        format : 'if' '(' expression ')' '{' statements '}'
        ( 'else' '{' statements '}' )?
        :param caller:
        :return:
        """
        node = SubElement(caller, 'ifStatement')  # set sub root tag
        node.text = self.tokenizer.current_token
        self.next()

        child = SubElement(node, 'keyword')
        child.text = self.tokenizer.current_token  # set 'if' as text

        g1_child = SubElement(node, 'symbol')  # set '('
        g1_child.text = self.tokenizer.current_token
        self.next()

        self.compile_expression(node)

        g2_child = SubElement(node, 'symbol')  # set ')'
        g2_child.text = self.tokenizer.current_token
        self.next()

        g3_child = SubElement(node, 'symbol')  # set '{'
        g3_child.text = self.tokenizer.current_token
        self.next()

        self.compile_statements(node)

        g3_child = SubElement(node, 'symbol')  # set '}'
        g3_child.text = self.tokenizer.current_token
        self.next()

        if self.tokenizer.current_token == 'else':
            g4_child = SubElement(node, 'symbol')  # set '{'
            g4_child.text = self.tokenizer.current_token
            self.next()

            self.compile_statements(node)

            g4_child = SubElement(node, 'symbol')  # set '}'
            g4_child.text = self.tokenizer.current_token
            self.next()


    def compile_var_dec(self, caller):
        """
        format: 'var' type varName ( ',' varName)* ';'
        :param caller:
        :return:
        """

        node = SubElement(caller, 'keyword')  # set 'var' as first tag
        node.text = self.tokenizer.current_token

        self.next()

        child = SubElement(node, 'keyword')
        child.text = self.tokenizer.current_token  # type

        self.next()

        g1_child = SubElement(node, 'identifier')
        g1_child.text = self.tokenizer.current_token  # varName

        self.next()

        while self.tokenizer.current_token is not ';':
            if self.tokenizer.current_token is ',':
                g2_child = SubElement(node, 'symbol')  # set ','
                g2_child.text = self.tokenizer.current_token

                self.next()
            else:  # it means its another var name
                g3_child = SubElement(node, 'identifier')
                g3_child.text = self.tokenizer.current_token  # varName

                self.next()

        g4_child = SubElement(g1_child, 'symbol')  # set ';'
        g4_child.text = self.tokenizer.current_token
        self.next()


def main():
    tk = Tokenizer('Mytestfor10.jack')
    while(tk.has_more_tokens()):
        tk.advance()
        print(tk.token_type(),tk.current_token)
    ce = CompilationEngine('Mytestfor10.jack')
    root = Element('returnStatment')
    ce.compile_return(root)
    print()
    print(prettify(root))



if __name__ == main():
    main()