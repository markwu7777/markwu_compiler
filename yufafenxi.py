#穿插的语义分析，当下只有符号表
class SymbolTable:
    def __init__(self):
        self.table = {}

    def add(self, identifier, info):
        self.table[identifier] = info

    def lookup(self, identifier):
        return self.table.get(identifier, None)

#语法分析，以令牌匹配形式结合递归下降实现
class Parser:
    def __init__(self, tokens):
        # 初始化解析器，tokens是词法分析器输出的令牌列表
        self.tokens = tokens + [('END', -1)]  # 在令牌列表末尾添加结束标记
        self.index = 0
        self.lookahead = self.tokens[self.index]
        self.bracket_stack = []  # 用于跟踪括号匹配的栈
        self.symbol_table=SymbolTable()  # 创建符号表实例
        self.quadruples=[]  # 创建四元式列表
        self.label_counter = 0

    def match(self, expected_type):
        # 如果当前令牌是结束标记，则检查括号是否匹配
        if self.lookahead[0] == 'END':
            if self.bracket_stack:
                raise SyntaxError("括号没有正确匹配")
            return
        # 匹配当前令牌类型，如果匹配则消耗令牌，否则抛出语法错误
        if self.lookahead[0] == expected_type:
            # 如果是左括号或左大括号，推入栈中
            if self.lookahead[1] in ['(', '{']:
                self.bracket_stack.append(self.lookahead[1])
            # 如果是右括号或右大括号，从栈中弹出并检查匹配
            elif self.lookahead[1] in [')', '}']:
                if not self.bracket_stack or \
                   (self.lookahead[1] == ')' and self.bracket_stack[-1] != '(') or \
                   (self.lookahead[1] == '}' and self.bracket_stack[-1] != '{'):
                    raise SyntaxError("括号没有正确匹配")
                self.bracket_stack.pop()
            self.index += 1
            if self.index < len(self.tokens):
                self.lookahead = self.tokens[self.index]
            else:
                self.lookahead = None
        else:
            raise SyntaxError(f"预期的 {expected_type}，但是得到了 {self.lookahead[0]}")

    def new_label(self):
        self.label_counter+=1
        return f"label{self.label_counter}"

    def get_label(self):
        return  f"label{self.label_counter}"

    def program(self):
        # 解析程序，即一系列函数定义
        while (self.lookahead and self.lookahead[0] != 'END'):  # 检查是否到达结束标记
            self.function_definition()
        # 到达结束标记，解析结束

    def function_definition(self):
        # 解析函数定义
        self.type()
        self.match("IDENTIFIER")
        self.match("DELIMITER")
        self.parameter_list()
        self.match("DELIMITER")
        self.compound_statement()

    def type(self):
        # 检查当前令牌是否为数据类型关键字，并消耗它
        if self.lookahead[0] == "RESERVE_WORD" and self.lookahead[1] in ["int", "float", "char", "void"]:
            type_name = self.lookahead[1]
            self.match("RESERVE_WORD")
            return type_name
        else:
            raise SyntaxError("预期的数据类型关键字")

    def parameter_list(self):
        # 解析参数列表
        if self.lookahead and self.lookahead[0] == "RESERVE_WORD":
            self.parameter_declaration()
            while self.lookahead and self.lookahead[0] == "DELIMITER" and self.lookahead[1] == ",":
                self.match("DELIMITER")
                self.parameter_declaration()

    def parameter_declaration(self):
        # 解析单个参数声明
        self.type()
        self.match("IDENTIFIER")

    def compound_statement(self):
        # 解析复合语句，即由大括号包围的语句块
        self.match("DELIMITER")
        # 确保声明列表和语句列表方法存在
        self.declaration_list()
        self.statement_list()
        self.match("DELIMITER")

    def declaration_list(self):
        # 解析声明列表
        while self.lookahead[0] == "RESERVE_WORD":
            self.declaration()

    def declaration(self):
        # 解析单个声明
        var_type=self.type()  # 获取变量的类型
        identifier=self.lookahead[1]
        self.match("IDENTIFIER")
        self.match("DELIMITER")
        # 将变量添加到符号表，使用解析到的类型
        self.symbol_table.add(identifier,{'type':var_type,'scope':'local'})

    def statement_list(self):
        # 解析语句列表
        while self.lookahead and self.lookahead[0] in ["IDENTIFIER","RESERVE_WORD","DELIMITER"]:
            # 如果遇到右大括号，立即返回
            if self.lookahead[0]=="DELIMITER" and self.lookahead[1]=="}":
                return
            self.statement()  # 解析单个语句

    def statement(self):
        # 解析单个语句
        if self.lookahead[0] == "IDENTIFIER":
            self.expression_statement()
        elif self.lookahead[1] in ["if", "while"]:
            self.control_statement()
        elif self.lookahead[0] == "DELIMITER" and self.lookahead[1] == "{":
            self.compound_statement()
        else:
            self.match("DELIMITER")

    def expression_statement(self):
        # 解析表达式语句
        self.expression()
        # 确保每个表达式语句后面都有一个分号
        print(self.lookahead[0])
        if self.lookahead[0]!="DELIMITER" or self.lookahead[1]!=';':
            raise SyntaxError("缺少语句结束符号 ';' ")
        self.match("DELIMITER")  # 匹配分号

    def control_statement(self):
        # 解析控制语句
        if self.lookahead[1]=="if":
            self.if_statement()
        elif self.lookahead[1]=="while":
            self.while_statement()
        else:
            raise SyntaxError("未知的控制语句")
    def expression(self):
        # 解析表达式
        return self.assignment_expression()

    def assignment_expression(self):
        # 解析赋值表达式
        if self.lookahead[0]=="IDENTIFIER":
            identifier=self.lookahead[1]
            if not self.symbol_table.lookup(identifier):
                raise SyntaxError(f"未声明的变量 '{identifier}' 使用")
            self.match("IDENTIFIER")
            if self.lookahead[1] in ['++','--']:
                operator=self.lookahead[1]
                self.match("OPERATOR")
                # 创建并返回四元式
                quad=(self.new_label(),operator,identifier,None,identifier)
                self.quadruples.append(quad)  # 将四元式添加到列表中
                return quad
            else:
                self.match("OPERATOR")  # 匹配赋值操作符
                # 确保赋值操作符后面有一个有效的表达式
                if self.lookahead[0] not in ["IDENTIFIER","CONSTANT"]:
                    raise SyntaxError("赋值操作符后缺少表达式")
                # 处理右侧的表达式
                right_hand_side=self.additive_expression()
                # 创建并返回赋值四元式
                assign_quad=(self.new_label(),'=',right_hand_side,None,identifier)
                self.quadruples.append(assign_quad)  # 将四元式添加到列表中
                return assign_quad
        else:
            self.logical_expression()  # 处理逻辑表达式

    def logical_expression(self):
        # 首先检查是否有逻辑非运算符 '!'
        left=self.relational_expression()  # 解析第一个关系表达式
        while self.lookahead[0]=="OPERATOR" and self.lookahead[1] in ["!","||","&&"]:
            operator=self.lookahead[1]
            self.match("OPERATOR")
            if operator=="!":
                # 对于逻辑非运算符，不需要解析右操作数
                right=None
            else:
                right=self.relational_expression()  # 解析下一个关系表达式
            temp_var=self.new_temp()  # 创建新的临时变量
            quad=(self.new_label(),operator,left,right,temp_var)  # 创建四元式
            self.quadruples.append(quad)  # 将四元式添加到列表中
            left=temp_var  # 更新左侧表达式为临时变量
        return left  # 返回逻辑表达式的结

    def relational_expression(self):
        left=self.additive_expression()
        while self.lookahead[0]=="OPERATOR" and self.lookahead[1] in ["<",">","==","<=",">=","!="]:
            operator=self.lookahead[1]
            self.match("OPERATOR")
            right=self.additive_expression()
            temp_var=self.new_temp()
            quad=(self.new_label(),operator,left,right,temp_var)
            self.quadruples.append(quad)
            left=temp_var
        return left

    def additive_expression(self):
        # 解析加减表达式并返回四元式
        left=self.multiplicative_expression()  # 解析第一个乘除表达式
        while self.lookahead[0]=="OPERATOR" and self.lookahead[1] in ["+","-","++","--"]:
            operator=self.lookahead[1]
            self.match("OPERATOR")
            if operator in ["++","--"]:
                # 对于一元运算符 '++' 和 '--'，不需要解析右操作数
                right='1'
            else:
                # 检查下一个令牌是否是一个有效的操作数
                if self.lookahead[0] not in ["IDENTIFIER","CONSTANT"]:
                    raise SyntaxError("加法或减法操作符后缺少操作数")
                right=self.multiplicative_expression()  # 解析下一个乘除表达式
            temp_var=self.new_temp()  # 创建新的临时变量
            quad=(self.new_label(),operator,left,right,temp_var)  # 创建四元式
            self.quadruples.append(quad)  # 将四元式添加到列表中
            left=temp_var  # 更新左侧表达式为临时变量
        return left  # 返回加减表达式的结果

    def multiplicative_expression(self):
        # 解析乘除表达式并返回四元式
        left=self.factor()  # 解析第一个因子
        while self.lookahead[0]=="OPERATOR" and self.lookahead[1] in ["*","/"]:
            operator=self.lookahead[1]
            self.match("OPERATOR")
            right=self.factor()  # 解析下一个因子
            temp_var=self.new_temp()  # 创建新的临时变量
            quad=(self.new_label(),operator,left,right,temp_var)  # 创建四元式
            self.quadruples.append(quad)  # 将四元式添加到列表中
            left=temp_var  # 更新左侧因子为临时变量
        return left  # 返回乘除表达式的结果

    def while_statement(self):
        self.match("RESERVE_WORD")
        self.match("DELIMITER")
        condition=self.logical_expression()  # 解析循环条件
        self.match("DELIMITER")
        begin_label = self.get_label()
        start_label=self.new_label()  # 创建循环开始的标签
        #self.quadruples.append((None,None,None,start_label))  # 将标签添加到四元式列表中
        self.quadruples.append((start_label,'jfalse',condition,None,None))  # 创建条件跳转的四元式，跳转地址暂时留空
        jump_location=len(self.quadruples)-1  # 记录需要回填的四元式的位置
        self.match("DELIMITER")
        self.statement_list()  # 解析循环体中的多条语句
        self.match("DELIMITER")
        self.quadruples.append((self.new_label(),'jump',None,None,begin_label))  # 创建无条件跳转的四元式
        end_label=self.new_label()  # 创建循环结束的标签
        self.quadruples.append((end_label,None,None,None,end_label))  # 将标签添加到四元式列表中
        self.quadruples[jump_location]=(start_label,'jfalse',condition,None,end_label)  # 回填跳转地址

    def if_statement(self):
        self.match("RESERVE_WORD")  # 匹配 "if"
        self.match("DELIMITER")  # 匹配 "("
        condition=self.logical_expression()  # 解析 if 条件
        self.match("DELIMITER")  # 匹配 ")"
        start_label = self.new_label()
        self.quadruples.append((start_label,'jfalse',condition,None,None))  # 创建条件跳转的四元式，跳转地址暂时留空
        jump_location=len(self.quadruples)-1  # 记录需要回填的四元式的位置
        self.match("DELIMITER")  # 匹配 "{"
        self.statement_list()  # 解析 if 语句体中的多条语句
        self.match("DELIMITER")  # 匹配 "}"
        end_label=self.new_label()  # 创建 if 条件为假时的标签
        self.quadruples.append((end_label,'jump',None,None,end_label))  # 创建无条件跳转的四元式，跳转地址暂时留空
        jump_location2=len(self.quadruples)-1  # 记录需要回填的四元式的位置
        self.quadruples[jump_location]=(start_label,'jfalse',condition,None,end_label)  # 回填跳转地址

        # 检查是否有 "else" 或 "else if"
        while self.lookahead and self.lookahead[1] in ["else"]:
            self.match("RESERVE_WORD")  # 匹配 "else"
            if self.lookahead and self.lookahead[1]=="if":
                self.if_statement()  # 如果是 "else if"，则递归调用 if_statement 函数
            else:
                self.match("DELIMITER")  # 匹配 "{"
                self.statement_list()  # 解析 else 语句体中的多条语句
                self.match("DELIMITER")  # 匹配 "}"
        self.quadruples[jump_location2]=(end_label,'jump',None,None,self.new_label())  # 回填跳转地址
        self.quadruples.append((self.get_label(),None,None,None,None))
    def factor(self):
        # 解析因子并返回四元式或常数值
        if self.lookahead[0]=="DELIMITER" and self.lookahead[1]=="(":
            self.match("DELIMITER")
            expr_quad=self.expression()
            self.match("DELIMITER")
            return expr_quad
        elif self.lookahead[0]=="IDENTIFIER":
            identifier=self.lookahead[1]
            if not self.symbol_table.lookup(identifier):  # 检查符号表
                raise SyntaxError(f"未声明的变量 '{identifier}' 使用")
            self.match("IDENTIFIER")
            return identifier  # 返回标识符名称
        elif self.lookahead[0]=="CONSTANT":
            constant_value=self.lookahead[1]
            self.match("CONSTANT")
            return constant_value  # 返回常数值

    def new_temp(self):
        # 生成新的临时变量名称
        if not hasattr(self,'temp_count'):
            self.temp_count=0  # 初始化临时变量计数器
        temp_name=f"t{self.temp_count}"  # 根据计数器生成临时变量名称
        self.temp_count+=1  # 增加计数器
        return temp_name  # 返回新的临时变量名称

if __name__ == '__main__':
    tokens = [
        ('RESERVE_WORD','int'),
        ('IDENTIFIER','main'),
        ('DELIMITER','('),
        ('DELIMITER',')'),
        ('DELIMITER','{'),
        ('RESERVE_WORD','int'),
        ('IDENTIFIER','number'),
        ('DELIMITER',';'),
        ('RESERVE_WORD','int'),
        ('IDENTIFIER','a'),
        ('DELIMITER',';'),
        ('IDENTIFIER','number'),
        ('OPERATOR','='),
        ('CONSTANT','10'),
        ('DELIMITER',';'),
        ('RESERVE_WORD','if'),
        ('DELIMITER','('),
        ('IDENTIFIER','number'),
        ('OPERATOR','>'),
        ('CONSTANT','0'),
        ('DELIMITER',')'),
        ('DELIMITER','{'),
        ('IDENTIFIER','a'),
        ('OPERATOR','='),
        ('IDENTIFIER','number'),
        ('DELIMITER',';'),
        ('DELIMITER','}'),
        ('RESERVE_WORD','else'),
        ('DELIMITER','{'),
        ('IDENTIFIER','a'),
        ('OPERATOR','='),
        ('CONSTANT','2'),
        ('DELIMITER',';'),
        ('DELIMITER','}'),
        ('DELIMITER','}')
    ]



    # 创建解析器实例
    parser = Parser(tokens)

    # 开始解析

    parser.program()
    print(parser.symbol_table.table)
    # 如果没有抛出SyntaxError异常，说明解析成功
    print("解析成功！")
    print(parser.quadruples)
