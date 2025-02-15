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
    ast.draw_ast().render('ast', view=True)