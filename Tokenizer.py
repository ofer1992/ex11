import re
from JackTokens import JackTokens as JTok
from xml.etree.ElementTree import Element, SubElement, Comment, tostring


class Tokenizer:
    """

    """
    word_pat = re.compile(r'[a-zA-Z_][\w_]*')
    int_pat = re.compile(r'\d+')
    str_pat = re.compile(r'^\".*\"$')
    KEYWORDS = {'class','constructor','function','method','field','static','var','int','char','boolean',
                'void','true','false','null','this','let','do','if','else','while','return'}
    SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&','|',
               '<', '>', '=', '-', '~'}

    def __init__(self, file_path):
        self.file = open(file_path)
        self.char = ''
        self.peek = self.file.read(1)
        self.current_token = None
        self.current_type = None

    def next_char(self): #TODO: Add buffer?
        """
        Reads next char in file.
        :return:
        """
        self.char = self.peek
        self.peek = self.file.read(1)

    def advance(self):#
        """
        Gets the next token from the input
        and makes it the current token. This
        method should only be called if
        hasMoreTokens() is true. Initially
        there is no current token.
        :return:
        """
        if self.char.isalpha(): # keyword or identifier
            self.current_token = self.char
            while (self.peek not in self.SYMBOLS) and (not self.peek.isspace() and (self.peek != '')):
                self.next_char()
                self.current_token += self.char
            self.current_type = JTok.KEYWORD if self.current_token in self.KEYWORDS else JTok.IDENTIFIER

        elif self.char in self.SYMBOLS: # symbol
            self.current_token = self.char
            self.current_type = JTok.SYMBOL

        elif self.char == "\"": # string constant
            self.current_token = self.char
            self.next_char()
            while self.char != "\"":
                self.current_token += self.char
                self.next_char()
            self.current_token += self.char
            self.current_type = JTok.STRING_CONST

        elif self.char.isdigit(): # int constant
            self.current_token = self.char
            while self.peek.isdigit():
                self.next_char()
                self.current_token += self.char
            self.current_type = JTok.INT_CONST

    def has_more_tokens(self):
        """
        Do we have more tokens in the input?
        :return:
        """
        if self.peek == '':
            return False
        if self.peek == '/':
            self.next_char()
            if self.peek == '/':
                while self.char != '\n':
                    self.next_char()
            elif self.peek == "*":
                self.next_char()
                self.next_char()
                while not (self.char == '*' and self.peek == '/'):
                    self.next_char()
                self.next_char()
            else:
                return True
            return self.has_more_tokens()
        if self.peek.isspace():
            while self.peek.isspace():
                self.next_char()
            return self.has_more_tokens()
        self.next_char()
        return True

    def token_type(self):
        """
        Returns the type of the current token.
        :return:
        """
        return self.current_type

    def key_word(self):
        """
        Returns the keyword which is the
        current token. Should be called only
        when tokenType() is KEYWORD .
        :return:
        """
        return self.current_token

    def symbol(self):
        """
        Returns the character which is the
        current token. Should be called only
        when tokenType() is SYMBOL .
        :return:
        """
        return self.current_token

    def identifier(self):
        """
        Returns the identifier which is the
        current token. Should be called only
        when tokenType() is IDENTIFIER .
        :return:
        """
        return self.current_token

    def intVal(self):
        """
        Returns the integer value of the
        current token. Should be called only
        when tokenType() is INT_CONST .
        :return:
        """
        return int(self.current_token)

    def string_val(self):
        """
        Returns the string value of the current
        token, without the double quotes.
        Should be called only when
        tokenType() is STRING_CONST .
        """
        return self.current_token[1:-1]



def main():
    path = '/home/ofer/nand2tetris/projects/10/Square/SquareGame.jack'
    myT = Tokenizer(path)
    print('.' not in myT.SYMBOLS)
    tokens = Element('tokens')
    while(myT.has_more_tokens()):
        myT.advance()
        type = myT.token_type()
        if type is JTok.KEYWORD:
            curr_elem = SubElement(tokens,"keyword")
            curr_elem.text = " "+myT.key_word()+" "
        elif type is JTok.IDENTIFIER:
            curr_elem = SubElement(tokens, "identifier")
            curr_elem.text = " "+myT.identifier()+" "
        elif type is JTok.INT_CONST:
            curr_elem = SubElement(tokens, "integerConstant")
            curr_elem.text = " "+str(myT.intVal())+" "
        elif type is JTok.STRING_CONST:
            curr_elem = SubElement(tokens, "stringConstant")
            curr_elem.text = " "+str(myT.string_val())+" "
        elif type is JTok.SYMBOL:
            curr_elem = SubElement(tokens, "symbol")
            curr_elem.text = " "+str(myT.symbol())+" "
    print(tostring(tokens))
    open(path[:-4]+"xml",'w').write(tostring(tokens).decode())


if __name__ == main():
    main()





