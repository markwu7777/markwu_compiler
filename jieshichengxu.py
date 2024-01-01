class Interpreter:
    def __init__(self, quadruples):
        self.quadruples = quadruples
        self.variables = {}
        self.labels = {}

    def execute(self):
        # 首先，找出所有标签的位置
        for i, quad in enumerate(self.quadruples):
            if quad[0] and quad[0].startswith('label'):
                self.labels[quad[0]] = i

        # 然后，从第一个四元式开始执行
        i = 0
        while i<len(self.quadruples):
            quad=self.quadruples[i]
            # 提供默认值
            op=quad[1] if len(quad)>1 else None
            arg1=quad[2] if len(quad)>2 else None
            arg2=quad[3] if len(quad)>3 else None
            result=quad[4] if len(quad)>4 else None

            if op == '=':  # 赋值操作
                self.variables[result] = self.variables.get(arg1, arg1)
            elif op in ['+', '-', '*', '/']:  # 算术操作
                self.variables[result] = eval(f"{self.variables.get(arg1, arg1)} {op} {self.variables.get(arg2, arg2)}")
            elif op in ['>', '<', '==', '<=', '>=', '!=']:  # 关系操作
                self.variables[result] = eval(f"{self.variables.get(arg1, arg1)} {op} {self.variables.get(arg2, arg2)}")
            elif op == 'jfalse':  # 条件跳转
                if not self.variables.get(arg1, arg1):
                    i = self.labels[result]
                    continue
            elif op == 'jump':  # 无条件跳转
                i = self.labels[result]
                continue
            elif op in ['++', '--']:  # 自增和自减操作
                self.variables[result] = eval(f"{self.variables.get(arg1, arg1)} {op[0]} 1")

            i += 1

        return self.variables  # 返回所有变量的最终值
if __name__ == '__main__':
    quadruples = [('label1', '=', '10', None, 'number'), ('label2', '>', 'number', '0', 't0'), ('jfalse', 't0', None, 'label4'), ('label3', '=', 'number', None, 'a'), ('jump', None, None, 'label6'), ('label5', '=', '2', None, 'a')]
    # 创建解释器实例并执行四元式序列
    interpreter = Interpreter(quadruples)
    variables = interpreter.execute()

    # 打印所有变量的最终值
    for var, value in variables.items():
        print(f"{var} = {value}")
