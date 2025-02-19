from graphviz import Digraph

class AFDState:
    def __init__(self, state_number):
        self.state_number = state_number
        self.is_final = False
        self.transitions = {}
    def __repr__(self):
        return f"State({self.state_number})"

class DFA:
    def __init__(self, transition_table, acceptance_states):
        self.states = {}
        self.start_state = None
        self.final_states = set()
        self.transition_table = self._clean_transition_table(transition_table)
        self.acceptance_states = acceptance_states
        self._construct_dfa()

    def _clean_transition_table(self, transition_table):
        cleaned_table = {}
        for state_id, data in transition_table.items():
            cleaned_table[state_id] = {
                "transitions": {symbol: next(iter(target)) if isinstance(target, set) else target 
                                for symbol, target in data["transitions"].items()}
            }
        print("Cleaned table: ", cleaned_table)
        return cleaned_table

    def _construct_dfa(self):
        for state_id in self.transition_table:
            state = AFDState(state_id)
            if state_id in self.acceptance_states:
                state.is_final = True
                self.final_states.add(state)
            self.states[state_id] = state
            
        self.start_state = self.states[0]  # Assumption: initial state is always 0
        
        for state_id, transitions in self.transition_table.items():
            for symbol, target_id in transitions["transitions"].items():
                if isinstance(target_id, set):  # Ensure target_id is a single value
                    target_id = next(iter(target_id))
                self.states[state_id].transitions[symbol] = self.states.get(target_id, None)
        for state in self.states.values():
            print(state, state.state_number, state.transitions, state.is_final)


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
                currentState = currentTransitions[char]
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
            for symbol, target_state in transitions["transitions"].items():
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


__all__ = ["DFA"]

