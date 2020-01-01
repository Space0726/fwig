RADICAL = "radical.mf"
COMBINATION = "combination.mf"

# For beginchar()
BEGIN_CHAR = "beginchar({name}, {width}, {height}, {depth});"
END_CHAR = "endchar;"

# For if statement
IF_STATEMENT = "if {condition}:"
END_IF = "fi"

def _apply_indent(indent_level, string):
    if indent_level:
        return "    " * indent_level + string
    return string


class MfStatement:
    def __init__(self, mf, begin_format, args_dict, end_keyword, indent_level):
        self.mf = mf
        self.begin_format = begin_format
        self.args_dict = args_dict
        self.end_keyword = end_keyword
        self.indent_level = indent_level

    def __enter__(self):
        self.mf.write(_apply_indent(self.indent_level, self.begin_format.format(**self.args_dict)) + '\n')
        return self

    def __exit__(self, type_, value, traceback):
        self.mf.write(_apply_indent(self.indent_level, self.end_keyword) + '\n')

    def add_body(self, *exprs):
        for expr in exprs:
            self.mf.write(_apply_indent(self.indent_level+1, expr + '\n'))

class MfFunc(MfStatement):
    def __init__(self, mf, signature, args_dict, end_keyword, indent_level):
        super().__init__(mf, signature, args_dict, end_keyword, indent_level)

class MfIf(MfStatement):
    def __init__(self, mf, condition, indent_level):
        cond_dict = {'condition': condition}
        super().__init__(mf, IF_STATEMENT, cond_dict, END_IF, indent_level)

class BeginChar(MfFunc):
    def __init__(self, mf, name, width, height, depth, indent_level=0):
        args_dict = {
            "name": name,
            "width": width,
            "height": height,
            "depth": depth
        }
        super().__init__(mf, BEGIN_CHAR, args_dict, END_CHAR, indent_level)
