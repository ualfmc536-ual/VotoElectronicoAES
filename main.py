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
    carpeta_datos = Path(__file__).resolve().parent / "Documentos"
    archivo_votantes = carpeta_datos / "votantes.txt"
    with open(archivo_votantes, "r", encoding="utf-8") as votantes:
        lista = [linea.strip() for linea in votantes if linea.strip()]

    global num_votantes
    num_votantes = len(lista)
    with open("censo.txt", "w", encoding="utf-8") as archivo:
        for identificador in range(1, num_votantes + 1):
            archivo.write(f"{identificador}\n")


def verificar_voto(id_votante: int) -> bool:
    """Indica si el ID existe en el censo y aún no tiene índice asignado."""
    with open("censo.txt", "r", encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.split()
            if campos and int(campos[0]) == id_votante:
                return len(campos) == 1
    return False


def obtener_votantes_pendientes() -> list[int]:
    """Devuelve los IDs del censo que todavía no tienen un índice asignado."""
    with open("censo.txt", "r", encoding="utf-8") as archivo:
        return [
            int(campos[0])
            for linea in archivo
            if (campos := linea.split()) and len(campos) == 1
        ]


def actualizar_censo(id_votante: int, index: int) -> None:
    """Guarda el índice de urna asignado junto al ID del votante."""
    with open("censo.txt", "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    censo_actualizado = []
    id_encontrado = False
    for linea in lineas:
        campos = linea.split()
        if campos and int(campos[0]) == id_votante:
            censo_actualizado.append(f"{id_votante}\t{index}\n")
            id_encontrado = True
        else:
            censo_actualizado.append(linea)

    if not id_encontrado:
        raise ValueError(f"El ID {id_votante} no aparece en el censo.")

    with open("censo.txt", "w", encoding="utf-8") as archivo:
        archivo.writelines(censo_actualizado)


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
    if num_votantes <= 0:
        raise ValueError("Debe haber votantes en el censo para registrar un voto.")

    while True:
        try:
            id_votante = int(input(f"Introduzca el ID del votante (1-{num_votantes}): "))
        except ValueError:
            print("El ID debe ser un número entero.")
            continue

        if 1 <= id_votante <= num_votantes:
            if verificar_voto(id_votante):
                break
            print(f"El ID {id_votante} ya ha votado o no aparece en el censo.")
        else:
            print(f"ID no válido. Introduzca un número entre 1 y {num_votantes}.")

    index = generador.choice(índices_restantes)

    print("ID del votante: ", id_votante)
    print("Índice aleatorio asignado en la urna: ", index)
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
    print("Ingrese el valor del polinomio en el índice asignado: ")
    valor = int(input())
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
    actualizar_censo(id_votante, index)
    índices_restantes = [indice for indice in índices_restantes if indice != index]

def realizar_voto_automatico():
    global índices_restantes
    while índices_restantes:
        with open("censo.txt", "r", encoding="utf-8") as archivo:
            registros_censo = [linea.split() for linea in archivo if linea.strip()]

        ids_pendientes = [
            int(registro[0]) for registro in registros_censo if len(registro) == 1
        ]
        índices_asignados = {
            int(registro[1]) for registro in registros_censo if len(registro) > 1
        }
        índices_restantes = [
            indice for indice in índices_restantes
            if indice not in índices_asignados
        ]
        if not ids_pendientes or not índices_restantes:
            break

        id_votante = generador.choice(ids_pendientes)
        index = generador.choice(índices_restantes)

        print("ID del votante: ", id_votante)
        print("Índice asignado en la urna: ", index)
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
        actualizar_censo(id_votante, index)
        índices_restantes.remove(index)

def generar_polinomio(grado: int) -> list[int]:
    if grado < 0:
        raise ValueError("El grado debe ser mayor o igual que 0")

    # Coeficientes desde el término independiente hasta x^(grado - 1).
    coeficientes = [generador.randrange(p) for _ in range(grado)]

    # El coeficiente principal no puede ser 0 si queremos ese grado exacto.
    coeficientes.append(generador.randrange(1, p))

    return coeficientes



def main(): 
    censo_iniciado = False
    urna_iniciada = False
    votacion_terminada = False
    while True:
        print("Menú de votación AES")
        print("Opciones:")
        print("1. Iniciar censo electoral")
        print("2. Iniciar algoritmo SKGA")
        print("3. Iniciar conjuntos de codificación")
        print("4. Iniciar algoritmo de recolección y proceso de voto")
        print("5. Iniciar algoritmo de recuento y recuento de votos")
        print("6. Salir")
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
                print("Iniciando algoritmo SKGA...")
                algoritmo_skga = alg_skga()
                algoritmo_skga.iniciar_urnas()
                print("Algoritmo SKGA iniciado correctamente.")
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
            elif not obtener_votantes_pendientes():
                print("No quedan votantes pendientes.")
            else:
                algoritmo_recoleccion = alg_recoleccion()
                algoritmo_recoleccion.presentar_menu()
        
        elif opcion == "5":
            if not urna_iniciada:
                print("Primero debe iniciar la urna.")
            else:
                print("Iniciando algoritmo de recolección y recuento de votos...")
                algoritmo_recuento = alg_recuento()
                algoritmo_recuento.realizar_recuento()
                print("Recuento guardado correctamente en recuento.txt.")
        elif opcion == "6":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción del 1 al 6.")


class alg_skga:
    """Clase auxiliar para inicializar urnas y generar una clave.

    Reutiliza la lógica del flujo principal del proyecto, sin romper la
    funcionalidad actual de main().
    """
    # Constructor
    def __init__(self):
        pass

    # Función de iniciar urnas
    def iniciar_urnas(self):
        """Inicializa la urna utilizando la misma lógica que iniciar_urna()."""
        if num_votantes <= 0:
            raise ValueError("Debe iniciar el censo antes de inicializar la urna.")
        iniciar_urna()
        return True

    # Función de crear clave
    def crear_clave(self, longitud: int = 16) -> str:
        """Genera una clave aleatoria de tipo numérico para la votación."""
        if longitud <= 0:
            raise ValueError("La longitud de la clave debe ser mayor que 0.")

        clave = "".join(str(generador.randint(0, 9)) for _ in range(longitud))
        return clave


class alg_recoleccion:
    """Gestiona el menú del proceso de votación."""

    def presentar_menu(self):
        global índices_restantes
        votantes_pendientes = obtener_votantes_pendientes()
        if not votantes_pendientes:
            print("No quedan votantes pendientes.")
            return

        with open("censo.txt", "r", encoding="utf-8") as archivo:
            índices_asignados = {
                int(campos[1])
                for linea in archivo
                if len(campos := linea.split()) > 1
            }
        índices_restantes = [
            indice
            for indice in range(num_votantes)
            if indice not in índices_asignados
        ]

        while índices_restantes:
            print("1. Iniciar proceso de voto manual")
            print("2. Iniciar proceso de voto automático")
            opcion_voto = input("Seleccione una opción: ")

            if opcion_voto == "1":
                self.realizar_voto_manual()
                print("Proceso de voto manual terminado correctamente.")
            elif opcion_voto == "2":
                self.realizar_voto_automatico()
                print("Proceso de voto automático terminado correctamente.")
            else:
                print("Opción de voto no válida. Por favor, seleccione 1 o 2.")

    def realizar_voto_manual(self):
        realizar_voto_manual()

    def realizar_voto_automatico(self):
        realizar_voto_automatico()


class alg_recuento:
    """Calcula el recuento por columna a partir de los datos de la urna."""

    def realizar_recuento(self) -> list[int]:
        with open("urna.txt", "r", encoding="utf-8") as archivo:
            lineas = [linea.split() for linea in archivo if linea.strip()]

        if len(lineas) < 2:
            raise ValueError("El archivo urna.txt debe contener al menos dos líneas.")

        valores_segunda_linea = [int(valor) for valor in lineas[1]]
        if any(len(fila) != len(valores_segunda_linea) for fila in lineas):
            raise ValueError("Las filas de urna.txt deben tener el mismo número de columnas.")

        sumas_por_columna = [0] * len(valores_segunda_linea)

        for fila in lineas[2:]:
            for columna, valor in enumerate(fila):
                sumas_por_columna[columna] = (
                    sumas_por_columna[columna] + int(valor)
                ) % p

        recuento = [
            (suma - valor_segunda_linea) % p
            for suma, valor_segunda_linea in zip(
                sumas_por_columna, valores_segunda_linea
            )
        ]

        ruta_recuento = Path(__file__).resolve().parent / "Documentos" / "recuento.txt"
        with open(ruta_recuento, "w", encoding="utf-8") as archivo:
            archivo.write("Recuento de votos por columna:\n")
            archivo.write("\t".join(map(str, recuento)) + "\n")

        self.contar_votos()
        return recuento

    def contar_votos(self) -> dict[str, int]:
        ruta_recuento = Path(__file__).resolve().parent / "Documentos" / "recuento.txt"
        ruta_codificaciones = (
            Path(__file__).resolve().parent / "conjuntos_codificacion.txt"
        )

        with open(ruta_recuento, "r", encoding="utf-8") as archivo:
            lineas_recuento = archivo.readlines()
        if len(lineas_recuento) < 2:
            raise ValueError("recuento.txt debe contener una segunda línea con los votos.")
        votos_por_columna = [
            int(valor) for valor in lineas_recuento[1].split()
        ]

        codificaciones: dict[str, set[int]] = {}
        candidato_actual = None
        prefijo_candidato = "Conjunto de codificación del "
        with open(ruta_codificaciones, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea.startswith(prefijo_candidato):
                    candidato_actual = linea[len(prefijo_candidato):].rstrip(":").strip()
                    codificaciones[candidato_actual] = set()
                elif linea and candidato_actual is not None:
                    codificaciones[candidato_actual].update(
                        int(valor) for valor in linea.split()
                    )

        if not codificaciones:
            raise ValueError("No se encontraron conjuntos de codificación de candidatos.")

        votos_por_candidato = {candidato: 0 for candidato in codificaciones}
        for valor_voto in votos_por_columna:
            candidatos_coincidentes = [
                candidato
                for candidato, valores in codificaciones.items()
                if valor_voto in valores
            ]
            if len(candidatos_coincidentes) != 1:
                raise ValueError(
                    f"El valor {valor_voto} no pertenece a un único candidato."
                )
            votos_por_candidato[candidatos_coincidentes[0]] += 1

        for candidato, cantidad in votos_por_candidato.items():
            print(f"{candidato}: {cantidad} votos")

        maximo_votos = max(votos_por_candidato.values())
        candidatos_ganadores = [
            candidato
            for candidato, cantidad in votos_por_candidato.items()
            if cantidad == maximo_votos
        ]
        if len(candidatos_ganadores) == 1:
            print(f"Candidato con mayor número de votos: {candidatos_ganadores[0]}")
        else:
            print(
                "Empate en el mayor número de votos: "
                + ", ".join(candidatos_ganadores)
            )

        return votos_por_candidato


if __name__ == "__main__":  
    main()
