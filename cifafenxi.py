class Lexer:
    def __init__(self):
        # 定义保留字和运算符
        self.reserve_words = ["if", "else", "while", "return", "int"]
        self.operators = ["+", "-", "*", "/", "=", "==", "!=", "<", "<=", ">", ">=", "&&", "||", "!","++","--"]
        self.delimiters = [";", ",", "(", ")", "{", "}"]
        self.token = ""
        self.tokens = []

    def is_reserve(self, word):
        return word in self.reserve_words

    def is_operator(self, char):
        return char in self.operators

    def is_delimiter(self, char):
        return char in self.delimiters

    def tokenize(self, code):
        i = 0
        while i < len(code):
            if code[i].isspace():
                i += 1
                continue
            elif code[i].isalpha():  # 开始是字母，可能是保留字或者变量名
                start = i
                while i < len(code) and (code[i].isalpha() or code[i].isdigit()):
                    i += 1
                word = code[start:i]
                if self.is_reserve(word):
                    self.tokens.append(("RESERVE_WORD",word))
                else:
                    self.tokens.append(("IDENTIFIER",word))
            elif code[i].isdigit():  # 开始是数字，可能是常数
                start = i
                while i < len(code) and code[i].isdigit():
                    i += 1
                self.tokens.append(("CONSTANT",code[start:i]))
            elif self.is_operator(code[i]):
                op=code[i]
                if i+1<len(code) and self.is_operator(code[i:i+2]):  # 检查是否是两个字符的运算符
                    op=code[i:i+2]
                    i+=2
                else:
                    i+=1
                self.tokens.append(("OPERATOR",op))
            elif self.is_delimiter(code[i]):  # 可能是分隔符
                self.tokens.append(("DELIMITER",code[i]))
                i += 1
            else:
                raise SyntaxError(f"无法识别的字符: {code[i]}")

        return self.tokens
###对应的文法，当然在语法分析用
"""
    code = 
    P -> FD P | ε
    FD -> T ID '(' PL ')' CS
    T -> 'int' | 'float' | 'char' | 'void'
    PL -> PD PL' | ε
    PL' -> ',' PD PL' | ε
    PD -> T ID
    CS -> '{' DL SL '}'
    DL -> D DL | ε
    D -> T ID ';'
    SL -> S SL | ε
    S -> ES | CS | ';' | CS
    ES -> E ';'
    CS -> 'if' '(' E ')' S | 'while' '(' E ')' S
    E -> AE
    AE -> ID '=' AE | LE
    LE -> LE '||' RE | RE
    RE -> RE '&&' AE | AE
    AE -> AE '+' ME | AE '-' ME | ME
    ME -> ME '*' F | ME '/' F | F
    F -> '(' E ')' | ID | CONST
"""
if __name__ == '__main__' :
    code = "int main() {int number;int a;number = 10;if (number > 0) {a = number;}else {a = 2;}}"
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    for token in tokens:
        print(token)
