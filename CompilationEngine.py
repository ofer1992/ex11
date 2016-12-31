import Tokenizer
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from JackTokens import JackTokens as JTok


class CompilationEngine:
    path = ""
    tokenizer = Tokenizer(path)

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
                self.tokenizer.has_more_tokens()
                self.tokenizer.advance()
                self.compile_expression(SubElement(caller, "expression"))
                SubElement(caller, "symbol").text = self.tokenizer.symbol()
                self.tokenizer.has_more_tokens()
                self.tokenizer.advance()
            SubElement(caller, "symbol").text = self.tokenizer.symbol()

        elif type is JTok.IDENTIFIER:
            name = self.tokenizer.identifier()
            if not self.tokenizer.has_more_tokens():
                print("UNEXPECTED")
            self.tokenizer.advance()
            type = self.tokenizer.token_type
            if type is JTok.SYMBOL and self.tokenizer.symbol() == '.':
                subroutine = SubElement(caller, "subroutineCall")



