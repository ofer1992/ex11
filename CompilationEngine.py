from Tokenizer import Tokenizer
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from JackTokens import JackTokens as JTok


class CompilationEngine:

    operators = {'+':'+','-':'-','/':'/','&':'&amp;','|':'|','<':'&lt;','>':'&gt;','=':'='}

    def __init__(self, source):  # TODO activate parsing?
        self.outFileName = source[:-5] + ".xml"
        self.outFile = open(self.outFileName, 'w')
        # Create Tokenizer
        self.tokenizer = Tokenizer(source)
        self.tokenizer.has_more_tokens()
        self.tokenizer.advance()
        # Close file stream

    def next(self):
        if not self.tokenizer.has_more_tokens():
            print("UNEXPECTED")
        self.tokenizer.advance()

    def is_op(self, symbol):
        return symbol in self.operators

    def compile_expression(self,caller):
        """

        :param caller:
        :return:
        """
        self.compile_term(caller)
        while self.tokenizer.current_type is JTok.SYMBOL and self.is_op(self.tokenizer.symbol()):
            SubElement(caller,"symbol").text = self.operators[self.tokenizer.symbol()]
            self.next()
            self.compile_term(caller)
        self.next()


    def compile_return(self,caller):
        """
        'return' expression? ';'
        :return:
        """
        SubElement(caller,"keyword").text = self.tokenizer.identifier()
        self.next()
        if self.tokenizer.current_token is JTok.SYMBOL and self.tokenizer.symbol() == ';':
            SubElement(caller, "symbol").text = self.tokenizer.symbol()
        else:
            self.compile_expression(SubElement(caller,"expression"))
            SubElement(caller, "symbol").text = self.tokenizer.symbol()
        self.next()

    def compile_subroutineCall(self,caller,first_token):
        """
        First token, the indentifier must be sent manually
        :param caller:
        :param first_token:
        :return:
        """
        SubElement(caller, 'identifier').text = first_token
        SubElement(caller, "symbol").text = self.tokenizer.symbol()
        if self.tokenizer.symbol() == '.':
            self.next()

            SubElement(caller, 'identifier').text = self.tokenizer.identifier()
            self.next()

            SubElement(caller,"symbol").text = self.tokenizer.symbol()
        self.next()

        self.compile_expressionList(SubElement(caller, "expressionList"))
        SubElement(caller, "symbol").text = self.tokenizer.symbol()
        self.next()


    def compile_term(self,caller):
        type = self.tokenizer.token_type()
        if type is JTok.INT_CONST:
            SubElement(caller, "integerConstant").text = str(self.tokenizer.intVal())

        elif type is JTok.STRING_CONST:
            SubElement(caller, "stringConstant").text = self.tokenizer.string_val()

        elif type is JTok.KEYWORD:
            SubElement(caller, "keyword").text = self.tokenizer.key_word()

        elif type is JTok.SYMBOL:
            if self.tokenizer.symbol == '(': #
                SubElement(caller, "symbol").text = self.tokenizer.symbol()
                self.next()

                self.compile_expression(SubElement(caller, "expression"))
                SubElement(caller, "symbol").text = self.tokenizer.symbol()
                self.next()

            SubElement(caller, "symbol").text = self.tokenizer.symbol()

        elif type is JTok.IDENTIFIER:
            name = self.tokenizer.identifier()
            self.next()

            type = self.tokenizer.token_type
            if type is JTok.SYMBOL and self.tokenizer.symbol() == '.':
                self.compile_subroutineCall(SubElement(caller, "subroutineCall"),name)
            elif type is JTok.SYMBOL and self.tokenizer.symbol() == '[':
                SubElement(caller, "symbol").text = self.tokenizer.symbol()
                self.next()

                self.compile_expression(SubElement(caller, "expression"))
                SubElement(caller, "symbol").text = self.tokenizer.symbol()
                self.next()

            else:
                SubElement(caller, "identifier").text = name


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
    ce = CompilationEngine('Mytestfor10.jack')
    root = Element('someroot')
    ce.compile_term(root)
    print(tostring(root))



if __name__ == main():
    main()