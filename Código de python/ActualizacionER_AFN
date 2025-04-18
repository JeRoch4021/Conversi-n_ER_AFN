#Programa para realizar la conversión de una expresión regular a un autómata finito no determinista
import re

# Definición de la clase ExpresiónRegular
class ExpresionRegular:
  # Constructor de la clase
  def __init__(self):
      self.expresion = input("Ingrese la expresión regular: ")
      self.alfabeto = set(re.findall(r'[a-zA-Z0-9]', self.expresión)) # Extrae el alfabeto de la expresión regular
      self.estado_inicial = 'q0' # Estado inicial del autómata
      self.estado_final = 'q1' # Estado final del autómata
      self.estados = [] # Conjunto de estados del autómata
      self.transiciones = [] # Lista de transiciones del autómata
      self.estados.append(self.estado_inicial) # Agrega el estado inicial al conjunto de estados
      self.estados.append(self.estado_final) # Agrega el estado final al conjunto de estados

  def balanceoParentesis(self):
      # Verifica si la expresión regular tiene paréntesis balanceados
      stack = []
      for char in self.expresion:
          if char == '(': # Si encuentra un paréntesis de apertura, lo agrega a la pila
              stack.append(char)
          elif char == ')': # Si encuentra un paréntesis de cierre, verifica si hay un paréntesis de apertura correspondiente
              if not stack or stack.pop() != '(':
                  return False # Si hay un paréntesis de cierre sin su correspondiente apertura
      return len(stack) == 0 # Devuelve True si todos los paréntesis están balanceados
  
  def esOperador(self, char):
      # Verifica si un carácter es un operador de la expresión regular
      return char in {'|', ',', '*', '+', '?', '^', '.', '(', ')'}
  
  def analizar_expresion(self):
      if not self.balanceoParentesis(self):
          print("Error: Paréntesis no balanceados en la expresión regular.")
          return False

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

  # Convierte una expresión regular en notación postfija usando el algoritmo Shunting Yard
  # Se utiliza para asignar prioridad a los operadores de la expresion regular
  def cambiar_a_postfijo(self, regex):
      precedencias = {'*':3, '+':3, '?': 3, '^':3, '.':2, '|':1, ',':1} # Definición de las precedencias de los operadores
      salida = ''
      pila = []
      for caracter in regex:
          if not self.esOperador(caracter): # Si el carácter no es un operador, se agrega a la salida
              salida += caracter
          elif caracter == '(': # Si encuentra un paréntesis de apertura, se agrega a la pila
              pila.append(caracter)
          elif caracter == ')': # Si encuentra un paréntesis de cierre, se vacía la pila hasta encontrar el paréntesis de apertura
              while pila and pila[-1] != '(':
                  salida += pila.pop()
              pila.pop()
          else: # Si el carácter es un operador, se compara su precedencia con la del operador en la parte superior de la pila
              while pila and pila[-1] != '(' and precedencias.get(caracter, 0) <= precedencias.get(pila[-1], 0):
                  salida += pila.pop()
              pila.append(caracter)
      while pila:
          salida += pila.pop()
      return salida
  
  def separar_subexpresiones(self):
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
      return filaSubexp # Devuelve la lista de subexpresiones

  def casoCerraduraKleene(self, exp, cont, cursorEstado):
      # Maneja la cerradura de Kleene (*) en la expresión regular
      self.estados.insert(cursorEstado + 1, 'q' + str(cont)) # Agrega un nuevo estado al conjunto de estados una posicion adelante del cursor
      self.transiciones.append((self.estados[cursorEstado], 'ε', self.estados[cursorEstado+1])) # Agrega una transición epsilon al autómata
      self.transiciones.append((self.estados[cursorEstado+1], exp, self.estados[cursorEstado+1])) # Agrega la transicion de la cerradura de kleene al autómata
      self.transiciones.append((self.estados[cursorEstado+1], 'ε', self.estados[cursorEstado+2])) # Agrega una transición epsilon al autómata
  
  def casoCerraduraPos(self, exp, cont, cursorEstado):
      # Maneja la cerradura positiva (+) en la expresión regular
      self.estados.insert(cursorEstado + 1, 'q' + str(cont)) # Agrega un nuevo estado al conjunto de estados una posicion adelante del cursor
      self.transiciones.append((self.estados[cursorEstado], exp, self.estados[cursorEstado+1])) # Agrega una transición al autómata
      self.transiciones.append((self.estados[cursorEstado+1], exp, self.estados[cursorEstado+1])) # Agrega la transicion de la cerradura positiva al autómata
      self.transiciones.append((self.estados[cursorEstado+1], 'ε', self.estados[cursorEstado+2])) # Agrega una transición epsilon al autómata

  def casoOr(self, exp1, exp2, cont, cursorEstado):
      # Maneja el caso de la operación OR (|) en la expresión regular
      self.estados.insert(cursorEstado + 1, 'q' + str(cont)) # Agrega un nuevo estado al conjunto de estados una posicion adelante del cursor
      self.transiciones.append((self.estados[cursorEstado], exp1, self.estados[cursorEstado+1])) # Agrega una transición al autómata
      self.transiciones.append((self.estados[cursorEstado], exp2, self.estados[cursorEstado+1])) # Agrega una transición al autómata

  def casoOpcional(self, exp, cont, cursorEstado):
      # Maneja el caso de la operación opcional (?) en la expresión regular
      self.estados.insert(cursorEstado + 1, 'q' + str(cont)) # Agrega un nuevo estado al conjunto de estados una posicion adelante del cursor
      self.transiciones.append((self.estados[cursorEstado], exp, self.estados[cursorEstado+1])) # Agrega una transición al autómata
      self.transiciones.append((self.estados[cursorEstado], 'ε', self.estados[cursorEstado+1])) # Agrega una transición al autómata

  def casoConcatenacion(self, exp1, exp2, cont, cursorEstado):
      # Maneja el caso de la operación de concatenación (.) en la expresión regular
      self.estados.insert(cursorEstado + 1, 'q' + str(cont)) # Agrega un nuevo estado al conjunto de estados una posicion adelante del cursor
      self.transiciones.append((self.estados[cursorEstado], exp1, self.estados[cursorEstado+1])) # Agrega una transición al autómata
      self.transiciones.append((self.estados[cursorEstado+1], exp2, self.estados[cursorEstado+2])) # Agrega una transición al autómata

  def conversion_a_afn(self):
      # Convierte la expresión regular a un autómata finito no determinista (AFN)
      self.transiciones.append(('q0', self.expresion, 'q1'))
      print ("Transiciones: ", self.transiciones) # Imprime la primera transición
      self.alfabeto.add('ε')  # Agrega la transición epsilon al alfabeto
      contador = 2 # Contador para crear los nuevos estados(q0, q1 son los estados iniciales y finales respectivamente)
      cursorEstado = 0 # Cursor para recorrer el conjunto de estados
      # Separa la expresión en subexpresiones
      self.expresion = self.insertar_concatenacion(self.expresion) # Inserta operadores de concatenación explícitos (.) donde sea necesario
      subexpresiones = self.separar_subexpresiones()
      for subexp in subexpresiones:
          if subexp == '*':
              self.casoCerraduraKleene(subexp, contador, cursorEstado)
              contador += 1
              cursorEstado += 2 # Aumenta el contador y el cursor de estado
          elif subexp == '+':
              self.casoCerraduraPos(subexp, contador, cursorEstado)
              contador += 1
              cursorEstado += 2
          elif subexp == '?':
              # Maneja el caso de la operación opcional (?) en la expresión regular
              self.casoOpcional(subexp, contador, cursorEstado)
              contador += 1
              cursorEstado += 1
          elif subexp == '|' or subexp == ',':
              # Si encuentra el operador OR, se separa en dos subexpresiones
              exp1 = subexpresiones.pop(0)
              exp2 = subexpresiones.pop(0)
              self.casoOr(exp1, exp2, contador, cursorEstado)
              contador += 1   
              cursorEstado += 1 # Aumenta el contador y el cursor de estado
          elif subexp == '.':
              # Si encuentra el operador de concatenación, se separa en dos subexpresiones
              exp1 = subexpresiones.pop(0)
              exp2 = subexpresiones.pop(0)
              self.casoConcatenacion(exp1, exp2, contador, cursorEstado)
              contador += 1
              cursorEstado += 1

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
    
if __name__ == "__main__":
  # Crear una instancia de la clase ExpresiónRegular y ejecutar el programa
  er = ExpresionRegular()
  er.main()
  # Ejecutar el programa
