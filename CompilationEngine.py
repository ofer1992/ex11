from Tokenizer import Tokenizer
from xml.etree.ElementTree import Element, SubElement, tostring
from JackTokens import JackTokens as JTok
from JackTokens import *
from xml.dom import minidom
from SymbolTable import SymbolTable
from SymbolTable import Kind
from VMWriter import VMWriter

EXPRESSION = "expression"
EXPRESSION_LIST = "expressionList"
SYMBOL = "symbol"
TERM = "term"
INTEGER_CONSTANT = "integerConstant"
STRING_CONSTANT = "stringConstant"
KEYWORD = "keyword"
IDENTIFIER = "identifier"
SUBROUTINE_CALL = "subroutineCall"
CLASS = "class"
STATEMENTS = "statements"

CONSTANT = "constant"
TEMP = "temp"
POINTER = "pointer"
ARGUMENT = "argument"


class CompilationEngine:


    def __init__(self, source):
        self.tokenizer = Tokenizer(source)
        self.tokenizer.has_more_tokens()
        self.tokenizer.advance()
        self.symbols = SymbolTable()
        self.writer = VMWriter(source)
        self.arithmetic_op = {}
        self.init_op()
        self.root = Element(CLASS)
        self.class_name = "TEMP"
        self.compile_subroutine(self.root)

        #self.compile_class(self.root)

    def init_op(self):
        self.arithmetic_op = {'+': "add",
                         '-': "sub",
                         '*': "call Math.multiply 2",
                         '/': "call Math.divide 2",
                         '&': "and",
                         '|': "or",
                        }

    def next(self):
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def compile_expression(self,caller):
        """
        Compiles an expression.
        :param caller:
        :return:
        """
        op_stack = []
        self.compile_term(SubElement(caller,TERM))
        while self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() in OPERATORS:
            #SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
            op_stack.append(self.tokenizer.symbol())
            self.next()
            self.compile_term(SubElement(caller,TERM))
        while op_stack:
            self.writer.write_arithmetic(self.arithmetic_op[op_stack.pop()])

    def compile_expressionList(self,caller):
        """
            compiles a list of expressions
        :param caller:
        :return: num_of_args - number of expressions in expressions list.
        used by function call
        """
        num_of_args = 0
        #  if expression list is empty
        if self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() == ")":
            caller.text = " "
            return num_of_args

        num_of_args += 1
        self.compile_expression(SubElement(caller,EXPRESSION))
        while self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() == ",":
            #SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
            num_of_args += 1
            self.next()
            self.compile_expression(SubElement(caller,EXPRESSION))
        return num_of_args

    def compile_subroutineCall(self,caller,first_token):
        """
        First token, the first identifier must be sent manually, so the method
        expects the current token to be the second in the specification.
        :param caller:
        :param first_token:
        :return:
        """
        #SubElement(caller, IDENTIFIER).text = first_token
        func_name = first_token
        #SubElement(caller, SYMBOL).text = self.tokenizer.symbol()

        if self.tokenizer.symbol() == '.':
            self.next()
            if self.symbols.kind_of(func_name): # If first token is var name
                segment = self.symbols.kind_of(func_name)
                segment = Kind.get_segment(segment)
                index = self.symbols.index_of(func_name)
                self.writer.write_push(segment,index)
                func_name = self.symbols.type_of(func_name)

            func_name = func_name+"."+self.tokenizer.identifier()
            #SubElement(caller, IDENTIFIER).text = self.tokenizer.identifier()
            self.next()

            #SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
        else:
            func_name = self.class_name+"."+func_name

        self.next()
        num_of_args = self.compile_expressionList(SubElement(caller, EXPRESSION_LIST))

        self.writer.write_call(func_name,num_of_args)
        #SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
        self.next()


    def compile_term(self,caller):
        """

        :param caller:
        :return:
        """
        type = self.tokenizer.token_type()
        if type is JTok.INT_CONST:
            #SubElement(caller, INTEGER_CONSTANT).text = str(self.tokenizer.intVal())
            self.writer.write_push(CONSTANT,self.tokenizer.intVal())
            self.next()

        elif type is JTok.STRING_CONST:
            #TODO : When is this the case
            SubElement(caller, STRING_CONSTANT).text = self.tokenizer.string_val()
            self.next()

        elif type is JTok.KEYWORD:
            #SubElement(caller, KEYWORD).text = self.tokenizer.key_word()
            if self.tokenizer.key_word() in {"null", "false"}:
                self.writer.write_push(CONSTANT, 0)
            elif self.tokenizer.key_word() == "true": # Assuming valid input, it must be true
                self.writer.write_push(CONSTANT, 1)
                self.writer.write_arithmetic("neg")
            elif self.tokenizer.key_word() == "this":
                self.writer.write_push(POINTER, 0)
            else:
                print("unexpected")

            self.next()

        elif type is JTok.IDENTIFIER:
            name = self.tokenizer.identifier()

            self.next()
            type = self.tokenizer.token_type()

            if type is JTok.SYMBOL and self.tokenizer.symbol() in {".", "("}:
                    self.compile_subroutineCall(caller,name)

            elif type is JTok.SYMBOL and self.tokenizer.symbol() == '[': #TODO: Arrays, later
                SubElement(caller, IDENTIFIER).text = name
                SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
                self.next()

                self.compile_expression(SubElement(caller, EXPRESSION))

                SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
                self.next()

            else:
                #SubElement(caller, IDENTIFIER).text = name
                kind = self.symbols.kind_of(name)
                index = self.symbols.index_of(name)
                if kind is not None:
                    self.writer.write_push(kind.get_segment(),index)
                else:
                    print("unexpected")

        elif type is JTok.SYMBOL:
            if self.tokenizer.symbol() == '(':
                #SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
                self.next()

                self.compile_expression(SubElement(caller, EXPRESSION))
                #SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
                self.next()

            elif self.tokenizer.symbol() in {'-','~'}:
                #SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
                unary_op = self.tokenizer.symbol()
                self.next()
                self.compile_term(SubElement(caller,TERM))
                if unary_op == "-":
                    self.writer.write_arithmetic("neg")
                elif unary_op == "~":
                    self.writer.write_arithmetic("not")
                else:
                    "unexpected"



    def compile_do(self, caller):
        """
        format : 'do' subroutineCall ';'
        :param caller:
        :return:
        """

        #SubElement(caller, KEYWORD).text = self.tokenizer.key_word()
        self.next()

        name = self.tokenizer.identifier()
        self.next()

        self.compile_subroutineCall(caller,name)
        self.writer.write_pop(TEMP,0)
        #SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set ';'
        self.next()

    def compile_let(self, caller):
        """
        format : 'let' varName ( '[' expression ']' )? '=' expression ';'
        :param caller:
        :return:
        """
        self.next() # skip 'let'

        varName = self.tokenizer.identifier()
        self.next()

        kind = self.symbols.kind_of(varName)
        index = self.symbols.index_of(varName)

        if self.tokenizer.symbol() == '[': # if array
            self.next() # skip [

            self.compile_expression(SubElement(caller, EXPRESSION))
            self.writer.write_push(kind.get_segment(),index)
            self.writer.write_arithmetic("add")
            self.writer.write_pop(POINTER,1)
            kind = "that"
            index = 0
            self.next() #skip ]

        self.next() # skip =

        self.compile_expression(SubElement(caller, EXPRESSION))
        self.writer.write_pop(kind.get_segment(),index)

        self.next() # skip ;


    def compile_return(self, caller):
        """
        format : 'return' expression? ';'
        :param caller:
        :return:
        """
        #SubElement(caller,KEYWORD).text = self.tokenizer.identifier()
        self.next()

        if self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() == ";":
            #SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
            self.writer.write_push(CONSTANT, 0)
            self.writer.write_return()
            self.next()
            return

        self.compile_expression(SubElement(caller,EXPRESSION))
        self.writer.write_return()
        #SubElement(caller, SYMBOL).text = self.tokenizer.symbol()
        self.next()

    def compile_while(self, caller):
        """
        format : 'while' '(' expression ')' '{' statements '}'
        :param caller:
        :return:
        """
        SubElement(caller, KEYWORD).text = self.tokenizer.key_word()  # set 'while' as text
        self.next()

        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set '('
        self.next()

        self.compile_expression(SubElement(caller, EXPRESSION))

        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set ')'
        self.next()

        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set '{'
        self.next()

        self.compile_statements(SubElement(caller, STATEMENTS))

        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set '}'
        self.next()


    def compile_statements(self, caller):
        """

        :param caller:
        :return:
        """
        STATEMENTS = {'do','while','let','return','if'}
        caller.text = " "
        while self.tokenizer.token_type() is JTok.KEYWORD and self.tokenizer.key_word() in STATEMENTS:
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
                   KEYWORD).text = self.tokenizer.key_word()  # set 'if' as text
        self.next()

        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set '('
        self.next()

        self.compile_expression(SubElement(caller, EXPRESSION))

        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set ')'
        self.next()

        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set '{'
        self.next()

        self.compile_statements(SubElement(caller, STATEMENTS))

        SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set '}'
        self.next()

        if self.tokenizer.token_type() is JTok.KEYWORD and self.tokenizer.key_word() == 'else':
            SubElement(caller,
                       KEYWORD).text = self.tokenizer.key_word()  # set 'else' as text
            self.next()

            SubElement(caller,
                       SYMBOL).text = self.tokenizer.symbol()  # set '{'
            self.next()

            self.compile_statements(SubElement(caller, STATEMENTS))

            SubElement(caller,
                       SYMBOL).text = self.tokenizer.symbol()  # set '}'
            self.next()

    def compile_var_dec(self, caller):
        """
        format: 'var' type varName ( ',' varName)* ';'
        :param caller:
        :return:
        """

        kind = self.tokenizer.key_word()
        #SubElement(caller, KEYWORD).text = kind  # set var as keyword
        self.next()

        return self.compile_list_of_vars(caller, "var", Kind[kind])

    def compile_class(self,caller):
        """

        :param caller:
        :return:
        """
        SubElement(caller,KEYWORD).text = self.tokenizer.key_word()
        self.next()

        SubElement(caller,IDENTIFIER).text = self.tokenizer.identifier()
        self.class_name = self.tokenizer.identifier()
        self.next()

        SubElement(caller,SYMBOL).text = self.tokenizer.symbol() #{
        self.next()

        while self.tokenizer.token_type() is JTok.KEYWORD and self.tokenizer.key_word() in {'static','field'}:
            self.compile_classVarDec(SubElement(caller,"classVarDec"))

        while not self.tokenizer.token_type() is JTok.SYMBOL:
            self.compile_subroutine(SubElement(caller,"subroutineDec"))

        SubElement(caller,SYMBOL).text = self.tokenizer.symbol() #}
        self.next()


    def compile_list_of_vars(self,caller,category, kind):
        """
        Helper method to compile lists of variables according to
        type varName (',' varName)*
        :param caller:
        :return:
        """
        num_of_vars = 0
        type = self.compile_type(caller)
        self.symbols.define(self.tokenizer.identifier(),type,kind)
        num_of_vars += 1
        #text = category+", defined, "+type+", "+kind.name+", "+str(self.symbols.index_of(self.tokenizer.identifier()))
        #SubElement(caller, IDENTIFIER).text = self.tokenizer.identifier()+", "+text  # set var name  as identifier
        self.next()

        while self.tokenizer.symbol() != ';':
            #SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set ','
            self.next()

            self.symbols.define(self.tokenizer.identifier(), type, kind)
            num_of_vars += 1
            #text = category + ", defined, " + type + ", " + kind.name + ", " + str(
            #    self.symbols.index_of(self.tokenizer.identifier()))
            #SubElement(caller, IDENTIFIER).text = self.tokenizer.identifier()+", "+text  # set var name
            self.next()

        #SubElement(caller, SYMBOL).text = self.tokenizer.symbol()  # set ';'
        self.next()
        return num_of_vars

    def compile_classVarDec(self,caller):
        """

        :param caller:
        :return:
        """
        kind = self.tokenizer.key_word()
        #SubElement(caller,KEYWORD).text = kind
        self.next()

        self.compile_list_of_vars(caller, kind, Kind[kind])



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
        return text

    def compile_subroutine(self,caller):
        """

        :param caller:
        :return:
        """

        subroutine_type = self.tokenizer.key_word()
        self.next()

        # Just to skip void or type
        if self.tokenizer.token_type() is JTok.KEYWORD and self.tokenizer.key_word() == "void":
            SubElement(caller,KEYWORD).text = self.tokenizer.key_word()
            self.next()
        else:
            self.compile_type(caller)

        name = self.class_name+"."+self.tokenizer.identifier()
        self.symbols.start_subroutine()
        self.next()

        self.next() # Skips (

        self.compile_parameterList(SubElement(caller,"parameterList"))

        self.next() # Skips )

        self.next() # Skips {

        num_of_locals = 0
        while self.tokenizer.token_type() is JTok.KEYWORD and self.tokenizer.key_word() == "var":
            num_of_locals += self.compile_var_dec(SubElement(caller,"varDec"))

        self.writer.write_function(name,num_of_locals)

        if subroutine_type == "constructor":
            self.writer.write_call("Memory.alloc", self.symbols.var_count(Kind.field))
            self.writer.write_pop(POINTER,0)

        elif subroutine_type == "method":
            self.writer.write_push(ARGUMENT,0)
            self.writer.write_pop(POINTER,0)

        self.compile_statements(SubElement(caller,"statements"))

        self.next() # Skips }

    def compile_parameterList(self,caller):
        """

        :param caller:
        :return:
        """
        if self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() == ")":
            caller.text = " "
            return

        type = self.compile_type(caller)
        name = self.tokenizer.identifier()

        # SubElement(caller,IDENTIFIER).text = self.tokenizer.identifier()
        self.symbols.define(name,type,Kind.arg)
        self.next()


        while self.tokenizer.token_type() is JTok.SYMBOL and self.tokenizer.symbol() == ",":
            # SubElement(caller,SYMBOL).text = self.tokenizer.symbol()
            self.next()
            print(self.symbols.subroutine_table)
            type = self.compile_type(caller)
            name = self.tokenizer.identifier()
            self.symbols.define(name, type, Kind.arg)
            #SubElement(caller, IDENTIFIER).text = self.tokenizer.identifier()
            self.next()




def main():
    # tk = Tokenizer('Mytestfor10.jack')
    # # while(tk.has_more_tokens()):
    # #     tk.advance()
    # #     print(tk.token_type(),tk.identifier())
    # ce = CompilationEngine('Mytestfor10.jack')
    # root = Element('class')
    # ce.compile_class(root)
    # print()
    # print(prettify(root))
    ce = CompilationEngine('Mytestfor10.jack')



if __name__ == "__main__":
    main()