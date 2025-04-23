import re
import os
from graphviz import Digraph

class ExpresionRegularAFN:

    def __init__(self): 
        # Constructor: inicializa los atributos necesarios para el AFN.
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
        # Llama a balanceoParentesis y devuelve False si hay error de sintaxis.
        if not self.balanceoParentesis():
            print("Error: Paréntesis no balanceados en la expresión regular.")
            return False
        return True
    
    def cambiar_a_postfijo(self, regex):
        # Convierte una expresión regular en notación postfija usando el algoritmo Shunting Yard
        # Se utiliza para asignar prioridad a los operadores de la expresion regular
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
                dot.node(name=estado, label=estado, shape='doublecircle') # Forma par a los estados finales
            else:
                dot.node(name=estado, label=estado)

        # Dibujar las transiciones
        for origen, simbolo, destino in transiciones_parciales:
            label = simbolo
            dot.edge(origen, destino, label=label)

        # Guardar las imagenes
        # Crear el directorio sino existe
        if not os.path.exists("AFN_paso_por_paso"):
            os.makedirs("AFN_paso_por_paso")
        # Ruta completa del archivo de salida
        ruta_salida = os.path.join("AFN_paso_por_paso", f'AFN_paso_{paso:02}')
        dot.render(filename=ruta_salida, cleanup=True)

    def conversion_a_afn(self):
        # Método principal para construir el AFN paso a paso desde la expresión regular en postfijo.
        postfijo = self.cambiar_a_postfijo(self.expresion)
        contador = 0
        paso = 1

        def nuevo_estado():
            # Crea un nuevo estado con nombre único (q0, q1, ...).
            nonlocal contador
            estado = f'q{contador}'
            contador += 1
            return estado
        
        pila = []

         # Recorre cada símbolo en la expresión postfija para construir el AFN.
        for caracter in postfijo:
            if caracter in self.alfabeto:
                # Si el carácter es parte del alfabeto, se crea una transición
                Q1, Q2 = nuevo_estado(), nuevo_estado()

                # Agrega la transición (Q1 --caracter--> Q2)
                self.transiciones.append((Q1, caracter, Q2))

                # Empuja el nuevo fragmento del AFN a la pila
                pila.append((Q1, Q2))
                self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {Q2}, Q1, paso)
                paso += 1
            elif caracter == '.':
                # Operador de concatenación
                expresion_2 = pila.pop()
                expresion_1 = pila.pop()
                transiciones_actualizadas = []

                # Redirige transiciones de expresion_2 para conectarlas con el final de expresion_1
                for origen, simbolo, destino in self.transiciones:
                    if origen == expresion_2[0]:
                        origen = expresion_1[1]
                        transiciones_actualizadas.append((origen, simbolo, destino))
                
                # Elimina las transiciones viejas del segundo fragmento
                self.transiciones = [t for t in self.transiciones if t[0] not in {expresion_2[0]}]
                self.transiciones.extend(transiciones_actualizadas)

                # Empuja el nuevo fragmento concatenado a la pila
                pila.append((expresion_1[0], expresion_2[1]))
                self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {expresion_2[1]}, expresion_1[0], paso)
                paso += 1

            elif caracter == '|' or caracter == ',':
                # Operador de alternancia
                
                # Crea nuevos estados compartidos
                estado_inicial, estado_final = nuevo_estado(), nuevo_estado()

                expresion_2 = pila.pop()
                expresion_1 = pila.pop()
                
                # Redirigir transiciones de expresion_1
                for i in range(len(self.transiciones)):
                    if self.transiciones[i][0] == expresion_1[0]:
                        self.transiciones[i] = (estado_inicial, self.transiciones[i][1], self.transiciones[i][2])
                    if self.transiciones[i][2] == expresion_1[1]:
                        self.transiciones[i] = (self.transiciones[i][0], self.transiciones[i][1], estado_final)
                
                # Redirigir transiciones de expresion_2
                for i in range(len(self.transiciones)):
                    if self.transiciones[i][0] == expresion_2[0]:
                        self.transiciones[i] = (estado_inicial, self.transiciones[i][1], self.transiciones[i][2])
                    if self.transiciones[i][2] == expresion_2[1]:
                        self.transiciones[i] = (self.transiciones[i][0], self.transiciones[i][1], estado_final)
                
                # Empuja el fragmento resultante
                pila.append((estado_inicial, estado_final))
                self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                paso += 1
                
            elif caracter == '*':
                # Operador de cerradura de Kleene
                estado_inicial, estado_final = nuevo_estado(), nuevo_estado()
                estado_repeticion = nuevo_estado()
                expresion = pila.pop()
                
                # Redirigimos todas las transiciones internas hacia el nuevo estado de repetición
                for i in range(len(self.transiciones)):
                    if self.transiciones[i][0] == expresion[0]:
                        self.transiciones[i] = (estado_repeticion, self.transiciones[i][1], self.transiciones[i][2])
                    if self.transiciones[i][2] == expresion[1]:
                        self.transiciones[i] = (self.transiciones[i][0], self.transiciones[i][1], estado_repeticion)

                # Transiciones ε para entrada y salida del bucle
                self.transiciones.append((estado_inicial, 'ε', estado_repeticion))
                self.transiciones.append((estado_repeticion, 'ε', estado_final))

                # Empuja el nuevo bloque a la pila
                pila.append((estado_inicial, estado_final))
                self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                paso += 1

            elif caracter == '+':
                # Operador de cerradura positiva
                estado_inicial, estado_final = nuevo_estado(), nuevo_estado()
                estado_intermedio = nuevo_estado()
                estado_retorno = nuevo_estado()
                expresion = pila.pop()

                inicio_sub_afn, fin_sub_afn = expresion
                
                # Redirige las transiciones desde el nuevo estado inicial
                for i in range(len(self.transiciones)):
                    if self.transiciones[i][0] == inicio_sub_afn:
                        self.transiciones[i] = (estado_inicial, self.transiciones[i][1], self.transiciones[i][2])
                
                # Cambiamos el sub estado inicial por el nuevo estado inicial
                inicio_sub_afn = estado_inicial

                # Evalua si exite una concatenación entre dos o mas caracteres, de los contrario
                # solo colocara una repetición al mismo estado.
                for i in range(len(self.transiciones)):
                    if (self.transiciones[i][0] == inicio_sub_afn and self.transiciones[i][2] == fin_sub_afn):
                        self.transiciones.append((estado_intermedio, self.transiciones[i][1], estado_intermedio))
                    if self.transiciones[i][2] != fin_sub_afn:
                        self.transiciones.append((estado_intermedio, self.transiciones[i][1], estado_retorno))
                    if self.transiciones[i][0] != inicio_sub_afn:
                        self.transiciones.append((estado_retorno, self.transiciones[i][1], estado_intermedio))

                # Entrada de la transicion vacia al estado intermedio
                self.transiciones.append((fin_sub_afn, 'ε', estado_intermedio))
                # Salida de la transicion vacia al estado final
                self.transiciones.append((estado_intermedio, 'ε', estado_final))
                
                # Empujar el nuevo bloque a la pila
                pila.append((estado_inicial, estado_final))
                self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                paso += 1

            elif caracter == '?':
                # Operador de cero o una vez
                estado_inicial, estado_final = nuevo_estado(), nuevo_estado()
                expresion = pila.pop()

                # Redirige transiciones de entrada
                for i in range(len(self.transiciones)):
                    if self.transiciones[i][0] == expresion[0]:
                        self.transiciones[i] = (estado_inicial, self.transiciones[i][1], self.transiciones[i][2])
                    if self.transiciones[i][2] == expresion[1]:
                        self.transiciones[i] = (self.transiciones[i][0], self.transiciones[i][1], estado_final)

                # Transición ε directa que representa "cero veces"
                self.transiciones.append((estado_inicial, 'ε', estado_final))

                # Empuja resultado a la pila
                pila.append((estado_inicial, estado_final))
                self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                paso += 1
            elif caracter == '^':
                # Operador de nada (cadena vacía)
                estado_inicial, estado_final = nuevo_estado(), nuevo_estado()

                # Transicion ε de algo o nada
                self.transiciones.append((estado_inicial, 'ε', estado_final))
                    
                pila.append((estado_inicial, estado_final))
                self.proyeccion_grafica_paso_a_paso(self.transiciones.copy(), {estado_final}, estado_inicial, paso)
                paso += 1

        # Finaliza la construcción del AFN: define estado inicial y estados finales
        inicio, fin = pila.pop()
        self.estado_inicial = inicio
        self.estados_finales.add(fin)

        # Agrega todos los estados encontrados a la lista de estados del autómata
        for origen, _, destino in self.transiciones:
            self.estados.update([origen, destino])

    def mostrar_AFN(self):
        # Imprime los cinco componentes principales del AFN en consola.
        lista_estados_ordenados = sorted(self.estados, key=lambda k: int(k[1:]))
        alfabeto_ordenado = sorted(self.alfabeto)
        print("AFN: ")
        print("K (Estados): ", lista_estados_ordenados)
        print("Σ (Alfabeto): ", alfabeto_ordenado)
        print("S (Estado inicial): ", self.estado_inicial)
        print("F (Estados finales): ", self.estados_finales)
        print("δ (Transiciones): ")
        
        for transicion in self.transiciones:
            print(f"{transicion[0]} --{transicion[1]}--> {transicion[2]}")
        
    def main(self):
        # Ejecuta el flujo principal del programa: análisis, conversión y visualización.
        if self.analizar_expresion():
            self.expresion = self.insertar_concatenacion(self.expresion)
            self.conversion_a_afn()
            self.mostrar_AFN()

if __name__ == "__main__":
    clase_principal = ExpresionRegularAFN()
    clase_principal.main()