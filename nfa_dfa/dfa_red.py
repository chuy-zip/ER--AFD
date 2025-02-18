import itertools
from dfa import DFA
from nfa import State

class DFA_Reducer:
    def __init__(self, dfa):
        self.dfa = dfa
        self.state_pairs = list(itertools.combinations(dfa.transition_table.keys(), 2))
        self.table = {}
        self.initial_Alias = dfa.start_state.state_number
        self.final_Alias = self.getFinalStatesAliases()
        self.equivalent_groups = {}  # Initialize equivalent groups attribute
        self.initialize_table()

    def getFinalStatesAliases(self):
        final_states = self.dfa.final_states
        return [state.state_number for state in final_states]

    def initialize_table(self):
        # Initialize the table with False (not distinguishable)
        print()
        print("start state:", self.initial_Alias)
        print("final states: ", self.final_Alias)

        for i, j in self.state_pairs:
            self.table[(i, j)] = False

        # Mark distinguishable pairs based on final states
        for i, j in self.state_pairs:
            if (i in self.final_Alias) != (j in self.final_Alias):
                self.table[(i, j)] = True

    def print_table(self):
        print(self.table)
        for (i, j), value in self.table.items():
            print(f"States {i} and {j} are {'distinguishable' if value else 'not distinguishable'}")

    def mark_distinguishable_pairs(self):
        alphabet = self.dfa.valid_symbols
        changes_made = True  # Flag to track if any changes are made

        while changes_made:
            changes_made = False  # Reset flag for each pass
            
            # Go through each pair of states
            for (i, j) in self.state_pairs:
                if self.table.get((i, j), False):
                    continue  # Skip already distinguishable pairs

                # Check if these two states are distinguishable by transitions
                distinguishable = False
                for char in alphabet:
                    next_i = self.dfa.transition_table[i].get(char, ' ')
                    next_j = self.dfa.transition_table[j].get(char, ' ')
                    
                    if (next_i == ' ' and next_j != ' ') or (next_i != ' ' and next_j == ' '):
                        distinguishable = True
                        break
                    
                    if next_i != ' ' and next_j != ' ':
                        # Check if the resulting pair is distinguishable
                        next_pair = (min(next_i, next_j), max(next_i, next_j))  # Ensure pair is in sorted order
                        if self.table.get(next_pair, False):  # If the next pair is distinguishable
                            distinguishable = True
                            break
                
                if distinguishable:
                    self.table[(i, j)] = True  # Mark the current pair as distinguishable
                    changes_made = True  # Mark that a change was made in this pass


    def group_equivalent_states(self):
        # Dictionary to store groups of equivalent (non-distinguishable) states
        equivalent_groups = {}

        # Track which states have already been grouped
        state_to_group = {}

        group_counter = 0  # To assign unique group numbers

        for (i, j), distinguishable in self.table.items():
            if not distinguishable:  # If the pair is not distinguishable
                # Check if any of the states are already part of a group
                if i in state_to_group and j in state_to_group:
                    continue  # Both are already grouped

                if i in state_to_group:
                    group_id = state_to_group[i]
                    equivalent_groups[group_id].add(j)
                    state_to_group[j] = group_id
                elif j in state_to_group:
                    group_id = state_to_group[j]
                    equivalent_groups[group_id].add(i)
                    state_to_group[i] = group_id
                else:
                    # Create a new group for both states
                    equivalent_groups[group_counter] = {i, j}
                    state_to_group[i] = group_counter
                    state_to_group[j] = group_counter
                    group_counter += 1

        # Save the equivalent groups in a class attribute for future access
        self.equivalent_groups = equivalent_groups

        # Print out the equivalent groups for debugging
        print("\nEquivalent Groups (Non-Distinguishable States):")
        for group_id, group in equivalent_groups.items():
            print(f"Group {group_id}: {group}")
        
    def construct_reduced_dfa(self):
        # 1. Create a mapping of old states to new states based on equivalent groups
        state_mapping = {}  # Maps old states to their new state in the reduced DFA
        new_state_counter = 0  # Counter for new states

        # Step 1: For each group of equivalent states, map them to a single new state
        for group in self.equivalent_groups.values():
            new_state_alias = new_state_counter
            new_state_counter += 1
            for state in group:
                state_mapping[state] = new_state_alias

        # Handle states that were not part of any group (distinguishable states)
        for state in self.dfa.transition_table.keys():
            if state not in state_mapping:
                state_mapping[state] = new_state_counter
                new_state_counter += 1

        print("State Mapping (old -> new):", state_mapping)

        # 2. Create new State instances for the reduced DFA
        new_states = {alias: State(alias) for alias in state_mapping.values()}

        # 3. Set the is_final attribute for the reduced DFA states
        for final_state in self.dfa.final_states:
            new_final_state = state_mapping[final_state.state_number]
            new_states[new_final_state].is_final = True  # Mark as final state

        # 4. Create the new transition table and update each state's transitions
        reduced_transition_table = {}
        for old_state, transitions in self.dfa.transition_table.items():
            new_state = state_mapping[old_state]
            reduced_transition_table[new_state] = {}

            for symbol, target_state in transitions.items():
                if target_state != " ":  # If there's a valid transition
                    new_target_state = state_mapping[target_state]
                    reduced_transition_table[new_state][symbol] = new_target_state
                    # Update the transitions in the new State object
                    new_states[new_state].transitions[symbol] = {new_states[new_target_state]}

        print("Reduced Transition Table:", reduced_transition_table)

        # 5. Set the start state
        new_start_state = new_states[state_mapping[self.dfa.start_state.state_number]]

        # 6. Collect all the final states
        new_final_states = {new_states[state_mapping[final.state_number]] for final in self.dfa.final_states}

        # 7. Build and return the new reduced DFA
        reduced_dfa = DFA(new_start_state, new_final_states, reduced_transition_table)

        # Debugging output
        print("This is the initial state: ", reduced_dfa.start_state)
        print("This is the initial state's transitions: ", reduced_dfa.start_state.transitions)
        print("Final states: ", reduced_dfa.final_states)
        
        return reduced_dfa



    # Example usage to reduce DFA
    def reduce_dfa(self):
        self.print_table()
        self.mark_distinguishable_pairs()
        self.group_equivalent_states()  # Group the equivalent states
        self.print_table()
        reduced_dfa = self.construct_reduced_dfa()
        return reduced_dfa
