from graphviz import Digraph

class ASTNode:
    def __init__(self, value: str, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
        self.isNullable = False
        self.position = 0
        self.firstPos = {}
        self.lastPos = {}
        self.NextPos = {}

class AST:
    def __init__(self, postfix_expression: str):
        self.root = self.postfixToAst(postfix_expression)

    def postfixToAst(self, postfix):
        stack = []

        for char in postfix:
            if char.isalnum() or char == "ε" or char == "#":
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
    
    def add_position_to_leaves(self):

        def position_for_node(root: ASTNode, pos_counter) -> None:

            # If node is null, return
            if (not root):
                return

            # If node is leaf node, 
            # print its data
            if (not root.left and not root.right):

                root.position = pos_counter[0]
                pos_counter[0] += 1
                print(f"{root.value},{root.position}", end = " ")
                
                return

            # If left child exists, 
            # check for leaf recursively
            if root.left:
                position_for_node(root.left, pos_counter)
                

            # If right child exists, 
            # check for leaf recursively
            if root.right:
                position_for_node(root.right, pos_counter)
            
        position_counter = [1]
        position_for_node(self.root, position_counter)

    
    def calculate_AST_nullability(self):

        if self.root is None:
            return
        
        def nullable(node: ASTNode):
            
            if node is None:
                return False
            
            # Post order
            left_nullable = nullable(node.left)
            right_nullable = nullable(node.right)
        
            if node.value == "ε":
                node.isNullable = True
                print(f"The node with value: {node.value} nullability is {True}")
                return True

            elif node.position != 0:
                node.isNullable = False 
                print(f"The node with value: {node.value} nullability is {False}")
                return False

            elif node.value == "|":
                # if any of the child nodes is nullable, so is the node that has the | oeprator
                node.isNullable = left_nullable or right_nullable
                print(f"The node with value: {node.value} nullability is {node.isNullable}")
                return node.isNullable
                
            
            elif node.value == "~":
                # if bothe of the childe nodes are nullable, the node with ~ is also nullable
                node.isNullable = left_nullable and right_nullable
                print(f"The node with value: {node.value} nullability is {node.isNullable}")
                return node.isNullable

            elif node.value == "*":
                node.isNullable = True
                print(f"The node with value: {node.value} nullability is {True}")
                return True

        nullable(self.root)


