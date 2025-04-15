import os
import re
from tkinter import Tk, Label, Entry, Button, PhotoImage
from PIL import Image, ImageTk
from graphviz import Digraph

# ---------- Lógica para construir el AFN ----------

class State:
    _id_counter = 0

    def __init__(self):
        self.id = State._id_counter
        State._id_counter += 1
        self.transitions = {}

    def add_transition(self, symbol, state):
        self.transitions.setdefault(symbol, []).append(state)

class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept
        self.states = self.get_all_states()

    def get_all_states(self):
        visited = set()
        stack = [self.start]
        result = []

        while stack:
            state = stack.pop()
            if state.id not in visited:
                visited.add(state.id)
                result.append(state)
                for targets in state.transitions.values():
                    stack.extend(targets)
        return result

def regex_to_nfa(symbol):
    start = State()
    end = State()
    start.add_transition(symbol, end)
    return NFA(start, end)

def build_simple_nfa_from_regex(regex):
    # Solo símbolos, sin operadores complejos por ahora
    if not regex:
        return None
    if len(regex) == 1:
        return regex_to_nfa(regex)

    # Concatena todos los símbolos
    nfa = regex_to_nfa(regex[0])
    for c in regex[1:]:
        next_nfa = regex_to_nfa(c)
        nfa.accept.add_transition('ε', next_nfa.start)
        nfa = NFA(nfa.start, next_nfa.accept)
    return nfa

def visualize_nfa(nfa, filename="nfa_output"):
    dot = Digraph()
    dot.attr(rankdir='LR')
    dot.node('start', shape='plaintext', label="")

    for state in nfa.states:
        shape = 'doublecircle' if state == nfa.accept else 'circle'
        dot.node(f"S{state.id}", shape=shape)

    dot.edge('start', f"S{nfa.start.id}")

    for state in nfa.states:
        for symbol, targets in state.transitions.items():
            for target in targets:
                label = symbol if symbol != 'ε' else 'ε'
                dot.edge(f"S{state.id}", f"S{target.id}", label=label)

    dot.render(filename, format='png', cleanup=True)

def print_afn_info(nfa):
    print("\n--- Elementos del AFN ---")

    # Q: Estados
    estados = {f"S{state.id}" for state in nfa.states}
    print("Q (Estados):", estados)

    # Σ: Alfabeto
    alfabeto = set()
    for state in nfa.states:
        for symbol in state.transitions:
            if symbol != 'ε':
                alfabeto.add(symbol)
    print("Σ (Alfabeto):", alfabeto)

    # δ: Función de transición
    print("δ (Transiciones):")
    for state in nfa.states:
        for symbol, targets in state.transitions.items():
            for t in targets:
                print(f"  δ(S{state.id}, '{symbol}') → S{t.id}")

    # q₀: Estado inicial
    print("q₀ (Estado inicial):", f"S{nfa.start.id}")

    # F: Estados de aceptación
    print("F (Estados finales):", f"S{nfa.accept.id}")

# ---------- Interfaz gráfica ----------

class AFNApp:
    def __init__(self, master):
        self.master = master
        master.title("AFN desde Expresión Regular")

        self.label = Label(master, text="Expresión Regular (símbolos simples):")
        self.label.pack()

        self.entry = Entry(master, width=40)
        self.entry.pack()

        self.button = Button(master, text="Convertir a AFN", command=self.convertir)
        self.button.pack(pady=10)

        self.image_label = Label(master)
        self.image_label.pack()

    def convertir(self):
        regex = self.entry.get().strip()

        if not regex:
            print("Ingrese una expresión regular válida.")
            return

        # Reset IDs
        State._id_counter = 0

        # Crear el AFN
        nfa = build_simple_nfa_from_regex(regex)

        if not nfa:
            print("No se pudo construir el AFN.")
            return

        # Imprimir información del AFN
        print_afn_info(nfa)

        # Visualizar
        visualize_nfa(nfa, "nfa_output")

        # Mostrar en GUI
        img = Image.open("nfa_output.png").resize((600, 400))
        self.tk_image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_image)

# ---------- Ejecutar ----------

if __name__ == "__main__":
    root = Tk()
    app = AFNApp(root)
    root.mainloop()
