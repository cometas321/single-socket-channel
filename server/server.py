import socket
import threading
import pickle

# Almacén de clientes conectados
clients = {}

def handle_client(client_socket, client_address, client_id):
    """
    Maneja la comunicación con un cliente específico.
    """
    try:
        while True:
            # Leer el tamaño del mensaje
            data = client_socket.recv(4)
            if not data:
                break
            message_length = int.from_bytes(data, 'big')
            request_data = client_socket.recv(message_length)
            message = pickle.loads(request_data)

            print(f"Mensaje recibido de {client_id}: {message}")

            # Enviar el mensaje al destinatario
            if message["to"] in clients:
                recipient_socket = clients[message["to"]]
                response = pickle.dumps({"from": client_id, "message": message["message"]})
                recipient_socket.sendall(len(response).to_bytes(4, 'big'))
                recipient_socket.sendall(response)
            else:
                print(f"Cliente {message['to']} no está conectado.")

    except Exception as e:
        print(f"Error con el cliente {client_id}: {e}")
    finally:
        print(f"Cliente {client_id} desconectado.")
        del clients[client_id]
        client_socket.close()

def start_server():
    """
    Inicia el servidor que escucha conexiones de clientes.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 8080))
    server_socket.listen(5)
    print("Servidor escuchando en 127.0.0.1:8080")

    while True:
        client_socket, client_address = server_socket.accept()
        # Asignar un identificador único al cliente (puede ser un nombre o ID)
        client_id = client_socket.recv(1024).decode('utf-8')
        print(f"Cliente {client_id} conectado desde {client_address}")
        clients[client_id] = client_socket
        threading.Thread(target=handle_client, args=(client_socket, client_address, client_id)).start()

start_server()
