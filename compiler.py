# 主编译器脚本 compiler.py

from cifafenxi import Lexer
from yufafenxi import Parser
from jieshichengxu import Interpreter


class Compiler:
    def __init__(self,code):
        self.code=code
        self.lexer=Lexer()#词法分析
        self.tokens = self.lexer.tokenize(code)#生成令牌
        self.parser=Parser(self.tokens)
        self.interpreter=Interpreter(self.parser.quadruples)

    def compile(self):
        # 语法分析、语义分析、四元式生成
        print(self.tokens)
        self.parser.program()
        print(self.parser.symbol_table.table)
        print(self.parser.quadruples)
        # 解释执行
        result = self.interpreter.execute()

        return result

#读取存放代码的txt文件
with open("code1.txt","r",encoding="utf-8") as f :
    code = f.read()
print(code)

# 创建编译器实例
compiler=Compiler(code)

# 执行编译过程
result=compiler.compile()
#展示运行结果
for var,value in result.items():
    print(f"{var} = {value}")
