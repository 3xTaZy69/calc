import math
import customtkinter as ctk
from tkinter import filedialog

"""
INTLIT
UNDERSCORE
SEMICOL
IDENT
EQ
LPAREN
RPAREN
COMMA
LFIGURE
RFIGURE
COLON

EQZ
LESS
LESSEQ
GREATEREQ
GREATER
NEQ

ADD
SUB
MUL
DIV
BITWISE_AND
BITWISE_OR
XOR
BITWISE_NOT
LOGIC_NOT
SHL
SHR

POW
SIN
COS
TAN
ASIN
ACOS
ATAN
MOD
SQRT

SUM
PROD
LOG
MIN
MAX

"""

class Token:
    def __init__(self, kind, data):
        self.kind = kind
        self.data = data

    def dbg(self):
        print(self.kind, self.data)

class Lexer:
    def __init__(self, code):
        self.pc = 0
        self.code = code
        self.tokens = []
        self.cur = None if len(code) == 0 else code[0]

        while self.cur != None:
            if self.cur.isdigit():
                self.number()
            elif self.cur.isalpha():
                self.ident()
            elif self.cur in "+-&|!^&*/~=;()_,><=}{:":
                self.op()
            elif self.cur.isspace():
                self.adv()
            elif self.cur == "#":
                self.adv()
                while self.cur and self.cur != "#":
                    self.adv()
                self.adv()
                if self.cur and self.cur == ";":
                    self.adv()
            else:
                raise ValueError(f"\033[91mCANNOT USE \'{self.cur}\' SYMBOL\033[0m")

    def adv(self):
        self.pc += 1
        self.cur = None if len(self.code) == self.pc else self.code[self.pc]

    def number(self):
        number = ""

        while self.cur != None and self.cur.isdigit():
            number += self.cur
            self.adv()

        if self.cur == '.':
            number += self.cur
            self.adv()
            while self.cur != None and self.cur.isdigit():
                number += self.cur
                self.adv()
            n = float(number)
        elif self.cur == 'b' and number == '0':
            self.adv()
            number = ""

            while self.cur != None and self.cur in "01":
                number += self.cur
                self.adv()
            n = int(number, 2)
        elif (self.cur == 'x' or self.cur == 'h') and number == '0':
            self.adv()
            number = ""

            while self.cur != None and self.cur in "0123456789abcdefABCDEF":
                number += self.cur
                self.adv()
            n = int(number, 16)
        else:
            n = int(number)

        self.tokens.append(Token("INTLIT", n))

    def op(self):
        match self.cur:
            case '+': t = Token("ADD", None)
            case '-': t = Token("SUB", None)
            case '*':
                if self.pc < len(self.code) and self.code[self.pc+1] == '*':
                    self.adv()
                    t = Token("POW", None)
                else:
                    t = Token("MUL", None)
            case '/': t = Token("DIV", None)
            case '&': t = Token("BITWISE_AND", None)
            case '|': t = Token("BITWISE_OR", None)
            case '^': t = Token("XOR", None)
            case '~': t = Token("BITWISE_NOT", None)
            case '=':
                if  self.peek_next() == "=":
                    self.adv()
                    t = Token("EQZ", None)
                else:
                    t = Token("EQ", None)
            case '>':
                if  self.peek_next() == "=":
                    t = Token("GREATEREQ", None)
                    self.adv()
                elif  self.peek_next() == ">":
                    t = Token("SHR", None)
                    self.adv()
                else:
                    t = Token("GREATER", None)
            case '<':
                if  self.peek_next() == "=":
                    t = Token("LESSEQ", None)
                    self.adv()
                elif  self.peek_next() == "<":
                    t = Token("SHL", None)
                    self.adv()
                else:
                    t = Token("LESS", None)
            case '!':
                if  self.peek_next() == "=":
                    t = Token("NEQ", None)
                    self.adv()
                else:
                    t = Token("LOGIC_NOT", None)
            case ';': t = Token("SEMICOL", None)
            case '(': t = Token("LPAREN", None)
            case ')': t = Token("RPAREN", None)
            case '_': t = Token("UNDERSCORE", None)
            case ',': t = Token("COMMA", None)
            case '{': t = Token("LFIGURE", None)
            case '}': t = Token("RFIGURE", None)
            case ':': t = Token("COLON", None)

        self.adv()
        self.tokens.append(t)

    def peek_next(self):
        if len(self.code) > self.pc+1:
            return self.code[self.pc+1]

    def ident(self):
        ident = ""

        while self.cur != None and self.cur.isalnum():
            ident += self.cur
            self.adv()

        match ident:
            case "sin": t = Token("SIN", None)
            case "cos": t = Token("COS", None)
            case "tan": t = Token("TAN", None)
            case "acos": t = Token("ACOS", None)
            case "asin": t = Token("ASIN", None)
            case "atan": t = Token("ATAN", None)
            case "sum": t = Token("SUM", None)
            case "prod": t = Token("PROD", None)
            case "mod": t = Token("MOD", None)
            case "sqrt": t = Token("SQRT", None)
            case "log": t = Token("LOG", None)
            case "min": t = Token("MIN", None)
            case "max": t = Token("MAX", None)
            case _: t = Token("IDENT", ident)

        self.tokens.append(t)


class BinOp:
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

class UnOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class SUM:
    def __init__(self, vname, vstart, end, expr):
        self.vname = vname
        self.vstart = vstart
        self.end = end
        self.expr = expr

class PROD:
    def __init__(self, vname, vstart, end, expr):
        self.vname = vname
        self.vstart = vstart
        self.end = end
        self.expr = expr

class Variable:
    def __init__(self, name, value, dependencies):
        self.name = name
        self.expr = value
        self.dependencies = dependencies

class Function:
    def __init__(self, name, args, expr):
        self.name = name
        self.args = args
        self.expr = expr

class FunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Conditional:
    def __init__(self, expr, then_branch, else_branch):
        self.expr = expr
        self.then_branch = then_branch
        self.else_branch = else_branch

class Log:
    def __init__(self, base, arg):
        self.base = base
        self.arg = arg

class Min:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

class Max:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

class Parser:
    def __init__(self, tokens):
        self.pc = 0
        self.tokens = tokens
        self.ast = []
        self.cur = None if len(tokens) == 0 else tokens[0]
        self.vdependencies = []
        self.functions = []

    def adv(self):
        self.pc += 1
        self.cur = None if len(self.tokens) == self.pc else self.tokens[self.pc]

    def require(self, token):
        if self.cur == None:
            raise ValueError(f"\033[91mEXPECTED \'{token}\' GOT NONE\033[0m")
        elif self.cur.kind != token:
            raise ValueError(f"\033[91mEXPECTED \'{token}\' GOT \'{self.cur.kind}\'\033[0m")

    def ban(self, token):
        if self.cur == None and token == None:
            raise ValueError("\033[91mUNEXPECTED NONE\033[0m")
        elif self.cur == None and token != None:
            return
        elif self.cur.kind == token:
            raise ValueError(f"\033[91mUNEXPECTED \'{self.cur.kind}\'\033[0m")

    def exp(self):
        left = self.or_expr()
        while self.cur != None and self.cur.kind in ["EQZ", "NEQ", "LESS", "LESSEQ", "GREATER", "GREATEREQ"]:
            op = self.cur.kind
            self.adv()
            left = BinOp(left, op, self.or_expr())
        return left

    def or_expr(self):
        left = self.xor_expr()
        while self.cur != None and self.cur.kind == "BITWISE_OR":
            self.adv()
            left = BinOp(left, 'BITWISE_OR', self.xor_expr())
        return left

    def xor_expr(self):
        left = self.and_expr()
        while self.cur != None and self.cur.kind == "XOR":
            self.adv()
            left = BinOp(left, 'XOR', self.and_expr())
        return left

    def and_expr(self):
        left = self.add_expr()
        while self.cur != None and self.cur.kind == "BITWISE_AND":
            self.adv()
            left = BinOp(left, 'BITWISE_AND', self.add_expr())
        return left

    def add_expr(self):
        left = self.mul_expr()
        while self.cur != None and self.cur.kind in ["ADD", "SUB"]:
            op = self.cur.kind
            self.adv()
            left = BinOp(left, op, self.mul_expr())
        return left

    def mul_expr(self):
        left = self.pow_expr()
        while self.cur != None and self.cur.kind in ["MUL", "DIV"]:
            op = self.cur.kind
            self.adv()
            left = BinOp(left, op, self.pow_expr())
        return left

    def pow_expr(self):
        left = self.unary()
        while self.cur != None and self.cur.kind == "POW":
            self.adv()
            left = BinOp(left, 'POW', self.unary())
        return left

    def unary(self):
        self.ban(None)

        if self.cur.kind in ["SIN", "COS", "TAN", "ASIN", "ACOS", "ATAN", "MOD", "SQRT"]:
            op = self.cur.kind
            self.adv()
            self.ban(None)
            e = self.unary()
            return UnOp(op, e)
        elif self.cur.kind in ["SUM", "PROD"]:
            t = self.cur.kind
            self.adv()
            self.require("UNDERSCORE")
            self.adv()
            self.require("LPAREN")
            self.adv()
            self.require("IDENT")
            vname = self.cur.data
            self.adv()
            self.require("EQ")
            self.adv()
            vstart = self.exp()
            self.require("RPAREN")
            self.adv()
            self.require("XOR")
            self.adv()
            self.require("LPAREN")
            self.adv()
            end = self.exp()
            self.require("RPAREN")
            self.adv()
            self.require("UNDERSCORE")
            self.adv()
            self.require("LPAREN")
            self.adv()
            e = self.exp()
            self.require("RPAREN")
            self.adv()
            match t:
                case "SUM": return SUM(vname, vstart, end, e)
                case "PROD": return PROD(vname, vstart, end, e)
        elif self.cur.kind == 'SUB':
            self.adv()
            e = self.unary()
            return UnOp("NEG", e)
        elif self.cur.kind in ["MIN", "MAX"]:
            kind = self.cur.kind
            self.adv()
            self.require("LPAREN")
            self.adv()
            lhs = self.exp()
            self.require("COMMA")
            self.adv()
            rhs = self.exp()
            self.require("RPAREN")
            self.adv()

            match kind:
                case "MIN": return Min(lhs, rhs)
                case "MAX": return Max(lhs, rhs)
        elif self.cur.kind == "LOG":
            self.adv()
            self.require("UNDERSCORE")
            self.adv()
            self.require("LPAREN")
            self.adv()
            base = self.exp()
            self.require("RPAREN")
            self.adv()
            self.require("XOR")
            self.adv()
            self.require("LPAREN")
            self.adv()
            arg = self.exp()
            self.require("RPAREN")
            self.adv()

            return Log(base, arg)
        elif self.cur.kind in ['BITWISE_NOT', 'LOGIC_NOT']:
            op = self.cur.kind
            self.adv()
            e = self.unary()
            return UnOp(op, e)
        else:
            return self.primary()

    def primary(self):

        self.ban(None)

        if self.cur.kind == 'LPAREN':
            self.adv()
            e = self.exp()
            self.require("RPAREN")
            self.adv()
        elif self.cur.kind == "INTLIT":
            e = self.cur.data
            self.adv()
        elif self.cur.kind == "IDENT":
            e = self.cur.data
            self.adv()
            if self.cur != None and self.cur.kind == "LPAREN":
                args = self.parse_args()
                return FunctionCall(e, args)
            self.vdependencies.append(e)
        elif self.cur.kind == "LFIGURE":
            self.adv()
            expr = self.exp()
            self.require("COLON")
            self.adv()
            then_branch = self.exp()
            self.require("COLON")
            self.adv()
            else_branch = self.exp()
            self.require("RFIGURE")
            self.adv()
            e = Conditional(expr, then_branch, else_branch)
        else:
            raise ValueError(f"\033[91mUNEXPECTED \'{self.cur.kind}\'\033[0m")

        if self.cur and self.cur.kind == "LOGIC_NOT":
            self.adv()
            return UnOp("FACT", e)

        return e

    def fetch_variable(self):
        self.require("IDENT")
        name = self.cur.data
        self.adv()

        if self.cur != None and self.cur.kind == "LPAREN":
            args = self.parse_args()
            self.require("EQ")
            self.adv()
            e = self.exp()
            self.functions.append(Function(name, args, e))
        else:
            self.adv()
            self.vdependencies = []
            e = self.exp()
            return Variable(name, e, self.vdependencies.copy())

    def parse_args(self):
        self.require("LPAREN")
        self.adv()
        args = []
        if self.cur and self.cur.kind == "RPAREN":
            self.adv()
            return args
        args.append(self.exp())
        while self.cur != None and self.cur.kind == "COMMA":
            self.adv()
            args.append(self.exp())
        self.require("RPAREN")
        self.adv()
        return args

    def parse_all(self):
        variables = []
        v = self.fetch_variable()
        if v:
            variables.append(v)
        while self.cur != None and self.cur.kind == "SEMICOL":
            self.adv()
            v = self.fetch_variable()
            if v:
                variables.append(v)
        return variables

def debug_expr(expr):
    if isinstance(expr, BinOp):
        return f"({debug_expr(expr.lhs)}) {expr.op} ({debug_expr(expr.rhs)})"
    elif isinstance(expr, UnOp):
        return f"{expr.op}({debug_expr(expr.operand)})"
    else:
        return expr

def debug_variables(variables: list[Variable]):
    for variable in variables:
        print(f"{variable.name} = {debug_expr(variable.expr)}\n{variable.dependencies}")

def order(vs: list[Variable]):
    lut = {v.name: v for v in vs}
    indeg = {v.name: 0 for v in vs}
    users = {v.name: [] for v in vs}

    for v in vs:
        for d in set(v.dependencies):
            if d in users:
                indeg[v.name] += 1
                users[d].append(v.name)

    order = [n for n, k in indeg.items() if k == 0]

    i = 0
    while i < len(order):
        name = order[i]
        i += 1
        for u in users[name]:
            indeg[u] -= 1
            if indeg[u] == 0:
                order.append(u)

    if len(order) < len(indeg):
        looped = [n for n, k in indeg.items() if n not in order]
        raise ValueError(f"loop: {looped}")

    result = [lut[v] for v in order]

    return result

def function_dict(functions: list[Function]):
    return {f.name: f for f in functions}

def fetch_variables(code: str) -> list[Variable]:
    l = Lexer(code)
    p = Parser(l.tokens)
    pvs = p.parse_all()
    return order(pvs)

class Evaluator:
    def __init__(self, variables: list[Variable], functions: list[Function]):
        self.variables = variables
        self.values = {}
        self.functions = function_dict(functions)
        self.aliases = {}
    def eval_exp(self, exp) -> float:
        if isinstance(exp, int) | isinstance(exp, float):
            return float(exp) # flaot для избежания конфликта int + float
        elif isinstance(exp, str):
            if exp == 'pi': return math.pi
            elif exp == 'e': return math.e
            else:
                return self.values[exp]
        elif isinstance(exp, BinOp):
            left: float = self.eval_exp(exp.lhs)
            right: float = self.eval_exp(exp.rhs)

            match exp.op:
                case 'ADD': return left + right
                case 'SUB': return left - right
                case 'MUL': return left * right
                case 'DIV': return left / right
                case 'POW': return left ** right
                case 'BITWISE_AND': return float(int(left) & int(right))
                case 'BITWISE_OR': return float(int(left) | int(right))
                case 'XOR': return float(int(left) ^ int(right))
                case 'EQZ': return float(left == right)
                case 'NEQ': return float(left != right)
                case 'GREATER': return float(left > right)
                case 'GREATEREQ': return float(left >= right)
                case 'LESS': return float(left < right)
                case 'LESSEQ': return float(left <= right)
                case 'SHL': return float(int(left) << int(right))
                case 'SHR': return float(int(left) >> int(right))
        elif isinstance(exp, UnOp):
            operand: float = self.eval_exp(exp.operand)

            match exp.op:
                case 'NEG': return 0 - operand
                case 'COS': return math.cos(operand)
                case 'ACOS': return math.acos(operand)
                case 'SIN': return math.sin(operand)
                case 'ASIN': return math.asin(operand)
                case 'TAN': return math.tan(operand)
                case 'ATAN': return math.atan(operand)
                case 'BITWISE_NOT': return float(~int(operand))
                case 'LOGIC_NOT': return float(not operand)
                case 'MOD': return abs(operand)
                case 'SQRT': return math.sqrt(operand)
                case 'FACT': return float(math.factorial(int(operand)))
        elif isinstance(exp, SUM) | isinstance(exp, PROD):
            start = math.floor(self.eval_exp(exp.vstart) + 0.5)
            end = math.floor(self.eval_exp(exp.end) + 0.5)

            existed = None

            if exp.vname in self.values:
                existed = self.values[exp.vname]

            result: float = 0

            i = start

            if isinstance(exp, SUM):
                while i <= end:
                    self.values[exp.vname] = i
                    result += self.eval_exp(exp.expr)
                    i += 1
            else:
                result = 1
                while i <= end:
                    self.values[exp.vname] = i
                    result *= self.eval_exp(exp.expr)
                    i += 1

            if existed:
                self.values[exp.vname] = existed
            else:
                self.values.pop(exp.vname)

            return float(result)
        elif isinstance(exp, FunctionCall):
                fname = self.aliases.get(exp.name, exp.name)   # resolve f -> table
                func = self.functions[fname]

                new_values = {}
                new_funcs = {}

                for argname, argexpr in zip(func.args, exp.args):
                    if isinstance(argexpr, str) and argexpr not in self.values and (argexpr in self.functions or argexpr in self.aliases):
                        new_funcs[argname] = self.aliases.get(argexpr, argexpr)
                    else:
                        new_values[argname] = self.eval_exp(argexpr)

                save_values = {a: self.values[a] for a in func.args if a in self.values}
                save_funcs = {a: self.aliases[a] for a in func.args if a in self.aliases}

                for a in func.args:
                    self.values.pop(a, None)
                    self.aliases.pop(a, None)

                self.aliases.update(new_funcs)
                self.values.update(new_values)

                e = self.eval_exp(func.expr)

                for a in func.args:
                    self.values.pop(a, None)
                    self.aliases.pop(a, None)

                self.aliases.update(save_funcs)
                self.values.update(save_values)

                return e

        elif isinstance(exp, Conditional):

            e_eval = self.eval_exp(exp.expr)

            if e_eval == 0:
                return self.eval_exp(exp.else_branch)
            else:
                return self.eval_exp(exp.then_branch)
        elif isinstance(exp, Min):
            left: float = self.eval_exp(exp.lhs)
            right: float = self.eval_exp(exp.rhs)
            return min(left, right)
        elif isinstance(exp, Max):
            left: float = self.eval_exp(exp.lhs)
            right: float = self.eval_exp(exp.rhs)
            return max(left, right)
        elif isinstance(exp, Log):
            base: float = self.eval_exp(exp.base)
            arg: float = self.eval_exp(exp.arg)
            return math.log(arg, base)

    def eval(self):

        for v in self.variables:
            self.values[v.name] = self.eval_exp(v.expr)

THEME = {
    "fg": "#0b0f0c",
    "nav": "#121a14",
    "accent": "#4ade80",
    "text": "#d9f7e3",
    "muted": "#5f7d69",
}


class Block:
    def __init__(self, frame: ctk.CTkFrame, delete, entry, result, on_remove):
        self.frame = frame
        self.delete = delete
        self.entry = entry
        self.result = result
        self.on_remove = on_remove

        delete.configure(command=self.remove)
    def remove(self):
        self.frame.destroy()
        self.on_remove(self)

class App(ctk.CTk):
    def __init__(self):
        self.code = "a = pi"
        self.blocks: list[Block] = []
        self.main_page = True

        super().__init__()
        self.title("Calc")
        self.geometry("800x400")
        self.configure(fg_color=THEME["fg"])
        self.nav_panel = ctk.CTkFrame(self, width=800, height=50, fg_color=THEME["nav"], corner_radius=0)
        self.nav_panel.pack(fill="x")

        self.add_btn = ctk.CTkButton(self.nav_panel,
            hover_color=THEME["muted"],
            width=50,
            height=50,
            text="+",
            fg_color=THEME["nav"],
            corner_radius=0,
            command=self.push_block,
            font=ctk.CTkFont(
                size=30,
                weight="bold"
                )
            )
        self.add_btn.pack(side="left")


        self.export_btn = ctk.CTkButton(self.nav_panel,
            hover_color=THEME["muted"],
            width=50,
            height=50,
            text="export",
            fg_color=THEME["nav"],
            command = self.export,
            corner_radius=0,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
                )
            )

        self.export_btn.pack(side="right")

        self.import_btn = ctk.CTkButton(self.nav_panel,
            hover_color=THEME["muted"],
            width=50,
            height=50,
            text="import",
            fg_color=THEME["nav"],
            command = self.import_blocks,
            corner_radius=0,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
                )
            )

        self.import_btn.pack(side="right")

        self.theme_btn = ctk.CTkButton(self.nav_panel,
            hover_color=THEME["muted"],
            width=50,
            height=50,
            text="theme",
            fg_color=THEME["nav"],
            command = self.switch_menu,
            corner_radius=0,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
                )
            )

        self.theme_btn.pack(side="right")

        self.codeframe = ctk.CTkScrollableFrame(self,
            fg_color=THEME["fg"],
            corner_radius=0,
            scrollbar_button_color=THEME["nav"],
            scrollbar_button_hover_color=THEME["muted"])

        self.codeframe.pack(fill="both",
            expand=True)

        self.themeframe = ctk.CTkFrame(self,
            fg_color=THEME["fg"],
            corner_radius=0)

        self.themeframe.pack(fill="both",
            expand=True)

        self.themeframe.pack_forget()

        self.theme_btns = []

        for btn in range(4):
            match btn:
                case 0: f = self.theme_violet; name = "violet"
                case 1: f = self.theme_green; name = "green"
                case 2: f = self.theme_warm; name = "warm"
                case 3: f = self.theme_ocean; name = "ocean"

            b = ctk.CTkButton(self.themeframe,
                border_width=0,
                border_color=THEME["nav"],
                width=50,
                height=50,
                text=name,
                fg_color=THEME["nav"],
                command = f,
                corner_radius=0,
                font=ctk.CTkFont(
                    size=15,
                    weight="bold"
                    )
                )

            b.pack(side="left", fill="both", expand=True, padx=5)
            self.theme_btns.append(b)


    def export(self):

        path = filedialog.asksaveasfilename(
            title="Save as",
            defaultextension=".dat",
            filetypes=[("Data file", "*.dat"), ("All files", "*.*")],
            initialfile="project.dat",
        )

        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.code)

    def push_block(self, code=""):
        block = ctk.CTkFrame(self.codeframe, width=800, height=50, fg_color=THEME["fg"], corner_radius=0, border_color=THEME["accent"], border_width=1)
        block.pack(fill="x")
        block.grid_rowconfigure(0, weight=1)
        block.grid_rowconfigure(1, weight=1)
        block.grid_columnconfigure(0, weight=10)
        block.grid_columnconfigure(1, weight=1)

        var = ctk.StringVar()

        entry = ctk.CTkEntry(block, fg_color=THEME["fg"], justify="left", placeholder_text="", corner_radius=0, textvariable=var, border_color=THEME["muted"])
        entry.grid(row=0, column=0, columnspan=1, sticky="nsew")
        var.trace_add("write", lambda *args: self.on_edit())
        entry.bind("<Return>", self.on_enter)
        entry.bind("<KP_Enter>", self.on_enter)

        entry.insert(0, code)

        result = ctk.CTkLabel(block, fg_color=THEME["fg"], anchor="e", text="= 0", text_color=THEME["accent"])
        result.grid(row=1, column=0, columnspan=2,sticky="nsew")

        delete = ctk.CTkButton(block, width=1, fg_color=THEME["fg"], text_color=THEME["text"], text="❌", hover_color=THEME["muted"])
        delete.grid(row=0, column=1, sticky="nsew")

        b = Block(block, delete, entry, result, self.remove_block)

        self.blocks.append(b)

        return b

    def remove_block(self, block):
        self.blocks.remove(block)

    def refresh_code(self):
        self.code = ""
        for block in self.blocks:
            if len(block.entry.get()) > 0:
                self.code += block.entry.get()
                self.code += ';'
        self.code = self.code.removesuffix(';')

    def on_edit(self):
        self.refresh_code()
        try:
            p = Parser(Lexer(self.code).tokens)
            vs = p.parse_all()
            ev = Evaluator(order(vs), p.functions)
            ev.eval()
            for b in self.blocks:
                name: str = b.entry.get().split('=')[0].strip()
                for n, f in ev.functions.items():
                    if name.startswith(n):
                        b.result.configure(text="FUNCTION")
                if name in ev.values:
                    b.result.configure(text=f"= {ev.values[name]:.7}")
                elif name.startswith("#"):
                    b.result.configure(text="COMMENT")
        except ValueError as e:
            print(e)
            for b in self.blocks:
                name: str = b.entry.get().split('=')[0].strip()
                if name.startswith("#"):
                    b.result.configure(text="COMMENT")
                else:
                    b.result.configure(text="ERROR")

    def import_blocks(self):
        path = filedialog.askopenfilename(
            title="Open",
            filetypes=[("Data file", "*.dat"), ("All files", "*.*")]
        )

        if path:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()

            for b in self.blocks:
                b.frame.destroy()
            self.blocks.clear()

            for part in code.split(';'):
                part = part.strip()
                if part:
                    self.push_block(part)

            self.on_edit()

    def on_enter(self, *args):
        b = self.push_block()
        b.entry.focus_set()

    def theme_violet(self):
        THEME["fg"] = "#14121f"
        THEME["nav"] = "#1e1b2e"
        THEME["text"] = "#e9e7f5"
        THEME["accent"] = "#8b5cf6"
        THEME["muted"] = "#7c7a96"

        self.update_colors()

    def theme_ocean(self):
        THEME["fg"] = "#0d1b2a"
        THEME["nav"] = "#14263a"
        THEME["text"] = "#e0f2fe"
        THEME["accent"] = "#38bdf8"
        THEME["muted"] = "#6b8aa6"

        self.update_colors()

    def theme_green(self):
        THEME["fg"] = "#0b0f0c"
        THEME["nav"] = "#121a14"
        THEME["text"] = "#d9f7e3"
        THEME["accent"] = "#4ade80"
        THEME["muted"] = "#5f7d69"

        self.update_colors()

    def theme_warm(self):
        THEME["fg"] = "#16120d"
        THEME["nav"] = "#221c14"
        THEME["text"] = "#f5ecd9"
        THEME["accent"] = "#fbbf24"
        THEME["muted"] = "#8a7d66"

        self.update_colors()

    def update_colors(self):
        self.add_btn.configure(fg_color=THEME["nav"], hover_color=THEME["muted"])
        self.import_btn.configure(fg_color=THEME["nav"], hover_color=THEME["muted"])
        self.export_btn.configure(fg_color=THEME["nav"], hover_color=THEME["muted"])
        self.theme_btn.configure(fg_color=THEME["nav"], hover_color=THEME["muted"])
        self.themeframe.configure(fg_color=THEME["fg"], border_color=THEME["accent"])
        self.nav_panel.configure(fg_color=THEME["nav"], border_color=THEME["accent"])
        self.codeframe.configure(fg_color=THEME["fg"], scrollbar_button_color=THEME["nav"], scrollbar_button_hover_color=THEME["muted"])
        self.configure(fg_color=THEME["fg"])

        for block in self.blocks:
            block.frame.configure(fg_color=THEME["nav"], border_color=THEME["accent"])
            block.delete.configure(fg_color=THEME["fg"], text_color=THEME["text"], hover_color=THEME["muted"])
            block.entry.configure(fg_color=THEME["fg"], border_color=THEME["muted"])
            block.result.configure(fg_color=THEME["fg"], text_color=THEME["accent"])

        for btn in self.theme_btns:
            btn.configure(fg_color=THEME["nav"], hover_color=THEME["muted"])

    def switch_menu(self):
        if self.main_page:
            self.codeframe.pack_forget()
            self.themeframe.pack(fill="both", expand=True)
            self.main_page = False
        else:
            self.codeframe.pack(fill="both", expand=True)
            self.themeframe.pack_forget()
            self.main_page = True

a = App()
a.theme_ocean()
a.mainloop()

# Приклад молярної маси
"""
M(len) = sum_(n=0)^(len-1)_(table(atoms(n)));table(k) = { k == 72 : 1 : { k == 79 : 16 : { k == 78 : 14 : { k == 67 : 12 : 0 }}}};atoms(n) = { n == 0 : 72 : { n == 1 : 72 : { n == 2 : 79 : 0 }}};# молярна маса молекули "atoms" #;a = M(3)
"""

# Вбудоване
"""
a = 2;b = 8;# вбудовані функції #;mx = max(a, b);mn = min(a, b);lg = log_(a)^(b);sm = sum_(n=1)^(5)_(n);pd = prod_(n=1)^(5)_(n);# тригонометрія #;alpha  = 30;rad = alpha * pi / 180;sn = sin rad;cs = cos rad;tg = tan rad;asn = asin sn;acs = acos cs;atn = atan tg;# інше #;c = -1;abss = mod c
"""
