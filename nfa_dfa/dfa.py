from nfa import State, NFA
from graphviz import Digraph

def getAlias(transitionTable, compTransition):
    for index in transitionTable:
        item = transitionTable[index]
        if item["states"] == compTransition:
            return item["alias"]

def simplifyTransitionTable(transitionTable):
    stateNames = list(transitionTable.keys())

    simplfiedTable = {}

    for index in transitionTable:
         
        simplfiedTable[index] = {}

        transitions = transitionTable[index]["transitions"]

        for char in transitions:
            if transitions[char] != " ":
                completeTransition = transitions[char]
                alias = getAlias(transitionTable, completeTransition)
                simplfiedTable[index].update( {char : alias})
            else:
                simplfiedTable[index].update( {char : " "})
    return simplfiedTable
             

def setAlreadyInTable(transitionTable, setB):
    transitionTableLength = len(transitionTable)

    # The table is empty so the set is garanteed to not exist on the table
    # if transitionTableLength == 0:
    #     print("Current state of 'transitions in false': ", transitionTable)
    #     return False
    
    print("Current state of 'transitions in true': ", transitionTable)
    for index in transitionTable:

        if transitionTable[index]["states"] - setB == set():
            return True
    
    return False

def move(setOfStates, alfabetSymbol):
    print("\nTesting: ", setOfStates)
    print("I have to check the immediate transitions with the symbol", alfabetSymbol)

    statesItCanTransitionTo = set()

    for state in setOfStates:
        stateTransitionChars = list(state.transitions.keys())

        if alfabetSymbol in stateTransitionChars:
            possibleStates = state.transitions[alfabetSymbol]

            for item in possibleStates:
                statesItCanTransitionTo.add(item)

    return statesItCanTransitionTo
        
def NFAtoDFA(nfa: NFA, alfabet):

    # A list of sets, here i want to store all the sets that are generated with the epsilon(move()) 
    groupedTransitionsList = set()

    # This will be useful to determine which have alredy been checked
    evaluatedSets = set()

    # I also need a structure to store the transitions (Dictionary Maybe?)
    transitionTable = {}

    # First, get the epsilon transition for the initial state
    initialStateList = [nfa.start_state]
    initialClosure = frozenset(nfa.epsilon_closure(initialStateList))
    groupedTransitionsList.add(initialClosure)

    nonEvaluatedSets = groupedTransitionsList - evaluatedSets

    tableCounter = 0

    while nonEvaluatedSets != set():
        # Getting any of the not evaluated sets
        selectedSet = next(iter(nonEvaluatedSets))

        print("\ncurrent table counter", tableCounter)
    
        transitionTable[tableCounter] = {"alias": tableCounter, "states": set(selectedSet), "transitions": {}}

        for char in alfabet:
            moveResult = move(selectedSet, char)
            print(f"With char {char}, the set moves to {moveResult}")

            if moveResult == set():
                print("No transition found with char: ", char)
                print("transit:", transitionTable[tableCounter])
                transitionTable[tableCounter]["transitions"].update({char: " "})
            else:
                epsClosure = nfa.epsilon_closure(moveResult)
                print("Applying epsilon closure to move we get: ", epsClosure)
                groupedTransitionsList.add(frozenset(epsClosure))

                # Aqui lo que tengo que hacer es ver si este ya se encuentra entre los set, si ya se encuentra obtener su alias.?
                # Find alias of the state after epsilon closure
                print("the transition table:: ", transitionTable)
                print("the closure:: ", epsClosure)
                    
                alias = getAlias(transitionTable, epsClosure)
                print("Alias for the new set:: ", alias)

                transitionTable[tableCounter]["transitions"].update({char: epsClosure})

            print()
        print("---------------")

        evaluatedSets.add(selectedSet)

        # Check if there are new sets/group of states to check transitions in the while loop
        nonEvaluatedSets = groupedTransitionsList - evaluatedSets
        tableCounter += 1

    print("Hi")
    print(alfabet)
    print(initialClosure)
    print(transitionTable)

    # Simplify transition table
    simpleTable = simplifyTransitionTable(transitionTable)
    print("Simplified Transition Table:")
    print(simpleTable)

    # Creating DFA states from simplified table
    dfa_states = {}
    for alias, transitions in simpleTable.items():
        state = State(alias)  # Create a new DFA state
        dfa_states[alias] = state

    # Creating DFA transitions based on simplified transition table
    for alias, transitions in simpleTable.items():
        current_state = dfa_states[alias]
        for symbol, next_state_alias in transitions.items():
            if next_state_alias != " ":
                current_state.transitions[symbol] = {dfa_states[next_state_alias]}

    # Determining the DFA start state and final states
    dfa_start_state = dfa_states[0]  # The initial DFA state corresponds to alias 0
    dfa_final_states = set()

    for alias, details in transitionTable.items():
        for nfa_state in details["states"]:
            if nfa_state.is_final:  # If any NFA state in the group is final, mark the DFA state as final
                dfa_states[alias].is_final = True
                dfa_final_states.add(dfa_states[alias])

    # Return the DFA object
    return DFA(dfa_start_state, dfa_final_states, simpleTable)



class DFA:
    def __init__(self, start_state, final_states, transition_table):
        self.start_state = start_state  # This is a State object
        self.final_states = final_states  # Set of State objects
        self.transition_table = transition_table  # Simplified transition table with aliases
        self.valid_symbols = list(next(iter(transition_table.values())).keys())  # Symbols used in transitions

    def verifyString(self, w):

        # A queue to show how the string is being consumed
        wordQueue = list(w)
        currentState = self.start_state
        currentTransitions = currentState.transitions

        print("\nChecking th String: ", w)

        for char in w:
            #Deleting the first element of the queue 
            print()
            print(f"Current state of the string: {wordQueue}, consuming: {char}")
            print("Current state: ", currentState)
            print("Avaiable transitions", currentTransitions)
            wordQueue.pop(0)
            currentStateCharTransitions = list(currentTransitions.keys())

            if char == "ε":
                print("No transition made, found ε character")

            elif char in currentStateCharTransitions:
                print(f"{currentState} has transition with: {char}")
                currentState = next(iter(currentTransitions[char]))
                print("Transitioning to state: ", currentState)
                currentTransitions = currentState.transitions
            
            else:
                print(f"{currentState} has no transitions with: {char}")
                return False
        
        #If the string makes it out of the loop, the entire string was consumed and we check if the state is final 
        if currentState.is_final:
            return True
        
        #If not return false
        return False


    def draw_dfa(self, filename='dfa'):
        dot = Digraph()
        state_mapping = {}  # To map state numbers to node names in the Graphviz diagram

        # Create nodes for each state
        for state_alias in self.transition_table:
            state_name = f"State_{state_alias}"
            if state_alias in [state.state_number for state in self.final_states]:
                dot.node(state_name, label=str(state_alias), shape='doublecircle')
            else:
                dot.node(state_name, label=str(state_alias), shape='circle')
            state_mapping[state_alias] = state_name

        # Add edges for transitions
        for state_alias, transitions in self.transition_table.items():
            state_name = state_mapping[state_alias]
            for symbol, target_state in transitions.items():
                if target_state != " ":
                    target_state_name = state_mapping[target_state]
                    dot.edge(state_name, target_state_name, label=symbol)

        # Add an arrow pointing to the start state
        start_state_alias = self.start_state.state_number  # Get the alias of the start state (the number)
        start_state_name = state_mapping[start_state_alias]  # Now get the corresponding name in the Graphviz diagram
        dot.node('start', label='', shape='none', width='0', height='0')
        dot.edge('start', start_state_name)

        # Render the DFA to a file
        dot.render(filename, view=True)

    
    

