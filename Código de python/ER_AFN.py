import re

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
        stack = [] 
        for char in self.expresion: 
            if char == '(': 
                stack.append(char) 
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
                if (not self.esOperador(c1) or c1 in ')*+?') and (not self.esOperador(c2) or c2 == '(' or c2 == '^'):
                    resultado += '.'
        return resultado
    
    def analizar_expresion(self):
        if not self.balanceoParentesis():
            print("Error: Paréntesis no balanceados en la expresión regular.")
            return False
        return True
        
    def conversion_a_afn(self):
        # Convierte la expresión regular a un autómata finito no determinista (AFN)
        self.estado_inicial = 'q0'
        estado_actual = self.estado_inicial
        self.transiciones.append(('q0', self.expresion, 'q1'))
        # self.alfabeto.add('ε')  # Agrega la transición epsilon al alfabeto
        contador = 1

        for char in self.expresion:
            #if char in self.alfabeto and char not in self.esOperador(char):
            if not self.esOperador(char):
                # Si el carácter es parte del alfabeto, se crea una transición
                # nuevo_estado = f"q{contador}"
                nuevo_estado = f'q{contador}'
                self.estados.add(estado_actual)
                self.estados.add(nuevo_estado)
                self.transiciones.append((estado_actual, char, nuevo_estado))
                estado_actual = nuevo_estado
                contador += 1
            else:
                if char == '|' or char == ',':
                    nuevo_estado = f'q{contador}'
                    estado_intermedio = f'q{contador + 1}'
                    self.transiciones.append((estado_actual, 'ε', nuevo_estado))
                    self.transiciones.append((estado_actual, 'ε', estado_intermedio))
                    self.estados.update([estado_actual, nuevo_estado, estado_intermedio])
                    estado_actual = f'q{contador + 2}'
                    self.transiciones.append((nuevo_estado, 'ε', estado_actual))
                    self.transiciones.append((estado_intermedio, 'ε', estado_actual))
                    self.estados.add(estado_actual)
                    contador += 3
                elif char == '*':
                    estado_ciclo_inicial = f'q{contador}'
                    estado_ciclo_final = f'q{contador + 1}'
                    self.transiciones.append((estado_actual, 'ε', estado_ciclo_inicial))
                    self.transiciones.append((estado_ciclo_inicial, 'ε', estado_ciclo_final))
                    self.transiciones.append((estado_ciclo_final, 'ε', estado_ciclo_inicial))
                    self.transiciones.append((estado_ciclo_final, 'ε', estado_ciclo_inicial))
                    self.estados.update([estado_ciclo_inicial, estado_ciclo_final])
                    estado_actual = estado_ciclo_final
                    contador += 2
                elif char == '+':
                    self.transiciones.append((estado_actual, 'ε', estado_actual))
                elif char == '?':
                    self.transiciones.append((estado_actual, 'ε', estado_actual))

        self.estados.add(estado_actual)
        self.estados_finales.add(estado_actual)

    def mostrar_AFN(self):
        print("AFN: ")
        print("K (Estados): ", self.estados)
        print("Σ (Alfabeto): ", self.alfabeto)
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
