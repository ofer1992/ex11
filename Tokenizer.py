from JackTokens import JackTokens as JTok
from JackTokens import *


class Tokenizer:

    __already_called = False
    __more_tokens_flag = False

    def __init__(self, file_path):
        """
        Constructor for Tokenizer.
        :param file_path: path of file to be tokenized
        """
        self.__file = open(file_path)
        self.__char = ''
        self.__peek = self.__file.read(1)
        self.__current_token = None
        self.__current_type = None

    def next_char(self):
        """
        Reads next char in file.
        :return:
        """
        self.__char = self.__peek
        self.__peek = self.__file.read(1)

    def advance(self):
        """
        Gets the next token from the input
        and makes it the current token. This
        method should only be called if
        hasMoreTokens() is true. Initially
        there is no current token.
        :return:
        """
        self.__already_called = False

        if self.__char.isalpha(): # keyword or identifier
            self.__current_token = self.__char
            while self.__peek not in SYMBOLS and not self.__peek.isspace() and self.__peek != '':
                self.next_char()
                self.__current_token += self.__char
            self.__current_type = JTok.KEYWORD if self.__current_token in KEYWORDS else JTok.IDENTIFIER

        elif self.__char in SYMBOLS: # symbol
            self.__current_token = self.__char
            self.__current_type = JTok.SYMBOL

        elif self.__char == "\"": # string constant
            self.__current_token = self.__char
            while self.__peek != "\"":
                self.next_char()
                self.__current_token += self.__char
            self.next_char()
            self.__current_token += self.__char
            self.__current_type = JTok.STRING_CONST

        elif self.__char.isdigit(): # int constant
            self.__current_token = self.__char
            while self.__peek.isdigit():
                self.next_char()
                self.__current_token += self.__char
            self.__current_type = JTok.INT_CONST

        # When advance terminates, __char is the last character
            #  read from the file.


    def has_more_tokens(self):
        """
        Do we have more tokens in the input?
        :return: true iff there are more tokens to be read
        """

        # If has_more_tokens was already called once before advance(), return
        # the same answer.
        if self.__already_called:
            return self.__more_tokens_flag

        if self.__peek == '':  # Reached end of file
            self.__more_tokens_flag = False

        elif self.__peek == '/':  # Possibility of comment
            self.next_char()
            if self.__peek == '/':  # // comment
                while self.__char != '\n' and self.__char != '':
                    self.next_char()
                return self.has_more_tokens()

            elif self.__peek == '*':  # /* comment
                self.next_char()
                self.next_char()
                while not (self.__char == '*' and self.__peek == '/'):
                    self.next_char()
                self.next_char()
                return self.has_more_tokens()

            # / is a symbol
            self.__more_tokens_flag = True
            return self.__more_tokens_flag

        elif self.__peek.isspace():  # Eliminating white space
            while self.__peek.isspace():
                self.next_char()
            return self.has_more_tokens()

        else: # set char to beginning of new token
            self.next_char()
            self.__more_tokens_flag = True

        self.__already_called = True
        return self.__more_tokens_flag

    def token_type(self):
        """
        Returns the type of the current token.
        :return:
        """
        return self.__current_type

    def key_word(self):
        """
        Returns the keyword which is the
        current token. Should be called only
        when tokenType() is KEYWORD .
        :return:
        """
        return self.__current_token

    def symbol(self):
        """
        Returns the character which is the
        current token. Should be called only
        when tokenType() is SYMBOL .
        :return:
        """
        return self.__current_token

    def identifier(self):
        """
        Returns the identifier which is the
        current token. Should be called only
        when tokenType() is IDENTIFIER .
        :return:
        """
        return self.__current_token

    def intVal(self):
        """
        Returns the integer value of the
        current token. Should be called only
        when tokenType() is INT_CONST .
        :return:
        """
        return int(self.__current_token)

    def string_val(self):
        """
        Returns the string value of the current
        token, without the double quotes.
        Should be called only when
        tokenType() is STRING_CONST .
        """
        return self.__current_token[1:-1]

# TK = Tokenizer("Mytestfor10.jack")
# while(TK.has_more_tokens()):
#     TK.advance()
#     print(TK.token_type(),TK.identifier())