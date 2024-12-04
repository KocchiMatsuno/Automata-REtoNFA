import re
import os
from graphviz import Digraph

# this is where u define a state class for NFA
class State:
    def __init__(self):
        self.transitions = {}
        self.epsilon_transitions = []

class NFA:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def visualize(self, filename):
        dot = Digraph()
        visited = set()
        self._add_states(dot, self.start, visited)
        
        # fix/rename the filename to avoid invalid characters
        safe_filename = self.sanitize_filename(filename)
        
        dot.render(safe_filename, format="png", cleanup=True)

    def _add_states(self, dot, state, visited):
        if state in visited:
            return
        visited.add(state)
        for symbol, next_states in state.transitions.items():
            for next_state in next_states:
                dot.node(str(id(state)))
                dot.node(str(id(next_state)))
                dot.edge(str(id(state)), str(id(next_state)), label=symbol)
                self._add_states(dot, next_state, visited)
        for next_state in state.epsilon_transitions:
            dot.node(str(id(state)))
            dot.node(str(id(next_state)))
            dot.edge(str(id(state)), str(id(next_state)), label="ε")
            self._add_states(dot, next_state, visited)

    def sanitize_filename(self, filename):
        """Sanitize the filename to remove invalid characters."""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)


# Tokenizer function for the *, |, and ()
def tokenize_regex(regex):
    """Tokenizes the regular expression into operators, literals, and parentheses."""
    tokens = []
    for char in regex:
        if char in {'*', '|', '(', ')'}:
            tokens.append(char)
        else:
            tokens.append(char)  # Literals (e.g., 'a', 'b', 'c')
    return tokens


# Convert RE to NFA
def regex_to_nfa(regex):
    tokens = tokenize_regex(regex)
    stack = []
    operators = []

    def create_basic_nfa(symbol):
        start = State()
        end = State()
        start.transitions[symbol] = [end]
        return NFA(start, end)

    for token in tokens:
        if token.isalnum():  # Literal (like 'a', 'b', 'c')
            stack.append(create_basic_nfa(token))
        elif token == '*':  # Kleene star (closure)
            nfa = stack.pop()
            start = State()
            end = State()
            start.epsilon_transitions.append(nfa.start)
            nfa.end.epsilon_transitions.extend([nfa.start, end])
            stack.append(NFA(start, end))
        elif token == '|':  # Union (OR operator)
            operators.append('|')
        elif token == '(':  # Start of a group
            operators.append('(')
        elif token == ')':  # End of a group
            while operators and operators[-1] != '(':
                if operators[-1] == '|':
                    operators.pop()
                    nfa2 = stack.pop()
                    nfa1 = stack.pop()
                    start = State()
                    end = State()
                    start.epsilon_transitions.extend([nfa1.start, nfa2.start])
                    nfa1.end.epsilon_transitions.append(end)
                    nfa2.end.epsilon_transitions.append(end)
                    stack.append(NFA(start, end))
            operators.pop()  # Remove '('

    # If there's anything left in operators or stack, handle them
    while operators:
        op = operators.pop()
        if op == '|':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            start = State()
            end = State()
            start.epsilon_transitions.extend([nfa1.start, nfa2.start])
            nfa1.end.epsilon_transitions.append(end)
            nfa2.end.epsilon_transitions.append(end)
            stack.append(NFA(start, end))

    # Return the final NFA
    return stack.pop()


# Main function to get user input and convert the regular expression to an NFA
def main():
    regex = input("Enter a Regular Expression: ")
    nfa = regex_to_nfa(regex)
    nfa.visualize(f"{regex}_nfa")

if __name__ == "__main__":
    main()
