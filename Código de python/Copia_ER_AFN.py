import re
import os
from graphviz import Digraph

class ExpresionRegularAFN:

    def __init__(self): 
        self.expresion = input("Ingrese la expresión regular: ") 
        self.alfabeto = set(re.findall(r'[a-zA-Z0-9]', self.expresion)) 
        # Extrae el alfabeto de la expresión regular 
        self.estado_inicial = None 
        self.estados_finales = set() 
        self.transiciones = []
        self.estados = set()

    def balanceoParentesis(self): 
        # Verifica si la expresión regular tiene paréntesis balanceados 
        pila = [] 
        for caracter in self.expresion: 
            if caracter == '(': 
                pila.append(caracter) 
            elif caracter == ')': 
                if not pila or pila.pop() != '(': 
                    return False 
        return len(pila) == 0

    def esOperador(self, caracter):
        # Verifica si un carácter es un operador de la expresión regular
        return caracter in {'|', ',', '*', '+', '?', '^', '.', '(', ')'}

    def insertar_concatenacion(self, regex):
        # Inserta operadores de concatenación explícitos (.) donde sea necesario
        resultado = ''
        for i in range(len(regex)):
            c1 = regex[i]
            resultado += c1
            if i + 1 < len(regex):
                c2 = regex[i + 1]
                # Insertar '.' si es necesario por reglas de concatenación
                if (not self.esOperador(c1) or c1 in ')*+?') and (not self.esOperador(c2) or c2 == '(' or c2 == '^'):
                    resultado += '.'
        return resultado
    
    def analizar_expresion(self):
        if not self.balanceoParentesis():
            print("Error: Paréntesis no balanceados en la expresión regular.")
            return False
        return True
    
    # Convierte una expresión regular en notación postfija usando el algoritmo Shunting Yard
    # Se utiliza para asignar prioridad a los operadores de la expresion regular
    def cambiar_a_postfijo(self, regex):
        precedencias = {'*':3, '+':3, '?': 3, '^':3, '.':2, '|':1, ',':1}
        salida = ''
        pila = []
        for caracter in regex:
            if not self.esOperador(caracter):
                salida += caracter
            elif caracter == '(':
                pila.append(caracter)
            elif caracter == ')':
                while pila and pila[-1] != '(':
                    salida += pila.pop()
                pila.pop()
            else:
                while pila and pila[-1] != '(' and precedencias.get(caracter, 0) <= precedencias.get(pila[-1], 0):
                    salida += pila.pop()
                pila.append(caracter)
        while pila:
            salida += pila.pop()
        return salida

    def proyeccion_grafica_paso_a_paso(self, transiciones_parciales, estados_finales, estado_inicial, paso):
        # Crear un grafo orientado a la derecha
        dot = Digraph(comment='Construccion del AFN', format='png')
        dot.attr(rankdir ='LR') # Visualización horizontal, representación izquierda a derecha
        dot.attr('node', shape='circle')

        # Nodo ficticio para la flecha de inicio
        dot.node('', shape='none')

        # Flecha desde el nodo ficticio al estado incial
        dot.edge('', estado_inicial)

        # Recopilar todos los estados involucrados en las transiciones
        estados_involucrados = set()
        for origen, simbolo, destino in transiciones_parciales:
            estados_involucrados.update([origen, destino])

        # Dibujar estados como nodos
        for estado in estados_involucrados:
            if estado in estados_finales:
                dot.node(estado, shape='doublecircle') # Forma par a los estados finales
            else:
                dot.node(estado)

        # Dibujar las transiciones
        for origen, simbolo, destino in transiciones_parciales:
            label = 'ε' if simbolo == 'ε' else simbolo
            dot.edge(origen, destino, label=label)

        # Guardar las imagenes
        # Crear el directorio sino existe
        if not os.path.exists("AFN_paso_por_paso"):
            os.makedirs("AFN_paso_por_paso")
        # Ruta completa del archivo de salida
        ruta_salida = os.path.join("AFN_paso_por_paso", f'AFN_paso_{paso:02}')
        dot.render(filename=ruta_salida, cleanup=True)

    def conversion_a_afn(self):
        self.estados = set()
        postfijo = self.cambiar_a_postfijo(self.expresion)
        contador = 0
        paso = 1

        def nuevo_estado():
            nonlocal contador
            estado = f'q{contador}'
            contador += 1
            return estado
        
        pila = []

        for caracter in postfijo:
            if not self.esOperador(caracter):
                # Si el carácter es parte del alfabeto, se crea una transición
                Q1, Q2 = nuevo_estado(), nuevo_estado()
                self.transiciones.append((Q1, caracter, Q2))
                pila.append((Q1, Q2))
                self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {Q2}, Q1, paso)
                paso += 1
            else:
                if caracter == '.':
                    expresion_2 = pila.pop()
                    expresion_1 = pila.pop()
                    self.transiciones.append((expresion_1[1], 'ε', expresion_2[0]))
                    pila.append((expresion_1[0], expresion_2[1]))
                    self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {expresion_2[1]}, expresion_1[0], paso)
                    paso += 1
                elif caracter == '|' or caracter == ',':
                    estado_inicial, estado_final = nuevo_estado(), nuevo_estado()
                    expresion_2 = pila.pop()
                    expresion_1 = pila.pop()
                    self.transiciones += [
                        (estado_inicial, 'ε', expresion_1[0]),
                        (estado_inicial, 'ε', expresion_2[0]),
                        (expresion_1[1], 'ε', estado_final),
                        (expresion_2[1], 'ε', estado_final)
                    ]
                    pila.append((estado_inicial, estado_final))
                    self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                    paso += 1
                elif caracter == '*':
                    estado_inicial, estado_final = nuevo_estado(), nuevo_estado()
                    expresion = pila.pop()
                    self.transiciones += [
                        (estado_inicial, 'ε', expresion[0]),
                        (estado_inicial, 'ε', estado_final),
                        (expresion[1], 'ε', expresion[0]),
                        (expresion[1], 'ε', estado_final)
                    ]
                    pila.append((estado_inicial, estado_final))
                    self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                    paso += 1
                elif caracter == '+':
                    estado_inicial, estado_final = nuevo_estado(), nuevo_estado()
                    expresion = pila.pop()
                    self.transiciones += [
                        (estado_inicial, 'ε', expresion[0]),
                        (expresion[1], 'ε', expresion[0]),
                        (expresion[1], 'ε', estado_final)
                    ]
                    pila.append((estado_inicial, estado_final))
                    self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                    paso += 1
                elif caracter == '?':
                    estado_inicial, estado_final = nuevo_estado(), nuevo_estado()
                    expresion = pila.pop()
                    self.transiciones += [
                        (estado_inicial, 'ε', expresion[0]),
                        (estado_inicial, 'ε', estado_final),
                        (expresion[1], 'ε', estado_final)
                    ]
                    pila.append((estado_inicial, estado_final))
                    self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                    paso += 1
                elif caracter == '^':
                    estado_inicial, estado_final = nuevo_estado(), nuevo_estado()
                    self.transiciones.append((estado_inicial, 'ε', estado_final))
                    pila.append((estado_inicial, estado_final))
                    self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                    paso += 1

        inicio, fin = pila.pop()
        self.estado_inicial = inicio
        self.estados_finales.add(fin)

        for transicion in self.transiciones:
            self.estados.update([transicion[0], transicion[2]])

    def mostrar_AFN(self):
        lista_estados_ordenados = sorted(self.estados, key=lambda k: int(k[1:]))
        alfabeto_ordenado = sorted(self.alfabeto)
        print("AFN: ")
        #print("K (Estados): ", self.estados)
        print("K (Estados): ", lista_estados_ordenados)
        print("Σ (Alfabeto): ", alfabeto_ordenado)
        print("S (Estado inicial): ", self.estado_inicial)
        print("F (Estados finales): ", self.estados_finales)
        print("δ (Transiciones): ")
        for transicion in self.transiciones:
            print(f"{transicion[0]} --{transicion[1]}--> {transicion[2]}")
        
    # Funcion principal para ejecutar el programa
    def main(self):
        if self.analizar_expresion():
            self.expresion = self.insertar_concatenacion(self.expresion)
            self.conversion_a_afn()
            self.mostrar_AFN()

if __name__ == "__main__":
    clase_principal = ExpresionRegularAFN()
    clase_principal.main()