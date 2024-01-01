### 中途学习为目的，如果有需要可以实现这个抽象语法树的

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}  # 符号表

    def analyze(self, node):
        # 根据节点类型进行不同的语义分析
        if node.type == 'Assignment':
            self.process_assignment(node)
        elif node.type == 'BinaryOperation':
            self.process_binary_operation(node)
        # ... 其他节点类型的处理

    def process_assignment(self,node):
        # 处理赋值语句
        var_name=node.left.value
        var_value=node.right.value
        var_type=self.get_type(node.right)  # 使用 get_type 方法来确定右侧表达式的类型
        if var_name in self.symbol_table:
            # 变量已经声明，检查类型等语义规则
            expected_type=self.symbol_table[var_name]
            if expected_type!=var_type:
                raise TypeError(f"变量 '{var_name}' 的类型不匹配: 预期 {expected_type}, 实际 {var_type}")
        else:
            # 变量未声明，报错或者在符号表中添加新条目
            self.symbol_table[var_name]=var_type

    def process_binary_operation(self,node):
        # 处理二元运算
        left_type=self.get_type(node.left)
        right_type=self.get_type(node.right)

        # 类型转换规则
        if left_type=='int' and right_type=='float':
            left_type='float'
        elif left_type=='float' and right_type=='int':
            right_type='float'
        # 添加更多类型转换规则...

        # 检查转换后的类型是否匹配
        if left_type!=right_type:
            raise TypeError("类型不匹配")

        # 返回结果类型
        return left_type if left_type==right_type else None

    def get_type(self,node):
        if node.type=='Variable':
            # 如果节点是变量，从符号表中获取类型
            var_name=node.value
            if var_name in self.symbol_table:
                return self.symbol_table[var_name]
            else:
                raise NameError(f"未声明的变量: {var_name}")
        elif node.type=='Constant':
            # 如果节点是常量，根据值的类型返回类型
            if isinstance(node.value,int):
                return 'int'
            elif isinstance(node.value,float):
                return 'float'
        # ... 其他类型的判断

# 示例：语法树节点
class Node:
    def __init__(self, type, value, left=None, right=None):
        self.type = type
        self.value = value
        self.left = left
        self.right = right

# 构建语法树并进行语义分析
assignment_node = Node('Assignment', '=', Node('Variable', 'x'), Node('Constant', 42))
binary_op_node = Node('BinaryOperation', '+', Node('Variable', 'x'), Node('Constant', 3.14))

semantic_analyzer = SemanticAnalyzer()
semantic_analyzer.analyze(assignment_node)
semantic_analyzer.analyze(binary_op_node)

