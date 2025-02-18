from graphviz import Digraph
class State:
    def __init__(self, state_number):
        self.state_number = state_number
        self.transitions = {}  # {symbol: set([state1, state2, ...])}
        self.epsilon_transitions = set()  # Transitions via ε
        self.is_final = False  # Todos los estados son no finales por defecto

    def __repr__(self):
        return f"State({self.state_number})"

class NFA:
    def __init__(self, start_state, final_state):
        self.start_state = start_state
        self.final_state = final_state
        self.final_state.is_final = True
        self.valid_symbols = self.collect_valid_symbols(self.start_state)

    def collect_valid_symbols(self, state):
        symbols = set()
        visited = set()

        def dfs(state):
            if state in visited:
                return
            visited.add(state)
            symbols.update(state.transitions.keys())
            for next_state in state.epsilon_transitions:
                dfs(next_state)
            for next_states in state.transitions.values():
                for next_state in next_states:
                    dfs(next_state)

        dfs(state)
        return symbols

    def draw_nfa(self, filename='nfa'):
        dot = Digraph()
        state_mapping = {}
        state_counter = 0

        def visit(state, visited):
            nonlocal state_counter
            if state in visited:
                return
            visited.add(state)

            if state not in state_mapping:
                state_mapping[state] = state_counter
                state_counter += 1

            state_name = f"State_{state.state_number}"
            if state.is_final:
                dot.node(state_name, label=str(state.state_number), shape='doublecircle')
            else:
                dot.node(state_name, label=str(state.state_number), shape='circle')

            for symbol, states in state.transitions.items():
                for next_state in states:
                    visit(next_state, visited)
                    next_state_name = f"State_{next_state.state_number}"
                    dot.edge(state_name, next_state_name, label=symbol)

            for next_state in state.epsilon_transitions:
                visit(next_state, visited)
                next_state_name = f"State_{next_state.state_number}"
                dot.edge(state_name, next_state_name, label="ε")

        visit(self.start_state, set())

        # Agregar una flecha que apunte al estado inicial
        start_state_name = f"State_{self.start_state.state_number}"
        dot.node('start', label='', shape='none', width='0', height='0')
        dot.edge('start', start_state_name)

        dot.render(filename, view=True)

    def epsilon_closure(self, states):
        closure = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            for epsilon_state in state.epsilon_transitions:
                if epsilon_state not in closure:
                    closure.add(epsilon_state)
                    stack.append(epsilon_state)
                    
                    # Considerar las transiciones epsilon de los nuevos estados alcanzados
                    # Agregar a la pila todas las transiciones epsilon de epsilon_state
                    for nested_epsilon_state in epsilon_state.epsilon_transitions:
                        if nested_epsilon_state not in closure:
                            closure.add(nested_epsilon_state)
                            stack.append(nested_epsilon_state)

        return closure


    def verifyString(self, w):
        # Ensure that ε is treated as a valid symbol
        w = w.replace('ε', '')

        def dfs(current_states, w):
            # Obtener el epsilon-closure completo de los estados actuales
            current_states = self.epsilon_closure(current_states)
            print(f"Current states after epsilon closure: {[state.state_number for state in current_states]}")

            if not w:  # Si no quedan más símbolos, verifica si algún estado es final
                is_accepted = any(state.is_final for state in current_states)
                print(f"Final states: {[state.state_number for state in current_states]}")
                print(f"String accepted: {is_accepted}")
                return is_accepted

            symbol = w[0]
            print(f"Processing symbol: {symbol}")

            # Explorar todas las transiciones por el símbolo actual
            next_states_after_symbol = set()
            for state in current_states:
                if symbol in state.transitions:
                    next_states_after_symbol.update(state.transitions[symbol])

            # Obtener el epsilon-closure de los estados alcanzados por el símbolo
            next_states_after_symbol = self.epsilon_closure(next_states_after_symbol)
            print(f"Next states after processing symbol '{symbol}': {[state.state_number for state in next_states_after_symbol]}")

            # Llamada recursiva para el siguiente símbolo
            return dfs(next_states_after_symbol, w[1:]) if next_states_after_symbol else False

        initial_states = {self.start_state}
        return dfs(initial_states, w)


    def is_final_state(self, state):
        return state.is_final

# La función para crear el NFA desde el AST debe ajustarse para asignar los números de estado:
def ASTtoNFA(node, state_counter=None):
    if state_counter is None:
        state_counter = [0]

    def create_state():
        state = State(state_counter[0])
        state_counter[0] += 1
        return state

    if node.value.isalnum():  # Nodo hoja (operando)
        start_state = create_state()
        final_state = create_state()
        if node.value == "ε":
            start_state.epsilon_transitions.add(final_state)
        else:
            start_state.transitions[node.value] = {final_state}
        return NFA(start_state, final_state)

    elif node.value == '|':  # OR
        left_nfa = ASTtoNFA(node.left, state_counter)
        right_nfa = ASTtoNFA(node.right, state_counter)
        start_state = create_state()
        final_state = create_state()
        start_state.epsilon_transitions.update([left_nfa.start_state, right_nfa.start_state])
        left_nfa.final_state.is_final = False
        right_nfa.final_state.is_final = False
        left_nfa.final_state.epsilon_transitions.add(final_state)
        right_nfa.final_state.epsilon_transitions.add(final_state)
        return NFA(start_state, final_state)

    elif node.value == '~':  # Concatenación
        left_nfa = ASTtoNFA(node.left, state_counter)
        right_nfa = ASTtoNFA(node.right, state_counter)
        left_nfa.final_state.is_final = False
        left_nfa.final_state.epsilon_transitions.add(right_nfa.start_state)
        return NFA(left_nfa.start_state, right_nfa.final_state)

    elif node.value == '*':  # Kleene Star
        inner_nfa = ASTtoNFA(node.left, state_counter)
        start_state = create_state()
        final_state = create_state()
        start_state.epsilon_transitions.update([inner_nfa.start_state, final_state])
        inner_nfa.final_state.is_final = False
        inner_nfa.final_state.epsilon_transitions.update([inner_nfa.start_state, final_state])
        return NFA(start_state, final_state)
