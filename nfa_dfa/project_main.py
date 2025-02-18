from translator import getPostfixExpressionsFromFile
from nfa import ASTtoNFA
from newAst import draw_ast, postfixToAst
from dfa import NFAtoDFA
from dfa_red import DFA_Reducer

def requestWString():
    print("\nEnter the string 'w' that you want to verify")
    print("If you want to input ε, please use an underscore '_' ")
    w = input().strip()  # Strip to remove any surrounding whitespace
    w = w.replace("_", "ε")

    if w == "":
        w = "ε"
    
    print("The following string will be evaluated: ",  w)

    return w

def getOriginalExpressions(file):
    expressionList = []

    with open(file, "r", encoding="utf-8") as f:
        for x in f:
            exp = x.replace("\n", "")
            exp = exp.replace(" ", "")
            expressionList.append(exp)

    return expressionList

def testStringInDFA(w, dfa, selectedRegex):

    if w == "":
        w = "ε"

    belongs = "belongs" if dfa.verifyString(w) else "does not belong"

    print(f"The string 'w' = {w}, {belongs} to the generated lenguage by the postfix regular expression: {selectedRegex}")

def testStringinNFA(w, nfa, selectedRegex):

    if w == "":
        w = "ε"

    belongs = "belongs" if nfa.verifyString(w) else "does not belong"

    print(f"The string 'w' = {w}, {belongs} to the generated lenguage by the postfix regular expression: {selectedRegex}")

expressions = getOriginalExpressions("./nfa_dfa/regex2.txt")
print("my exp", expressions)

postfixExpressions, normalizedExpressions = getPostfixExpressionsFromFile("./nfa_dfa/regex2.txt")
print(postfixExpressions)
print(normalizedExpressions)

postfixExpressions.append("exit")


option = -1
expressionsCount = len(postfixExpressions)

while option != expressionsCount:

    print("\nWelcome, which expression do you want to test?")

    for idx, exp in enumerate(postfixExpressions):
        if exp != "exit":
            print(f"{idx + 1}. {expressions[idx]}  -->  {normalizedExpressions[idx]}  -->  {exp}")
        else:
            print(f"{idx + 1}. {exp}")
            
    option = int(input())

    if len(postfixExpressions) == option:
        break

    selectedExpression = postfixExpressions[option - 1]
    selectedRegex = expressions[option -1]
    selectedNormalReg = normalizedExpressions[option -1]
    
    ast = postfixToAst(selectedExpression)
    
    dot = draw_ast(ast)
    dot.render('ast', view=True)
    
    nfa = ASTtoNFA(ast)
    dfa = NFAtoDFA(nfa, nfa.valid_symbols)
    reducer = DFA_Reducer(dfa)
    nfa.draw_nfa('nfa')
    dfa.draw_dfa("dfa")
    red_dfa = reducer.reduce_dfa()
    red_dfa.draw_dfa("red_dfa")
    userAction = ""

    while userAction !=  "4":

        print("\nWich automaton do you wish to test")
        print("1.NFA \n2.DFA \n3.Reduced DFA \n4.Return to regex selection")
        userAction = input().strip()

        if userAction == "1":
            w = requestWString()
            testStringinNFA(w, nfa, selectedRegex)

        elif userAction == "2":
            w = requestWString()
            testStringInDFA(w, dfa, selectedRegex)
            
        elif userAction == "3":
            w = requestWString()
            testStringInDFA(w, red_dfa, selectedRegex)
            