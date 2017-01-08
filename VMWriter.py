
class VMWriter:
    """
    Emits VM commands into a file, using the VM command syntax.
    """
    def __init__(self, file):
        """

        :param file:
        """
        self.file = open(file[:-5] + ".vm", 'w')

    def write_goto(self, label):
        """

        :param label:
        :return:
        """
        self.file.write("goto " + label + "\n")

    def write_if(self, label):
        """

        :param label:
        :return:
        """
        self.file.write("if-goto " + label + "\n")

    def write_call(self, name, n_args):
        """

        :param name:
        :param n_args:
        :return:
        """
        self.file.write("call " + name + " " + str(n_args) + "\n")

    def write_function(self, name, n_locals):
        """

        :param name:
        :param n_locals:
        :return:
        """
        self.file.write("function " + name + " " + str(n_locals) + "\n")

    def write_return(self):
        """

        :return:
        """
        self.file.write("return" + "\n")

    def write_push(self, segment, index):
        """

        :param segment:
        :param index:
        :return:
        """
        self.file.write("push " + segment + " " + str(index) + "\n")

    def write_pop(self, segment, index):
        """

        :param segment:
        :param index:
        :return:
        """
        self.file.write("pop " + segment + " " + str(index) + "\n")

    def write_arithmetic(self, command):
        """

        :param command:
        :return:
        """
        self.file.write(command + "\n")

    def write_label(self, label):
        """

        :param label:
        :return:
        """
        self.file.write("label " + label + "\n")

    def close(self):
        """

        :return:
        """
        self.file.close()

