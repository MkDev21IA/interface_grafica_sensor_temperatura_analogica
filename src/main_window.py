# src/main_window.py

import configparser # Para ler o .ini
from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from src.udp_listener import UDPListener # <-- 1. Importa o "ouvido"

class MainWindow(QMainWindow):
    """
    Classe da Janela Principal da aplicação.
    """
    def __init__(self):
        super().__init__()

        # --- 1. Ler o ficheiro de configuração ---
        config = configparser.ConfigParser()
        config.read('config.ini')
        udp_ip = config['Network']['UDP_IP']
        udp_port = int(config['Network']['UDP_PORT'])

        # --- 2. Configurações da Janela ---
        self.setWindowTitle("Monitor de Temperatura (Grupo 6)")
        self.setGeometry(100, 100, 400, 250) # Aumentei um pouco a altura

        # --- 3. Layout e Widgets (Componentes) ---
        
        # Vamos usar um layout vertical para organizar os widgets
        layout = QVBoxLayout()

        self.label_info = QLabel(f"A escutar em: {udp_ip}:{udp_port}")
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status = QLabel("Aguardando dados do sensor...")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Aumenta a fonte do texto de status
        font = self.label_status.font()
        font.setPointSize(20)
        self.label_status.setFont(font)

        # Adiciona os labels ao layout
        layout.addWidget(self.label_info)
        layout.addWidget(self.label_status)

        # Cria um "widget central" para aplicar o layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # --- 4. Iniciar o "Ouvido" (UDP Listener) ---
        self.listener = UDPListener(udp_ip, udp_port)
        
        # Conecta o sinal 'data_received' do listener à nossa função 'update_status'
        self.listener.data_received.connect(self.update_status)
        
        # Inicia a thread (chama a função 'run' do listener)
        self.listener.start()

    def update_status(self, data_dict):
        """
        Esta função (slot) é chamada AUTOMATICAMENTE quando
        o listener emite o sinal 'data_received'.
        'data_dict' é o dicionário que o listener enviou.
        """
        try:
            # Extrai os dados do dicionário (como definido no C++)
            valor = data_dict['value']
            unidade = data_dict['unit']
            sensor_id = data_dict['sensor_id']

            # Formata o valor com 2 casas decimais
            texto_formatado = f"{valor:.2f} {unidade}"
            
            # Atualiza o texto do label na tela
            self.label_status.setText(texto_formatado)
            
            # (Opcional) Mostra qual sensor enviou
            self.label_info.setText(f"Sensor: {sensor_id}")

        except KeyError:
            # Caso o JSON venha sem uma das chaves (ex: 'value')
            self.label_status.setText("Erro: Dados mal formatados")
        except Exception as e:
            self.label_status.setText(f"Erro: {e}")

    def closeEvent(self, event):
        """Função chamada quando a janela é fechada (clicando no 'X')"""
        print("A fechar a aplicação...")
        self.listener.stop() # Pede à thread para parar o loop
        self.listener.wait() # Espera a thread terminar de forma limpa
        event.accept() # Confirma o fecho da janela