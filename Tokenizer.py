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
    already_called = False
    more_tokens_flag = False
    queue = []
    lookback_index = -1

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
        if self.lookback_index < -1:
            self.lookback_index +=1
            self.current_type, self.current_token = self.queue[self.lookback_index]
        self.already_called = False
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
        self.queue.append((self.current_type, self.current_token))
        if len(self.queue) >=3:
            self.queue.pop(0)

    def has_more_tokens(self):
        """
        Do we have more tokens in the input?
        :return:
        """
        if self.lookback_index < -1:
            return True
        if self.already_called:
            return self.more_tokens_flag
        if self.peek == '':
            self.more_tokens_flag = False
        elif self.peek == '/':
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
                self.more_tokens_flag = True
                return True
            return self.has_more_tokens()
        elif self.peek.isspace():
            while self.peek.isspace():
                self.next_char()
            return self.has_more_tokens()
        else:
            self.next_char()
            self.more_tokens_flag = True
        self.already_called = True
        return self.more_tokens_flag

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

    def set_back(self):
        """
        Move back tokenizer 1 token
        :param n:
        :return:
        """
        self.lookback_index = -2
        self.current_type, self.current_token = self.queue[self.lookback_index]
