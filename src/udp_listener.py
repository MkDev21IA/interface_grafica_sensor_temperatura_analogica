# src/udp_listener.py

import socket
import json
from PyQt6.QtCore import QThread, pyqtSignal

class UDPListener(QThread):
    """
    Escuta a rede numa thread separada.
    Emite um sinal (data_received) com os dados recebidos.
    """
    # Sinal que irá "disparar" quando um dado novo chegar.
    # Ele vai carregar um dicionário (dict) como dados.
    data_received = pyqtSignal(dict)

    def __init__(self, ip, port, parent=None):
        super().__init__(parent)
        self.UDP_IP = ip
        self.UDP_PORT = port
        self.running = True

    def run(self):
        """Esta função é executada automaticamente quando a thread começa (com .start())"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.UDP_IP, self.UDP_PORT))

        print(f"A escutar em {self.UDP_IP}:{self.UDP_PORT}")

        while self.running:
            try:
                # Espera (bloqueia) até receber dados
                data, addr = sock.recvfrom(1024) # buffer size é 1024 bytes

                # Converte os bytes recebidos (ex: b'{...}') para string
                json_string = data.decode('utf-8')

                # Converte a string JSON num dicionário Python
                data_dict = json.loads(json_string)

                # Emite o sinal com os dados (o dicionário)
                self.data_received.emit(data_dict)

            except Exception as e:
                print(f"Erro ao receber dados: {e}")

        sock.close()
        print("Thread UDP terminada.")

    def stop(self):
        """Método para parar a thread de forma limpa"""
        self.running = False