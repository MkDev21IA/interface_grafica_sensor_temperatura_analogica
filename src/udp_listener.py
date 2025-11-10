"""!
@file udp_listener.py
@brief Implementa a thread de escuta (listener) UDP.
@details Este módulo contém a classe UDPListener, que herda de QThread.
         Sua responsabilidade é escutar por pacotes UDP em uma thread separada
         para não bloquear a interface gráfica principal. Ele usa um timeout
         para permitir um encerramento limpo.
"""

import socket
import json
from PyQt6.QtCore import QThread, pyqtSignal

class UDPListener(QThread):
    """!
    @brief Thread que escuta pacotes UDP e emite sinais com os dados.
    @details Esta classe é a principal trabalhadora de rede. Ela faz o 'bind'
             a um IP e porta e entra em um loop, emitindo um sinal
             'data_received' para cada pacote JSON válido que recebe.
    """
    
    data_received = pyqtSignal(dict)
    """!
    @brief Sinal emitido quando um novo pacote de dados (dict) é recebido.
    @details A MainWindow (ou qualquer outra classe) pode se conectar a este sinal
             para ser notificada quando novos dados chegarem.
    """

    def __init__(self, ip, port, parent=None):
        """!
        @brief Construtor da classe UDPListener.
        
        @param ip (str): O endereço IP para fazer o 'bind' (ex: '0.0.0.0').
        @param port (int): A porta UDP para escutar.
        @param parent (QObject): O objeto pai do Qt (opcional).
        """
        super().__init__(parent)
        self.UDP_IP = ip
        self.UDP_PORT = port
        self.running = True

    def run(self):
        """!
        @brief O "coração" da thread, executado quando .start() é chamado.
        @details Configura o socket, entra no loop 'while self.running', e escuta por pacotes.
                 O 'sock.settimeout(1.0)' é crucial para permitir que a thread feche
                 de forma limpa, pois o loop verifica 'self.running' a cada segundo,
                 mesmo se não houver dados (graças ao 'except socket.timeout').
        """
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
        """!
        @brief Pára a thread de forma limpa.
        @details Define a flag 'self.running' como False, o que faz com que
                 o loop em run() termine na próxima iteração (após o timeout).
        """
        self.running = False