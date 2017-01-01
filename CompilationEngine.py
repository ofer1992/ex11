from Tokenizer import Tokenizer
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from JackTokens import JackTokens as JTok


class CompilationEngine:
    path = ""
    tokenizer = Tokenizer(path)

    def next(self):
        if not self.tokenizer.has_more_tokens():
            print("UNEXPECTED")
        self.tokenizer.advance()

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
            SubElement(caller, "integerConstant").text = self.tokenizer.intVal()

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



