import re

class ExpresionRegularAFN:

    def init(self): 
        self.expresion = input("Ingrese la expresión regular: ") 
        self.alfabeto = set(re.findall(r'[a-zA-Z0-9]', self.expresión)) 
        # Extrae el alfabeto de la expresión regular 
        self.estado_inicial = None 
        self.estados_finales = set() 
        self.transiciones = []

    def balanceoParentesis(self): 
        # Verifica si la expresión regular tiene paréntesis balanceados 
        stack = [] 
        for char in self.expresion: 
            if char == '(': stack.append(char) 
            elif char == ')': 
                if not stack or stack.pop() != '(': 
                    return False 
                return len(stack) == 0

    def esOperador(self, char):
        # Verifica si un carácter es un operador de la expresión regular
        return char in {'|', ',', '*', '+', '?', '^', '.', '(', ')'}

    def insertar_concatenacion(self, regex):
        # Inserta operadores de concatenación explícitos (.) donde sea necesario
        resultado = ''
        for i in range(len(regex)):
            c1 = regex[i]
            resultado += c1
            if i + 1 < len(regex):
                c2 = regex[i + 1]
                # Insertar '.' si es necesario por reglas de concatenación
                if (not self.isOperator(c1) or c1 in ')*+?') and (not self.esOperador(c2) or c2 == '(' or c2 == '^'):
                    resultado += '.'
        return resultado
    
    def analizar_expresion(self):
        if not self.balanceoParentesis(self.expresion):
            print("Error: Paréntesis no balanceados en la expresión regular.")
            return False
        
    def conversion_a_afn(self):
        # Convierte la expresión regular a un autómata finito no determinista (AFN)
        self.estado_inicial = 'q0'
        self.estados_finales.add('q1')
        self.transiciones.append(('q0', self.expresion, 'q1'))
        self.alfabeto.add('ε')  # Agrega la transición epsilon al alfabeto
        for char in self.expresion:
            if char in self.alfabeto and char not in self.isOperator(char):
                # Si el carácter es parte del alfabeto, se crea una transición
                estado = 'q' + str(len(self.transiciones) + 1)
                self.transiciones.append((self.estado_inicial, char, estado))
                self.estado_inicial = estado
            elif char in self.isOperator(char):
                if char == '|':
                    estado = 'q' + str(len(self.transiciones) + 1)
                    self.transiciones.append((self.estado_inicial, char, estado))
                    self.estado_inicial = estado
                elif char == '*':
                    self.transiciones.append((self.estado_inicial, 'ε', self.estado_inicial))
                elif char == '+':
                    self.transiciones.append((self.estado_inicial, 'ε', self.estado_inicial))
                elif char == '?':
                    self.transiciones.append((self.estado_inicial, 'ε', self.estado_inicial))

    def mostrar_afn(self):
        print("AFN: ")
        print("K (Estados): ", self.estados)
        print("Σ (Alfabeto): ", self.alfabeto)
        print("S (Estado inicial): ", self.estado_inicial)
        print("F (Estados finales): ", self.estados_finales)
        print("δ (Transiciones): ")
        for transiciones in self.transiciones:
            print(transiciones)

    # Funcion principal para ejecutar el programa
    def main(self):
        if self.analizar_expresion():
            self.insertar_concatenacion(self.expresion)
            self.conversion_a_afn()
            self.mostrar_afn()

    def mostrar_afn(self): 
        # Aquí se implementaría la visualización del AFN pass
        print("AFN: ") 
        print("Estados: ", self.estados) 
        print("Alfabeto: ", self.alfabeto) 
        print("Transiciones: ") 
        for transiciones in self.transiciones: 
            print(transiciones) 
        print("Estado inicial: ", self.estado_inicial) 
        print("Estados finales: ", self.estados_finales)
    
