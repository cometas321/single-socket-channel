import socket
import pickle
from threading import Thread
from tkinter import Tk, Label, Entry, Button, Text, END

class ChatClient:
    def __init__(self, root, client_id):
        self.root = root
        self.root.title(f"Cliente: {client_id}")
        self.client_id = client_id.strip()

        # Configuración del socket
        self.server_address = ("socket_server", 8080)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.server_address)

        # Enviar el ID del cliente al servidor
        self.socket.sendall(self.client_id.encode('utf-8'))

        # Configuración de la interfaz gráfica
        Label(root, text="Destinatario:").grid(row=0, column=0, padx=10, pady=10)
        self.recipient_entry = Entry(root, width=30)
        self.recipient_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(root, text="Mensaje:").grid(row=1, column=0, padx=10, pady=10)
        self.message_entry = Entry(root, width=30)
        self.message_entry.grid(row=1, column=1, padx=10, pady=10)

        self.send_button = Button(root, text="Enviar", command=self.send_message)
        self.send_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.chat_text = Text(root, height=15, width=50)
        self.chat_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Hilo para recibir mensajes
        self.receive_thread = Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def send_message(self):
        """
        Envía un mensaje al destinatario especificado.
        """
        recipient = self.recipient_entry.get().strip()  # Limpia el destinatario
        message = self.message_entry.get()
        if not recipient or not message:
            self.append_chat("Debes especificar un destinatario y un mensaje.")
            return

        # Crear un paquete con el mensaje y el destinatario
        packet = {"to": recipient, "message": message}
        serialized_packet = pickle.dumps(packet)
        self.socket.sendall(len(serialized_packet).to_bytes(4, 'big'))
        self.socket.sendall(serialized_packet)

        self.append_chat(f"Yo (a {recipient}): {message}")
        self.message_entry.delete(0, END)

    def receive_messages(self):
        """
        Escucha mensajes desde el servidor y los muestra en el chat.
        """
        while True:
            try:
                data = self.socket.recv(4)
                if not data:
                    break
                message_length = int.from_bytes(data, 'big')
                response_data = self.socket.recv(message_length)
                response = pickle.loads(response_data)

                sender = response["from"]
                message = response["message"]
                self.append_chat(f"{sender}: {message}")
            except Exception as e:
                self.append_chat(f"Error recibiendo mensaje: {e}")
                break

    def append_chat(self, text):
        """
        Muestra un mensaje en el área de chat.
        """
        self.chat_text.insert(END, f"{text}\n")
        self.chat_text.see(END)

    def close_connection(self):
        """
        Cierra la conexión del socket.
        """
        self.socket.close()

if __name__ == "__main__":
    client_id = input("Introduce tu ID de cliente: ")
    root = Tk()
    app = ChatClient(root, client_id)
    root.protocol("WM_DELETE_WINDOW", app.close_connection)
    root.mainloop()
