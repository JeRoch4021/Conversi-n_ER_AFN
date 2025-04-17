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
        
    def conversion_a_afn(self):
        # Convierte la expresión regular a un autómata finito no determinista (AFN)
        self.transiciones.append(('q0', self.expresion, 'q1'))
        print ("Transiciones: ", self.transiciones) # Imprime la primera transición
        self.alfabeto.add('ε')  # Agrega la transición epsilon al alfabeto
        contador = 2 # Contador para los estados(q0, q1 son los estados iniciales y finales respectivamente)
        cursorEstado = 0 # Cursor para recorrer el conjunto de estados
        filaSubexp = [] # Pila para almacenar caracteres o subexpresiones
        # Separar los caracteres o subexpresiones concatenados
        for i, char in enumerate(self.expresion):
            if char in self.alfabeto:
                if i < len(self.expresion) - 1 and self.expresion[i + 1] == '.':
                    # Si el siguiente carácter es un operador de concatenación, se crea una transición
                    filaSubexp.append(char)
                elif i < len(self.expresion) - 1 and self.esOperador(self.expresion[i + 1] and self.expresion[i + 1] != '.' and self.expresion[i + 1] != '('):
                    # Si el siguiente caracter es un operador se añade a la subexpresión
                    subexpresion = char + self.expresion[i + 1]
                    filaSubexp.append(subexpresion)
            elif char == '(':
                # Si encuentra un paréntesis de apertura, lo agrega a la pila
                subexp = '('
                for j in range(i + 1, len(self.expresion)):
                    if self.expresion[j] == ')':
                        subexp += self.expresion[j] # Agrega el paréntesis de cierre a la subexpresión
                        if i < len(self.expresion) - 1 and self.esOperador(self.expresion[i + 1] and self.expresion[i + 1] != '.'):
                            # Si el siguiente carácter es un operador, se añade a la subexpresión
                            subexp += self.expresion[i + 1]
                        break # Sale del bucle al encontrar el paréntesis de cierre
                    subexp += self.expresion[j]
                filaSubexp.append(subexp) # Agrega la subexpresión a la pila

        # Procesar la pila para crear transiciones
        while filaSubexp:
            subexpresion = filaSubexp[0] # Toma el primer elemento de la pila
            filaSubexp.remove(filaSubexp[0]) # Elimina el primer elemento de la pila
            self.estados.insert(len(self.estados)-1, 'q' + str(contador)) # Agrega un nuevo estado en la penúltima posición del conjunto de estados
            self.transiciones.append((self.estados[cursorEstado], subexpresion, self.estados[cursorEstado+1])) # Crea una transición entre el estado actual y el nuevo estado
            cursorEstado += 1 # Actualiza el cursor al nuevo estado
            contador += 1 # Incrementa el contador de estados
        
        # Procesar subexpresiones
        for exp in self.transiciones:
            if len(exp[1]) > 1: # Si la subexpresión tiene más de un carácter
                for i in range(len(exp[1])):
                    if exp[1][i] == '.':
                        # Si encuentra un operador de concatenación, crea una transición
                        self.transiciones.append((exp[0], exp[1][i], exp[2]))
                    elif exp[1][i] == '|':
                        # Si encuentra un operador OR, crea una transición
                        self.transiciones.append((exp[0], exp[1][i], exp[2]))
                    elif exp[1][i] == '*':
                        # Si encuentra un operador de Kleene, crea una transición
                        self.transiciones.append((exp[0], exp[1][i], exp[2]))

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
