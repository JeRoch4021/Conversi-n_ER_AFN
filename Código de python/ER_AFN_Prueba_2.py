import os
from tkinter import Tk, Label, Entry, Button
from PIL import Image, ImageTk
from graphviz import Digraph

# Clase que representa un estado del autómata
class State:
    _id_counter = 0 # Contador global para asignar IDs únicos

    def __init__(self):
        self.id = State._id_counter # ID único del estado
        State._id_counter += 1
        self.transitions = {} # Diccionario de transiciones {símbolo: [estados destino]}

    def add_transition(self, symbol, state):
        # Agrega una transición desde este estado a otro por un símbolo
        self.transitions.setdefault(symbol, []).append(state)

# Clase para representar un AFN con estado inicial y final
class NFA:
    def __init__(self, start, accept):
        self.start = start # Estado inicial
        self.accept = accept # Estado final

# Función que verifica si un carácter es un operador de la expresión regular
def is_operator(c):
    return c in {'|', ',', '*', '+', '?', '^', '.', '(', ')'}

# Inserta operadores de concatenación explícitos (.) donde sea necesario
def insert_concat(regex):
    result = ''
    for i in range(len(regex)):
        c1 = regex[i]
        result += c1
        if i + 1 < len(regex):
            c2 = regex[i + 1]
            # Insertar '.' si es necesario por reglas de concatenación
            if (not is_operator(c1) or c1 in ')*+?') and (not is_operator(c2) or c2 == '(' or c2 == '^'):
                result += '.'
    return result

# Convierte una expresión regular en notación postfija usando el algoritmo Shunting Yard
def regex_to_postfix(regex):
    precedence = {'*': 3, '+': 3, '?': 3, '^': 3, '.': 2, '|': 1, ',': 1}
    output, stack = '', []
    for c in regex:
        if c.isalnum() or c == 'ε':
            output += c # Operando directo a la salida
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output += stack.pop() # Vaciar la pila hasta '('
            stack.pop() # Eliminar '(
        else:
            while stack and stack[-1] != '(' and precedence.get(c, 0) <= precedence.get(stack[-1], 0):
                output += stack.pop() # Sacar operadores con mayor o igual precedencia
            stack.append(c)
    while stack:
        output += stack.pop() # Vaciar el resto de la pila
    return output

# Genera una imagen del AFN usando graphviz
def visualize_nfa(nfa, filename):
    dot = Digraph(graph_attr={'rankdir': 'LR'})  # <- Visualización horizontal, representación izquierda a derecha
    visited = set()
    queue = [nfa.start]
    dot.node("start", shape="plaintext", label="") # Nodo de inicio ficticio
    dot.edge("start", f"S{nfa.start.id}") # Flecha hacia el estado inicial

    while queue:
        current = queue.pop()
        if current.id in visited:
            continue
        visited.add(current.id)
        shape = "doublecircle" if current == nfa.accept else "circle"
        dot.node(f"S{current.id}", label=f"S{current.id}", shape=shape)

        for symbol, states in current.transitions.items():
            for st in states:
                label = "ε" if symbol == 'ε' else symbol
                dot.edge(f"S{current.id}", f"S{st.id}", label=label)
                queue.append(st)

    dot.render(filename=filename, format='png', cleanup=True) # Guardar imagen

# Implementación del algoritmo de Thompson paso a paso para construir el AFN
def thompson_step_by_step(postfix):
    stack = []
    step_images = []
    step = 1
    State._id_counter = 0 # Reiniciar contador de estados

    for c in postfix:
        if c.isalnum() or c == 'ε':
            # Crear transiciones básicas
            s1, s2 = State(), State()
            s1.add_transition(c, s2)
            nfa = NFA(s1, s2)

        elif c == '*':
            # Cierre de Kleene
            nfa1 = stack.pop()
            s, a = State(), State()
            s.add_transition('ε', nfa1.start)
            s.add_transition('ε', a)
            nfa1.accept.add_transition('ε', nfa1.start)
            nfa1.accept.add_transition('ε', a)
            nfa = NFA(s, a)

        elif c == '+':
            # Cierre positivo
            nfa1 = stack.pop()
            s = nfa1.start
            a = State()
            nfa1.accept.add_transition('ε', nfa1.start)
            nfa1.accept.add_transition('ε', a)
            nfa = NFA(s, a)

        elif c == '?':
            # Cero o una vez
            nfa1 = stack.pop()
            s, a = State(), State()
            s.add_transition('ε', nfa1.start)
            s.add_transition('ε', a)
            nfa1.accept.add_transition('ε', a)
            nfa = NFA(s, a)

        elif c == '^':
            # Ninguna vez (cadena vacía)
            s, a = State(), State()
            s.add_transition('ε', a)
            nfa = NFA(s, a)

        elif c == '.':
            # Concatenación
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            nfa1.accept.add_transition('ε', nfa2.start)
            nfa = NFA(nfa1.start, nfa2.accept)

        elif c == '|' or c == ',':
            # Alternancia
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            s, a = State(), State()
            s.add_transition('ε', nfa1.start)
            s.add_transition('ε', nfa2.start)
            nfa1.accept.add_transition('ε', a)
            nfa2.accept.add_transition('ε', a)
            nfa = NFA(s, a)

        # Apilar el nuevo NFA construido
        stack.append(nfa)

        # Visualizar y guardar imagen del paso
        filename = f"step_{step:02}"
        visualize_nfa(nfa, filename)
        step_images.append(f"{filename}.png")
        step += 1

    final_nfa = stack.pop()

    # --- Imprimir los 5 elementos del AFN ---
    print("\n=== Elementos del AFN ===")
    visited = set()
    states = []
    alphabet = set()
    transitions = []
    queue = [final_nfa.start]

    while queue:
        current = queue.pop()
        if current.id in visited:
            continue
        visited.add(current.id)
        states.append(f"S{current.id}")
        for symbol, targets in current.transitions.items():
            for target in targets:
                transitions.append(f"δ(S{current.id}, '{symbol}') -> S{target.id}")
                if symbol != 'ε':
                    alphabet.add(symbol)
                queue.append(target)

    print("Q (Estados):", states)
    print("Σ (Alfabeto):", list(alphabet))
    print("q₀ (Inicial):", f"S{final_nfa.start.id}")
    print("F (Finales):", f"S{final_nfa.accept.id}")
    print("δ (Transiciones):")
    for t in transitions:
        print("  ", t)

    return final_nfa, step_images


# ---------- Interfaz gráfica con Tkinter ----------

class RegexGUI:
    def __init__(self, master):
        self.master = master
        master.title("AFN Paso a Paso")

        self.label = Label(master, text="Expresión Regular:")
        self.label.pack()

        self.entry = Entry(master, width=40)
        self.entry.pack()

        self.generate_button = Button(master, text="Generar AFN", command=self.generar)
        self.generate_button.pack(pady=10)

        self.image_label = Label(master) # Para mostrar imágenes
        self.image_label.pack()

        self.nav_frame = Label(master) # Frame de navegación
        self.nav_frame.pack()

        self.prev_button = Button(self.nav_frame, text="⏮ Anterior", command=self.prev)
        self.prev_button.grid(row=0, column=0)

        self.next_button = Button(self.nav_frame, text="Siguiente ⏭", command=self.next)
        self.next_button.grid(row=0, column=1)

        self.image_paths = [] # Lista de rutas a imágenes generadas
        self.image_index = 0 # Índice actual en la navegación

    def generar(self):
        regex = self.entry.get()
        if not regex:
            return

        # Crear carpeta para las imágenes si no existe
        if not os.path.exists("output"): os.makedirs("output")
        os.chdir("output")

        # Eliminar imágenes anteriores
        for f in os.listdir():
            if f.startswith("step_") and f.endswith(".png"):
                os.remove(f)

        # Procesar la expresión y generar el AFN paso a paso
        postfix = regex_to_postfix(insert_concat(regex))
        _, self.image_paths = thompson_step_by_step(postfix)
        os.chdir("..")
        self.image_index = 0
        self.update_image() # Mostrar la primera imagen

    def update_image(self):
        if not self.image_paths:
            return
        path = os.path.join("output", self.image_paths[self.image_index])
        img = Image.open(path).resize((1000, 400), Image.Resampling.LANCZOS)
        self.tkimage = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tkimage)

    def prev(self):
        if self.image_index > 0:
            self.image_index -= 1
            self.update_image()

    def next(self):
        if self.image_index < len(self.image_paths) - 1:
            self.image_index += 1
            self.update_image()


# ---------- Ejecutar la interfaz gráfica (GUI) ----------

if __name__ == "__main__":
    root = Tk()
    gui = RegexGUI(root)
    root.mainloop()



    

