from graphviz import Digraph

class ASTNode:
    def __init__(self, value: str, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

class AST:
    def __init__(self, postfix_expression: str):
        self.root = self.postfixToAst(postfix_expression)

    def postfixToAst(self, postfix):
        stack = []

        for char in postfix:
            if char.isalnum() or char == "ε":
                node = ASTNode(char)
                stack.append(node)
                print(f"Found {char}, pushing symbol to the stack")

            elif char in {'|', '~'}:
                right = stack.pop()
                left = stack.pop()
                node = ASTNode(char, left, right)
                stack.append(node)
                print(f"Found binary operator {char}, retrieving {right.value} and {left.value}, asigning them to the right and left childs respectively and pushing {char} to the stack")

            elif char == "*":
                left = stack.pop()
                node = ASTNode(char, left)
                stack.append(node)
                print(f"Found {char}, retrieving {left.value} and asigning it as left child, then char is pushed to the stack")

        return stack.pop()

    def draw_ast(self):
        dot = Digraph()
        
        def add_nodes_edges(node):
            if node.left:
                dot.node(str(id(node.left)), node.left.value)
                dot.edge(str(id(node)), str(id(node.left)))
                add_nodes_edges(node.left)
            if node.right:
                dot.node(str(id(node.right)), node.right.value)
                dot.edge(str(id(node)), str(id(node.right)))
                add_nodes_edges(node.right)
        
        if self.root:
            dot.node(str(id(self.root)), self.root.value)
            add_nodes_edges(self.root)
            
        return dot