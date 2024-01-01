#同样这里是供自己学习的，目前的compiler并未采用这个，只是用于学习四元式的生成和执行
#四元式的生成在语法分析那里穿插了，解释执行在解释程序那块
# 定义优先级
def precedence(op):
    if op == '(':
        return 0
    elif op in ['+', '-']:
        return 1
    elif op in ['*', '/']:
        return 2
    else:
        return 3

# 四元式生成函数
def generate_quadruples(expressions):
    temp_count = 1  # 用于生成临时变量
    quadruples = [] # 存储生成的四元式
    for expr in expressions:
        op_stack = []  # 运算符栈
        val_stack = [] # 变量栈
        for token in expr:
            if token.isalpha() or token.isdigit():
                val_stack.append(token)
            elif token == '(':
                op_stack.append(token)
            elif token == ')':
                while op_stack and op_stack[-1] != '(':
                    op2 = val_stack.pop()
                    op1 = val_stack.pop()
                    op = op_stack.pop()
                    temp_var = f't{temp_count}'
                    temp_count += 1
                    quadruples.append((op, op1, op2, temp_var))
                    val_stack.append(temp_var)
                op_stack.pop()  # 弹出 '('
            else:
                while op_stack and precedence(op_stack[-1]) >= precedence(token):
                    op2 = val_stack.pop()
                    op1 = val_stack.pop()
                    op = op_stack.pop()
                    temp_var = f't{temp_count}'
                    temp_count += 1
                    quadruples.append((op, op1, op2, temp_var))
                    val_stack.append(temp_var)
                op_stack.append(token)
        # 处理赋值运算符
        if expr[1] == '=':
            right_val = val_stack.pop() if val_stack else '_'
            left_var = expr[0]
            quadruples.append(('=', left_var, '_', right_val))
    return quadruples

# 示例
expressions = [
    ['k', '=', 'h'],
    ['a', '=', 'b', '+', 'c', '*', 'd'],
    ['e', '=', 'f', '/', 'g']
]
quadruples = generate_quadruples(expressions)
for quad in quadruples:
    print(quad)
