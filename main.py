"""
Created on 24/10/2026
@author: francisco montes, miguel, jose antonio, francisco sánchez
"""
from random import Random
from pathlib import Path

# Variables globales
generador = Random()
p = 13                  # Número primo para el módulo
num_votantes = 0        # Número de votantes
nº_candidatos = 2       # Número de candidatos
conjuntos_codificacion: list[list[int]] = []   # Listas de codificación para cada candidato
índices_restantes = []  # Lista de índices de votantes que aún no han votado

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
    with open("urna.txt", "w") as archivo:
        for i in range(num_votantes):
            archivo.write(str(generador.randint(0, 100)%p) + " \t")
        archivo.write("\n")
        for i in range(num_votantes):
            archivo.write(str(0) + " \t")
        archivo.write("\n")

def iniciar_conjuntos_codificacion():
    global conjuntos_codificacion
    conjuntos_codificacion.clear()
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


def realizar_voto_manual():
    global índices_restantes
    index = generador.choice(índices_restantes)

    print("Indice del votante: ", index)
    polinomio = generar_polinomio(num_votantes + 1)
    print("Polinomio generado: ", end="")
    for i in range(len(polinomio)):
        print(polinomio[i], end="")
        if i == 0:
            print(" + ", end="")
            continue
        elif i == len(polinomio) - 1:
            print("x^" + str(i), end="")
            break
        if i < len(polinomio):
            print("x^" + str(i) + " + ", end="")
    print("\n")
    print("Ingrese el valor del polinomio en el índice del votante: ")
    valor = int(input())
    print("Imprimiendo el valor ingresado: ", valor)
    valor = valor % p
    with open("urna.txt", "a+", encoding="utf-8") as archivo:
        archivo.seek(0)
        primera_fila = archivo.readline()
        numeros_aleatorios = [int(valor) for valor in primera_fila.split()]
    # Se calculan los valores del polinomio con los valores aleatorios
        valores_polinomio = []
        for i in range(len(numeros_aleatorios)):   
            valor_polinomio = 0
            for j in range(len(polinomio)):
                valor_polinomio += polinomio[j] * (numeros_aleatorios[i] ** j)
            valores_polinomio.append(valor_polinomio % p)
    # Se añade la nueva fila al final con el valor ingresado en el índice correspondiente
    # Se leen las líneas existentes del archivo
    with open("urna.txt", "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()
    # Calcula estos valores usando tus datos:
    # nueva_segunda_fila
    segunda_fila = lineas[1].strip().split()
    valores_segunda_fila = [int(valor) for valor in segunda_fila]
    nueva_segunda_fila = []
    for i in range(len(numeros_aleatorios)):
        nueva_segunda_fila.append((valores_polinomio[i] + valores_segunda_fila[i]) % p)

    # nueva_fila
    nueva_fila = []
    for i in range(len(numeros_aleatorios)):
        if i == index:
            nueva_fila.append(valor)
        else:
            nueva_fila.append(valores_polinomio[i])

    # Se reescriben las líneas en el archivo, reemplazando la segunda fila y agregando la nueva fila al final
    with open("urna.txt", "w", encoding="utf-8") as archivo:
        archivo.write(lineas[0])  # Primera fila
        archivo.write("\t".join(map(str, nueva_segunda_fila)) + "\n")  # Nueva segunda fila
        archivo.writelines(lineas[2:])  # Resto de las líneas
        archivo.write("\t".join(map(str, nueva_fila)) + "\n")  # Nueva fila al final
    índices_restantes.remove(index)

def realizar_voto_automatico():
    global índices_restantes
    while índices_restantes:
        index = generador.choice(índices_restantes)

        print("Indice del votante: ", index)
        polinomio = generar_polinomio(num_votantes + 1)
        print("Polinomio generado: ", end="")
        for i in range(len(polinomio)):
            print(polinomio[i], end="")
            if i == 0:
                print(" + ", end="")
                continue
            elif i == len(polinomio) - 1:
                print("x^" + str(i), end="")
                break
            if i < len(polinomio):
                print("x^" + str(i) + " + ", end="")
        print("\n")
        valor = generador.randint(0, p - 1)
        print("Valor aleatorio generado para el polinomio en el índice del votante: ", valor)
        with open("urna.txt", "a+", encoding="utf-8") as archivo:
            archivo.seek(0)
            primera_fila = archivo.readline()
            numeros_aleatorios = [int(valor) for valor in primera_fila.split()]
        # Se calculan los valores del polinomio con los valores aleatorios
            valores_polinomio = []
            for i in range(len(numeros_aleatorios)):   
                valor_polinomio = 0
                for j in range(len(polinomio)):
                    valor_polinomio += polinomio[j] * (numeros_aleatorios[i] ** j)
                valores_polinomio.append(valor_polinomio % p)
        # Se añade la nueva fila al final con el valor ingresado en el índice correspondiente
        # Se leen las líneas existentes del archivo
        with open("urna.txt", "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
        # Calcula estos valores usando tus datos:
        # nueva_segunda_fila
        segunda_fila = lineas[1].strip().split()
        valores_segunda_fila = [int(valor) for valor in segunda_fila]
        nueva_segunda_fila = []
        for i in range(len(numeros_aleatorios)):
            nueva_segunda_fila.append((valores_polinomio[i] + valores_segunda_fila[i]) % p)

        # nueva_fila
        nueva_fila = []
        for i in range(len(numeros_aleatorios)):
            if i == index:
                nueva_fila.append(valor)
            else:
                nueva_fila.append(valores_polinomio[i])
        # Se reescriben las líneas en el archivo, reemplazando la segunda fila y agregando la nueva fila al final
        with open("urna.txt", "w", encoding="utf-8") as archivo:
            archivo.write(lineas[0])  # Primera fila
            archivo.write("\t".join(map(str, nueva_segunda_fila)) + "\n")  # Nueva segunda fila
            archivo.writelines(lineas[2:])  # Resto de las líneas
            archivo.write("\t".join(map(str, nueva_fila)) + "\n")  # Nueva fila al final
        índices_restantes.remove(index) 

def generar_polinomio(grado: int) -> list[int]:
    if grado < 0:
        raise ValueError("El grado debe ser mayor o igual que 0")

    # Coeficientes desde el término independiente hasta x^(grado - 1).
    coeficientes = [generador.randrange(p) for _ in range(grado)]

    # El coeficiente principal no puede ser 0 si queremos ese grado exacto.
    coeficientes.append(generador.randrange(1, p))

    return coeficientes

def realizar_recuento():
    with open("urna.txt", "r", encoding="utf-8") as archivo:


def main(): 
    censo_iniciado = False
    urna_iniciada = False
    votacion_terminada = False
    while True:
        print("Menú de votación AES")
        print("Opciones:")
        print("1. Iniciar censo electoral")
        print("2. Iniciar urna")
        print("3. Iniciar conjuntos de codificación")
        print("4. Iniciar proceso de voto")
        print("5. Realizar recuento de votos")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            urna_iniciada = False  # Reiniciar el estado de la urna al iniciar un nuevo censo
            print("Iniciando censo electoral...")
            iniciar_censo()
            print("Censo electoral iniciado correctamente.")
            censo_iniciado = True

        elif opcion == "2":
            if not censo_iniciado:
                print("Primero debe iniciar el censo electoral.")
            else:
                print("Iniciando urna...")
                iniciar_urna()
                print("Urna iniciada correctamente.")
                urna_iniciada = True

        elif opcion == "3":
            if not urna_iniciada:
                print("Primero debe iniciar la urna.")
            else:
                iniciar_conjuntos_codificacion()
                print("Conjuntos de codificación iniciados correctamente.")

        elif opcion == "4":
            if not urna_iniciada:
                print("Primero debe iniciar la urna.")
            else:
                global índices_restantes
                índices_restantes = list(range(num_votantes))
                while índices_restantes:
                    print("1.Iniciar proceso de voto manual")
                    print("2.Iniciar proceso de voto automático")
                    opcion_voto = input("Seleccione una opción: ")
                    if opcion_voto == "1":
                        realizar_voto_manual()
                        print("Proceso de voto manual terminado correctamente.")

                    elif opcion_voto == "2":
                        realizar_voto_automatico()
                        print("Proceso de voto automático terminado correctamente.")

                    else:
                        print("Opción de voto no válida. Por favor, seleccione 1 o 2.")
                    index = generador.randint(0, num_votantes - 1)

                    # Aquí se implementaría la lógica del proceso de voto
                    # Por ahora, solo mostramos un mensaje
                    print("Proceso de voto iniciado correctamente.")
        
        elif opcion == 5:
            print("Realizando recuento de votos...")
            realizar_recuento()
        else:
            print("Opción no válida. Por favor, seleccione una opción del 1 al 4.")

if __name__ == "__main__":  
    main()
