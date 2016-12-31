import re
from JackTokens import JackTokens as JTok


class Tokenizer:
    """

    """

    comment_pat = re.compile(r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"')
    keyWord_pat = re.compile(r'class|constructor|function|method|field|static|'
                             r'var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return')
    symbol_pat = re.compile(r'(.*)(\\{|\\}|\\(|\\)|\\[|\\]|\\.|\\,|;|\\+|-|\\*|/|&|\\||<|>|=|~)(.*)')
    iden_pat= re.compile(r'^[\d]')#TODO
    int_pat = re.compile(r'[0-32767]')#TODO
    str_pat = re.compile(r'^\"[^\"]+\"$')#TODO

    def __init__(self, file_path):
        self.file = open(file_path)
        self.curr_line = ''
        self.curr_token = ''

    def advance(self):#TODO
        """
        Gets the next token from the input
        and makes it the current token. This
        method should only be called if
        hasMoreTokens() is true. Initially
        there is no current token.
        :return:
        """
        # if not self.has_more_tokens:
        #     return
        # else:

        self.curr_line = self.file.readline()
        self.curr_line.replace(" ", "")

    def has_more_tokens(self):#TODO
        """
        Do we have more tokens in the input?
        :return:
        """
        pass

    def token_type(self):
        """
        Returns the type of the current token.
        :return:
        """
        if self.keyWord_pat.match(self.curr_token):
            return JTok.KEYWORD
        elif self.symbol_pat.match(self.curr_token):
            return JTok.SYMBOL
        elif self.iden_pat.match(self.curr_token):
            return JTok.IDENTIFIER
        elif self.int_pat.match(self.curr_token):
            return JTok.INT_CONST
        elif self.str_pat.match(self.curr_token):
            return JTok.STRING_CONST
        else:
            return JTok.ERROR

    def key_word(self):
        """
        Returns the keyword which is the
        current token. Should be called only
        when tokenType() is KEYWORD .
        :return:
        """
        if self.token_type() != JTok.KEYWORD:
            return JTok.ERROR

        if self.curr_token is "class" :
            return JTok.CLASS
        elif self.curr_token is "method":
            return JTok.METHOD
        elif self.curr_token is "function":
            return JTok.FUNCTION
        elif self.curr_token is "constructor":
            return JTok.CONSTRUCTOR
        elif self.curr_token is "int":
            return JTok.INT
        elif self.curr_token is "boolean":
            return JTok.BOOLEAN
        elif self.curr_token is "char":
            return JTok.CHAR
        elif self.curr_token is "void":
            return JTok.VOID
        elif self.curr_token is "var":
            return JTok.VAR
        elif self.curr_token is "static":
            return JTok.STATIC
        elif self.curr_token is "field":
            return JTok.FIELD
        elif self.curr_token is "let":
            return JTok.LET
        elif self.curr_token is "do":
            return JTok.DO
        elif self.curr_token is "if":
            return JTok.IF
        elif self.curr_token is "else":
            return JTok.ELSE
        elif self.curr_token is "while":
            return JTok.WHILE
        elif self.curr_token is "return":
            return JTok.RETURN
        elif self.curr_token is "true":
            return JTok.TRUE
        elif self.curr_token is "false":
            return JTok.FALSE
        elif self.curr_token is "null":
            return JTok.NULL
        elif self.curr_token is "this":
            return JTok.THIS
        else:
            return JTok.ERROR

    def symbol(self):  #TODO
        """
        Returns the character which is the
        current token. Should be called only
        when tokenType() is SYMBOL .
        :return:
        """
        if self.token_type() != JTok.SYMBOL:
            return JTok.ERROR
        else:
            if self.curr_token is "<":
                return "&lt;"
            elif self.curr_token is ">":
                return "&gt;"
            elif self.curr_token is "&":
                return "&amp;"
            else:
                return str(self.curr_token)

    def identifier(self): #TODO
        """
        Returns the identifier which is the
        current token. Should be called only
        when tokenType() is IDENTIFIER .
        :return:
        """
        if self.token_type() != JTok.IDENTIFIER:
            return JTok.ERROR
        else:
            return self.curr_token

    def intVal(self):  #TODO
        """
        Returns the integer value of the
        current token. Should be called only
        when tokenType() is INT_CONST .
        :return:
        """
        if self.token_type() != JTok.INT_CONST:
            return JTok.ERROR
        else:
            return str(self.curr_token)

    def string_val(self):  #TODO
        """
        Returns the string value of the current
        token, without the double quotes.
        Should be called only when
        tokenType() is STRING_CONST .
        """
        if self.token_type() != JTok.STRING_CONST:
            return JTok.ERROR
        else:
            return

    def is_comment(self, string_to_check):
        """
        helping func
        :param string_to_check:
        :return:
        """
        return self.comment_pat.match(string_to_check)

    def write_tag(self, output, word, curr_type):
        """
        :param output:
        :param word:
        :param curr_type:
        :return:
        """
        output.print("<" + curr_type + "> " + word + " </" + curr_type + ">")

    def create_xml(self, output):
        """

        :param output:
        :return:
        """

        output.print("<tokens>")

        while self.has_more_tokens():

            self.advance()

            curr_type = self.token_type()

            if curr_type == JTok.KEYWORD:
                self.write_tag(output, self.curr_token, "keyword")

            elif curr_type == JTok.SYMBOL:
                self.write_tag(output, self.symbol(), "symbol")

            elif curr_type == JTok.IDENTIFIER:
                self.write_tag(output, self.identifier(), "identifier")

            elif curr_type == JTok.INT_CONST:
                self.write_tag(output, str(self.intVal()), "integerConstant")

            elif curr_type == JTok.STRING_CONST:
                self.write_tag(output, self.string_val(), "stringConstant")

            else:
                self.write_tag(output, "ERROR", "error")

            output.print("</tokens>")


def main():
    myT = Tokenizer('/home/ofir/Desktop/CS/Nand/ex10/Mytestfor10.jack')
    myT.advance()

    if myT.keyWord_pat.match(myT.curr_line)or myT.comment_pat.match(myT.curr_line):
        print(myT.curr_line)
    else:
        print("no" + myT.curr_line)

if __name__ == main():
    main()





