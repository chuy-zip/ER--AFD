from translator import getPostfixExpressionsFromFile
from ASTNode import AST

def getOriginalExpressions(file):
    expressionList = []

    with open(file, "r", encoding="utf-8") as f:
        for x in f:
            exp = x.replace("\n", "")
            exp = exp.replace(" ", "")
            expressionList.append(exp)

    return expressionList


expressions = getOriginalExpressions("regex.txt")
print("my exp", expressions)

postfixExpressions, normalizedExpressions = getPostfixExpressionsFromFile("regex.txt")
print(postfixExpressions)
print(normalizedExpressions)

postfixExpressions.append("exit")


option = -1
expressionsCount = len(postfixExpressions)

while option != expressionsCount:

    print("\nWelcome, which expression do you want to test?")

    # WHen is say normalized i refer to translating an expression like ab? to a(b|ε)
    # That way we only have the core regex simbols |, *, + and concatenation (~)
    print("Exprossions are formatted as follows: OriginalRegex --> NormalizedRegex --> postfixRegex" )

    for idx, exp in enumerate(postfixExpressions):
        if exp != "exit":
            print(f"{idx + 1}. {expressions[idx]}  -->  {normalizedExpressions[idx]}  -->  {exp}")
        else:
            print(f"{idx + 1}. {exp}")
            
    option = int(input())

    if len(postfixExpressions) == option:
        break

    selected_postfix_expression = postfixExpressions[option - 1]
    selectedRegex = expressions[option -1]
    selectedNormalReg = normalizedExpressions[option -1]

    ast = AST(selected_postfix_expression)

    ast.add_position_to_leaves()

    print("\nCalculating nullability")
    ast.calculate_AST_nullability()

    print("\nCalculating first pos")
    ast.calculate_AST_firstPos()

    print("\nCalculating last pos")
    ast.calculate_AST_lastPos()

    print("\nCalculating next pos")
    ast.calculate_AST_nextPos()

    ast.draw_ast().render('ast', view=True)

    #Steps to success
    # 1. Concatenate # at the end (DONE)
    # 2. Create AST (DONE)
    # 3. Add a number (position) to each leaf node (DONE)
    # 4. Calculate nullability for every node (DONE)
    # 5. Calculate first pos for every node (DONE)
    # 6. Calculate last pos for every node (DONE)
    # 7. Calculate Next pos for every node (when procesing next poss a table should be made)
    # 8. With next pos table make subset construction (construccion de subconjuntos jeje) to make states
    # we will know which are acceptance states if they have the node with the "#"
    # 9. Build the dfa
    # 10. Minimize the DFA