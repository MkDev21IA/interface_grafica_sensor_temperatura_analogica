# src/udp_listener.py

import socket
import json
from PyQt6.QtCore import QThread, pyqtSignal

class UDPListener(QThread):
    """
    Escuta a rede numa thread separada.
    Emite um sinal (data_received) com os dados recebidos.
    """
    data_received = pyqtSignal(dict)

    def __init__(self, ip, port, parent=None):
        super().__init__(parent)
        self.UDP_IP = ip
        self.UDP_PORT = port
        self.running = True

    def run(self):
        """Esta função é executada automaticamente quando a thread começa (com .start())"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # --- [A CORREÇÃO ESTÁ AQUI] ---
        # Define um timeout de 1.0 segundo
        sock.settimeout(1.0)
        # -------------------------------

        try:
            sock.bind((self.UDP_IP, self.UDP_PORT))
            print(f"A escutar em {self.UDP_IP}:{self.UDP_PORT}")
        except Exception as e:
            print(f"ERRO: Não foi possível fazer o bind em {self.UDP_IP}:{self.UDP_PORT}. {e}")
            return # Termina a thread se não conseguir escutar

        while self.running:
            try:
                # Espera (bloqueia) por até 1.0 segundo
                data, addr = sock.recvfrom(1024) 
                
                # Converte os bytes recebidos (ex: b'{...}') para string
                json_string = data.decode('utf-8')
                
                # Converte a string JSON num dicionário Python
                data_dict = json.loads(json_string)
                
                # Emite o sinal com os dados (o dicionário)
                self.data_received.emit(data_dict)
            
            except socket.timeout:
                # Se der timeout (1s se passou sem dados),
                # o loop continua. Isso permite que o 'self.running'
                # seja verificado novamente, permitindo um fecho limpo.
                pass 
            except Exception as e:
                # Ignora outros erros menores de JSON ou rede
                print(f"Erro ao processar pacote: {e}")
        
        sock.close()
        print("Thread UDP terminada.")

    def stop(self):
        """Método para parar a thread de forma limpa"""
        self.running = False