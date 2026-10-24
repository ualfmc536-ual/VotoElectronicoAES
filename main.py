"""
Created on 24/10/2026
@author: francisco montes, miguel, jose antonio, francisco sánchez
"""
from random import Random
from pathlib import Path

generador = Random()
p = 13
num_votantes = 0
nº_candidatos = 2
conjuntos_codificacion: list[list[int]] = []


def iniciar_censo():
    CARPETA_DATOS = Path(__file__).resolve().parent / "Documentos"
    archivo_votantes = CARPETA_DATOS / "votantes.txt"
    with open("censo.txt", "w") as archivo:
        global num_votantes
        lista = []
        with open(archivo_votantes, "r") as votantes:
            for linea in votantes:
                lista.append(linea.strip())
        num_votantes = len(lista)
        for i in range(num_votantes):
            archivo.write(str(lista[i]) + " \n")


def iniciar_urna():
    print("Número de votantes: ", num_votantes)
    print("Número primo: ", p)
    with open("urna.txt", "w") as archivo:
        for i in range(num_votantes):
            archivo.write(str(generador.randint(0, 100)%p) + " \t")
        archivo.write("\n")
        for i in range(num_votantes):
            archivo.write(str(0) + " \t")
        archivo.write("\n")


def iniciar_conjuntos_codificacion():
    global conjuntos_codificacion
    lista_candidatos = []
    for i in range(nº_candidatos):
        lista_candidatos.append("Candidato " + str(i + 1))
        conjuntos_codificacion.append([lista_candidatos[i]])
    lista_numeros = []

    for i in range(p):
        lista_numeros.append(i)

    for i in range (p):
        numero_aleatorio = generador.randint(0, len(lista_numeros)-1)
        candidato_index = i % len(lista_candidatos)
        conjuntos_codificacion[candidato_index].append(lista_numeros[numero_aleatorio]) 
        lista_numeros.pop(numero_aleatorio)

    with open("conjuntos_codificacion.txt", "w") as archivo:
        for i in range(len(conjuntos_codificacion)):
            archivo.write("Conjunto de codificación del " + conjuntos_codificacion[i][0] + ": \n")
            for j in range(1, len(conjuntos_codificacion[i])):
                archivo.write(str(conjuntos_codificacion[i][j]) + " \t")
            archivo.write("\n")



def main(): 
    censo_iniciado = False
    urna_iniciada = False
    while True:
        print("Menú de votación AES")
        print("Opciones:")
        print("1. Iniciar censo electoral")
        print("2. Iniciar urna")
        print("3. Iniciar conjuntos de codificación")
        print("4. Iniciar proceso de voto")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            urna_iniciada = False  # Reiniciar el estado de la urna al iniciar un nuevo censo
            iniciar_censo()
            print("Censo electoral iniciado correctamente.")
            censo_iniciado = True

        elif opcion == "2":
            if not censo_iniciado:
                print("Primero debe iniciar el censo electoral.")
            else:
                iniciar_urna()
                print("Urna iniciada correctamente.")
                urna_iniciada = True

        if opcion == "3":
            if not urna_iniciada:
                print("Primero debe iniciar la urna.")
            else:
                iniciar_conjuntos_codificacion()
                print("Conjuntos de codificación iniciados correctamente.")


if __name__ == "__main__":  
    main()
    