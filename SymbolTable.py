from enum import Enum

class Kind(Enum):
    static = 0
    field = 1
    arg = 2
    var = 3

    def get_segment(self):
        if self is Kind.var:
            return "local"
        elif self is Kind.field:
            return "this"
        elif self is Kind.static:
            return "static"
        elif self is Kind.arg:
            return "argument"
        return None

TYPE_CELL = 0
KIND_CELL = 1
INDEX_CELL = 2

class SymbolTable:
    """

    """

    def __init__(self):
        """
        Smynol blal
        """
        self.class_table = {}
        self.subroutine_table = {}
        self.counter = {Kind.static: 0,
                        Kind.field: 0,
                        Kind.arg: 0,
                        Kind.var: 0}

    def start_subroutine(self):
        """

        :return:
        """
        self.subroutine_table = {}
        self.counter[Kind.arg], self.counter[Kind.var] = 0, 0

    def define(self,name, type, kind):
        """

        :param name:
        :param type:
        :param kind:
        :return:
        """
        if kind in {Kind.field, Kind.static}:
            self.class_table[name] = (type,kind,self.counter[kind])
        else:
            self.subroutine_table[name] = (type,kind,self.counter[kind])
        self.counter[kind] += 1

    def var_count(self, kind):
        """

        :param kind:
        :return:
        """
        return self.counter[kind]

    def kind_of(self,name):
        """

        :param name:
        :return:
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][KIND_CELL]
        elif name in self.class_table:
            return self.class_table[name][KIND_CELL]
        return None

    def type_of(self,name):
        """

        :param name:
        :return:
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][TYPE_CELL]
        elif name in self.class_table:
            return self.class_table[name][TYPE_CELL]
        return None

    def index_of(self,name):
        """

        :param name:
        :return:
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][INDEX_CELL]
        elif name in self.class_table:
            return self.class_table[name][INDEX_CELL]
        return None

