# Conversion_ER_AFN
Repositorio para guardar los avances del proyecto

import re

class ExpresionRegularAFN:
  def __init__(self):
      self.expresion = input("Ingrese la expresión regular: ")
      self.alfabeto = set(re.findall(r'[a-zA-Z0-9]', self.expresión)) # Extrae el alfabeto de la expresión regular
      self.estado_inicial = None
      self.estados_finales = set()
      self.transiciones = []
      
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
  
  def analizar_expresion(self):
      # Aquí se implementaría el análisis de la expresión regular
      # y la construcción del autómata finito no determinista (AFN)
      if not self.balanceoParentesis(self.expresion):
          print("Error: Paréntesis no balanceados en la expresión regular.")
          return False
      
  
  def mostrar_afn(self):
      # Aquí se implementaría la visualización del AFN
      pass
      
  # Método para imprimir la definicion (k,alfabeto,s,f,transiociones) del AFN resultante
  def mostrar_afn(self):
      print("AFN: ")
      print("Estados: ", self.estados)
      print("Alfabeto: ", self.alfabeto)
      print("Transiciones: ")
      for transiciones in self.transiciones:
          print(transiciones)
      print("Estado inicial: ", self.estado_inicial)
      print("Estados finales: ", self.estados_finales)
