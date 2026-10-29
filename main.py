"""
Created on 24/10/2026
@author: francisco montes, miguel, jose antonio, francisco sánchez
"""
import ast
from random import Random
from pathlib import Path
import os
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes


# Variables globales
clave: bytes = b""
generador = Random()
p = 13                  # Número primo para el módulo
num_votantes = 0        # Número de votantes
nº_candidatos = 2       # Número de candidatos
conjuntos_codificacion: list[list[int]] = []   # Listas de codificación para cada candidato
índices_restantes = []  # Lista de índices de votantes que aún no han votado


def iniciar_censo():
    carpeta_datos = Path(__file__).resolve().parent / "Documentos"
    carpeta_datos.mkdir(parents=True, exist_ok=True)
    archivo_votantes = carpeta_datos / "votantes.txt"
    
    if not archivo_votantes.exists():
        with open(archivo_votantes, "w", encoding="utf-8") as votantes:
            votantes.write("Votante 1\nVotante 2\nVotante 3\n")

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
    global clave
    clave = alg_skga.crear_clave()
    guardar_clave_texto_cifrado(clave)
  
    with open("urna.txt", "w", encoding="utf-8") as archivo:
        for i in range(num_votantes):
            archivo.write(str(generador.randint(0, 100) % p) + " \t")
        archivo.write("\n")
        
        cero = encoder(str(0), clave)
        for i in range(num_votantes):
            # Guardamos en formato hexadecimal legible por fromhex()
            archivo.write(cero.hex() + " \t\t")
        archivo.write("\n")


def iniciar_conjuntos_codificacion():
    global conjuntos_codificacion
    conjuntos_codificacion.clear()
    lista_candidatos = []
    for i in range(nº_candidatos):
        lista_candidatos.append("Candidato " + str(i + 1))
        conjuntos_codificacion.append([lista_candidatos[i]])
    lista_numeros = list(range(p))

    for i in range(p):
        numero_aleatorio = generador.randint(0, len(lista_numeros) - 1)
        candidato_index = i % len(lista_candidatos)
        conjuntos_codificacion[candidato_index].append(lista_numeros[numero_aleatorio]) 
        lista_numeros.pop(numero_aleatorio)

    with open("conjuntos_codificacion.txt", "w", encoding="utf-8") as archivo:
        for i in range(len(conjuntos_codificacion)):
            archivo.write("Conjunto de codificación del " + conjuntos_codificacion[i][0] + ": \n")
            for j in range(1, len(conjuntos_codificacion[i])):
                archivo.write(str(conjuntos_codificacion[i][j]) + " \t")
            archivo.write("\n")


def realizar_voto_manual():
    global índices_restantes
    clave_k = 0
    if num_votantes <= 0:
        raise ValueError("Debe haber votantes en el censo para registrar un voto.")

    while True:
        try:
            mensaje_no_encriptado = input(f"Introduzca el ID del votante (1-{num_votantes}): ")
            print("Enviando mensaje encriptado...")
            clave_k = get_random_bytes(16)

            mensaje_encriptado = encoder(str(mensaje_no_encriptado),clave_k)

            print ("Mensaje encriptado: ", mensaje_encriptado.hex())
            guardar_clave_texto_cifrado(clave_k)
            
            id_votante = int(decoder(mensaje_encriptado,clave_k))

        except ValueError:
            mensaje_encriptado = encoder("El ID debe ser un número entero.",clave_k)
            print("Recibiendo mensaje encriptado: ", mensaje_encriptado)
            print("Desencriptando mensaje...")
            print(decoder(mensaje_encriptado,clave_k))
            continue

        if 1 <= id_votante <= num_votantes:
            if verificar_voto(id_votante):
                break
            mensaje_encriptado = encoder(f"El ID {id_votante} ya ha votado o no aparece en el censo.",clave_k)
            print("Recibiendo mensaje encriptado: ", mensaje_encriptado)
            print("Desencriptando mensaje...")
            print(decoder(mensaje_encriptado,clave_k))
        else:
            mensaje_encriptado = encoder(f"ID no válido. Introduzca un número entre 1 y {num_votantes}.",clave_k)
            print("Recibiendo mensaje encriptado: ", mensaje_encriptado)
            print("Desencriptando mensaje...")
            print(decoder(mensaje_encriptado,clave_k))
        
    index = generador.choice(índices_restantes)

    mensaje_encriptado = encoder(f"ID no válido. Introduzca un número entre 1 y {num_votantes}.",clave_k)
    print("Recibiendo mensaje encriptado: ", mensaje_encriptado)
    print("Desencriptando mensaje...")
    print(decoder(mensaje_encriptado,clave_k))

    respuesta = "Índice aleatorio asignado en la urna: " + str(index) + "\n"
    respuesta += "Polinomio generado: "
    # print("Índice aleatorio asignado en la urna: ", index)
    polinomio = generar_polinomio(num_votantes + 1)
    # print("Polinomio generado: ", end="")
    for i in range(len(polinomio)):
        respuesta += str(polinomio[i]) 
        if i == 0:
            respuesta += " + "
            continue
        elif i == len(polinomio) - 1:
            respuesta += "x^" + str(i)
            break
        if i < len(polinomio):
            respuesta += "x^" + str(i) + " + "
    respuesta += "\n"
    respuesta += "Ingrese el valor del polinomio en el índice asignado: "

    mensaje_encriptado = encoder(respuesta,clave_k)
    print("Recibiendo mensaje encriptado: ", mensaje_encriptado)
    print("Desencriptando mensaje...")
    print(decoder(mensaje_encriptado,clave_k))

    valor = int(input()) % p

    mensaje_no_encriptado = str(valor)
    
    print("Enviando mensaje encriptado...")
    clave_k = get_random_bytes(16)
    
    mensaje_encriptado = encoder(str(mensaje_no_encriptado),clave_k)
    
    print ("Mensaje encriptado: ", mensaje_encriptado.hex())
    guardar_clave_texto_cifrado(clave_k)
                
    valor = int(decoder(mensaje_encriptado,clave_k))
    
    with open("urna.txt", "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    primera_fila = lineas[0]
    numeros_aleatorios = [int(v) for v in primera_fila.split()]

    valores_polinomio = []
    for i in range(len(numeros_aleatorios)):   
        valor_polinomio = 0
        for j in range(len(polinomio)):
            valor_polinomio += polinomio[j] * (numeros_aleatorios[i] ** j)
        valores_polinomio.append(valor_polinomio % p)

    segunda_fila = lineas[1].strip().split()
    for i in range(len(segunda_fila)):
        datos_en_bytes = bytes.fromhex(segunda_fila[i])
        segunda_fila[i] = decoder(datos_en_bytes, clave)

    valores_segunda_fila = [int(v) for v in segunda_fila]
    nueva_segunda_fila = []
    for i in range(len(numeros_aleatorios)):
        nueva_segunda_fila.append((valores_polinomio[i] + valores_segunda_fila[i]) % p)

    for i in range(len(nueva_segunda_fila)):
        texto_cifrado_bytes = encoder(str(nueva_segunda_fila[i]), clave)
        nueva_segunda_fila[i] = texto_cifrado_bytes.hex()

    nueva_fila = []
    for i in range(len(numeros_aleatorios)):
        if i == index:
            nueva_fila.append(valor)
        else:
            nueva_fila.append(valores_polinomio[i])

    with open("urna.txt", "w", encoding="utf-8") as archivo:
        archivo.write(lineas[0])
        archivo.write("\t".join(nueva_segunda_fila) + "\n")
        archivo.writelines(lineas[2:])
        archivo.write("\t".join(map(str, nueva_fila)) + "\n")

    actualizar_censo(id_votante, index)
    índices_restantes = [i for i in índices_restantes if i != index]

def formatear_polinomio(coeficientes: list[int]) -> str:
    """Convierte la lista de coeficientes [a0, a1, a2, ...] en una cadena legible: a0 + a1*x + a2*x^2 ..."""
    terminos = []
    for grado, coef in enumerate(coeficientes):
        if grado == 0:
            terminos.append(str(coef))
        elif grado == 1:
            terminos.append(f"{coef}x")
        else:
            terminos.append(f"{coef}x^{grado}")
    return " + ".join(terminos)


def realizar_voto_automatico():
    global índices_restantes

    with open("censo.txt", "r", encoding="utf-8") as archivo:
        registros_censo = [linea.split() for linea in archivo if linea.strip()]

    ids_pendientes = [int(r[0]) for r in registros_censo if len(r) == 1]
    índices_ocupados = {int(r[1]) for r in registros_censo if len(r) > 1}
    índices_libres = [i for i in range(num_votantes) if i not in índices_ocupados]

    if not ids_pendientes or not índices_libres:
        print("No hay votantes pendientes o ya no quedan urnas libres.")
        return

    while ids_pendientes and índices_libres:
        id_votante = generador.choice(ids_pendientes)
        index = generador.choice(índices_libres)

        print(f"ID del votante: {id_votante}")
        print(f"Índice asignado en la urna: {index}")

        # Generar y mostrar el polinomio
        polinomio = generar_polinomio(num_votantes + 1)
        texto_polinomio = formatear_polinomio(polinomio)
        print(f"Polinomio generado: {texto_polinomio}")

        valor = generador.randint(0, p - 1)
        print(f"Valor aleatorio generado para el polinomio en el índice del votante: {valor}\n")

        with open("urna.txt", "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()

        primera_fila = lineas[0]
        numeros_aleatorios = [int(v) for v in primera_fila.split()]

        # Evaluar polinomio
        valores_polinomio = []
        for aleatorio in numeros_aleatorios:
            val = 0
            for grado, coef in enumerate(polinomio):
                val += coef * (aleatorio ** grado)
            valores_polinomio.append(val % p)

        # Descifrar la segunda fila
        segunda_fila = lineas[1].strip().split()
        valores_segunda_fila = []
        for elem_hex in segunda_fila:
            elem_bytes = bytes.fromhex(elem_hex)
            valores_segunda_fila.append(int(decoder(elem_bytes, clave)))

        # Sumar y volver a cifrar
        nueva_segunda_fila_hex = []
        for i in range(len(numeros_aleatorios)):
            suma = (valores_polinomio[i] + valores_segunda_fila[i]) % p
            cifrado_bytes = encoder(str(suma), clave)
            nueva_segunda_fila_hex.append(cifrado_bytes.hex())

        nueva_fila = []
        for i in range(len(numeros_aleatorios)):
            if i == index:
                nueva_fila.append(valor)
            else:
                nueva_fila.append(valores_polinomio[i])

        with open("urna.txt", "w", encoding="utf-8") as archivo:
            archivo.write(lineas[0])
            archivo.write("\t".join(nueva_segunda_fila_hex) + "\n")
            archivo.writelines(lineas[2:])
            archivo.write("\t".join(map(str, nueva_fila)) + "\n")

        actualizar_censo(id_votante, index)

        ids_pendientes.remove(id_votante)
        índices_libres.remove(index)

    índices_restantes = índices_libres

def generar_polinomio(grado: int) -> list[int]:
    if grado < 0:
        raise ValueError("El grado debe ser mayor o igual que 0")

    coeficientes = [generador.randrange(p) for _ in range(grado)]
    coeficientes.append(generador.randrange(1, p))
    return coeficientes


def main(): 
    censo_iniciado = False
    urna_iniciada = False
    while True:
        print("\nMenú de votación AES")
        print("1. Iniciar censo electoral")
        print("2. Iniciar algoritmo SKGA")
        print("3. Iniciar conjuntos de codificación")
        print("4. Iniciar algoritmo de recolección y proceso de voto")
        print("5. Iniciar algoritmo de recuento y recuento de votos")
        print("6. Desencriptar mensaje")
        print("7. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            urna_iniciada = False
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
            texto_hex = input("Introduzca el texto cifrado en hexadecimal: ").strip()
            clave_hex = input("Introduzca la clave en hexadecimal: ").strip()

            try:
                texto_bytes = bytes.fromhex(texto_hex)
                clave_bytes = bytes.fromhex(clave_hex)
            except ValueError:
                print("Error: Una de las entradas no contiene caracteres hexadecimales válidos.")
                continue

            if len(clave_bytes) not in (16, 24, 32):
                print(f"Error: La clave debe tener 16, 24 o 32 bytes (32, 48 o 64 caracteres hex). Longitud actual: {len(clave_bytes)} bytes.")
                continue

            if len(texto_bytes) < 32 or len(texto_bytes) % 16 != 0:
                print("Error: El texto cifrado debe incluir el IV (16 bytes) y bloques múltiplos de 16 bytes.")
                continue

            try:
                mensaje = decoder(texto_bytes, clave_bytes)
                print(f"Mensaje descifrado: {mensaje}")
            except Exception as error:
                print(f"No se pudo desencriptar el mensaje: {error}")
        elif opcion == "7":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción del 1 al 7.")


def encoder(texto: str, clave: bytes) -> bytes:
    texto_bytes = str(texto).encode("utf-8")
    pad = 16 - (len(texto_bytes) % 16)
    texto_padded = texto_bytes + bytes([pad] * pad)
    cipher = AES.new(clave, AES.MODE_CBC)
    return cipher.iv + cipher.encrypt(texto_padded)


def decoder(texto_encriptado: bytes, clave: bytes) -> str:
    iv = texto_encriptado[:16]
    ciphertext = texto_encriptado[16:]
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    texto_padded = cipher.decrypt(ciphertext)
    pad = texto_padded[-1]
    texto_bytes = texto_padded[:-pad]
    return texto_bytes.decode("utf-8")


def guardar_clave_texto_cifrado(clave_bytes: bytes):
    with open("claves.txt", "a", encoding="utf-8") as f:
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{hora} | AES: {clave_bytes.hex()} \n")


class alg_skga:
    def __init__(self):
        pass

    def iniciar_urnas(self):
        if num_votantes <= 0:
            raise ValueError("Debe iniciar el censo antes de inicializar la urna.")
        iniciar_urna()
        return True

    @staticmethod
    def crear_clave() -> bytes:
        return get_random_bytes(16)


class alg_recoleccion:
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

        while índices_restantes and obtener_votantes_pendientes():
            print("\n1. Iniciar proceso de voto manual")
            print("2. Iniciar proceso de voto automático")
            print("3. Volver al menú principal")
            opcion_voto = input("Seleccione una opción: ")

            if opcion_voto == "1":
                self.realizar_voto_manual()
                print("Proceso de voto manual terminado correctamente.")
            elif opcion_voto == "2":
                self.realizar_voto_automatico()
                print("Proceso de voto automático terminado correctamente.")
            elif opcion_voto == "3":
                break
            else:
                print("Opción de voto no válida. Por favor, seleccione 1, 2 o 3.")

    def realizar_voto_manual(self):
        realizar_voto_manual()

    def realizar_voto_automatico(self):
        realizar_voto_automatico()


class alg_recuento:
    def realizar_recuento(self) -> list[int]:
        with open("urna.txt", "r", encoding="utf-8") as archivo:
            lineas = [linea.split() for linea in archivo if linea.strip()]

        if len(lineas) < 2:
            raise ValueError("El archivo urna.txt debe contener al menos dos líneas.")

        # Desciframos la segunda fila que está guardada en hex AES
        segunda_fila_hex = lineas[1]
        valores_segunda_linea = [
            int(decoder(bytes.fromhex(item), clave)) for item in segunda_fila_hex
        ]

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
        ruta_recuento.parent.mkdir(parents=True, exist_ok=True)
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

        print("\n--- Resultados del recuento ---")
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