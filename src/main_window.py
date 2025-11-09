# src/main_window.py

import configparser
import csv  # <-- Continua a ser necessário para o CSV
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QPushButton, QFileDialog, QMessageBox # <-- [NOVO]
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from collections import deque

from src.udp_listener import UDPListener

# --- Constantes de Alerta ---
TEMP_MIN_NORMAL = 15.0
TEMP_MAX_NORMAL = 30.0
HISTORICO_SEGUNDOS = 60
TAMANHO_TABELA = 10 

# --- Cores (Estilo "Moderno") ---
COR_FUNDO = "#1E1E1E"       
COR_TEXTO = "#D4D4D4"       
COR_DESTAQUE_NORMAL = "#00A896" 
COR_DESTAQUE_ALERTA = "#E53D00" 
COR_GRAFICO = "#00A896"
COR_GRID = "#555555"

TAMANHO_FONTE_VALOR = 120

class MainWindow(QMainWindow):
    """
    Interface Gráfica para monitoramento de sensor (v4.1 - Botão Salvar Log).
    """
    def __init__(self):
        super().__init__()

        # --- 1. Ler Configuração ---
        config = configparser.ConfigParser()
        config.read('config.ini')
        udp_ip = config['Network']['UDP_IP']
        udp_port = int(config['Network']['UDP_PORT'])

        # --- 2. Configurações da Janela ---
        self.setWindowTitle("Monitor de Sensor (Grupo 6)")
        self.setGeometry(100, 100, 1000, 600) 

        # --- 3. Aplicar Estilo/Cores (Modo Escuro) ---
        self.aplicar_estilo_escuro()

        # --- 4. Buffers de Dados ---
        self.data_buffer_grafico = deque(maxlen=HISTORICO_SEGUNDOS)
        self.data_buffer_tabela = deque(maxlen=TAMANHO_TABELA) 

        # --- 5. Layouts ---
        layout_principal = QHBoxLayout()
        layout_destaque = self.criar_painel_destaque()
        layout_detalhes = self.criar_painel_detalhes()
        layout_principal.addLayout(layout_destaque, 60)
        layout_principal.addLayout(layout_detalhes, 40)
        central_widget = QWidget()
        central_widget.setLayout(layout_principal)
        self.setCentralWidget(central_widget)

        # --- 6. Iniciar o Listener ---
        self.listener = UDPListener(udp_ip, udp_port)
        self.listener.data_received.connect(self.update_data)
        self.listener.start()

    def aplicar_estilo_escuro(self):
        """Aplica um tema escuro à aplicação."""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COR_FUNDO};
            }}
            QLabel {{
                color: {COR_TEXTO};
                font-size: 14px;
            }}
            QTableWidget {{
                background-color: #2A2A2A;
                color: {COR_TEXTO};
                gridline-color: {COR_GRID};
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: #333333;
                color: {COR_DESTAQUE_NORMAL};
                font-weight: bold;
            }}
            pg.PlotWidget {{
                background-color: #2A2A2A;
                border-radius: 5px;
            }}
            /* [NOVO] Estilo do Botão */
            QPushButton {{
                background-color: {COR_DESTAQUE_NORMAL};
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #007A6B; /* Um pouco mais escuro ao passar o mouse */
            }}
        """)

    def criar_painel_destaque(self):
        """Cria o painel da esquerda com a temperatura atual."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        self.label_sensor_id = QLabel("Sensor: ...")
        self.label_sensor_id.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label_valor_atual = QLabel("--- °C")
        self.label_valor_atual.setStyleSheet(f"""
            color: {COR_DESTAQUE_NORMAL};
            font-size: {TAMANHO_FONTE_VALOR}px;
            font-weight: bold;
        """)
        self.label_valor_atual.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status = QLabel("Aguardando dados...")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_status = self.label_status.font()
        font_status.setPointSize(16)
        self.label_status.setFont(font_status)

        layout.addWidget(self.label_sensor_id)
        layout.addWidget(self.label_valor_atual)
        layout.addWidget(self.label_status)
        
        return layout

    def criar_painel_detalhes(self):
        """Cria o painel da direita com gráfico, tabela e controlos."""
        layout = QVBoxLayout()

        # 1. Gráfico
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Histórico (Últimos 60s)")
        self.plot_widget.getAxis('left').setTextPen(COR_TEXTO)
        self.plot_widget.getAxis('bottom').setTextPen(COR_TEXTO)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_curve = self.plot_widget.plot(
            pen=pg.mkPen(COR_GRAFICO, width=2)
        )
        
        # 2. Tabela de Histórico
        self.tabela_historico = QTableWidget()
        self.tabela_historico.setRowCount(TAMANHO_TABELA)
        self.tabela_historico.setColumnCount(2)
        self.tabela_historico.setHorizontalHeaderLabels(["Timestamp", "Valor"])
        self.tabela_historico.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        
        # 3. [NOVO] Botão de Salvar Log
        self.save_log_button = QPushButton("Salvar Histórico (60s) em CSV")
        self.save_log_button.clicked.connect(self.save_log_file)
        
        # Adiciona os widgets ao layout
        layout.addWidget(self.plot_widget, 55) # Gráfico (55%)
        layout.addWidget(self.tabela_historico, 35) # Tabela (35%)
        layout.addWidget(self.save_log_button, 10) # Botão (10%)
        
        return layout

    # --- [NOVO] Função de Salvar Log ---

    def save_log_file(self):
        """
        Chamado quando o botão 'Salvar' é clicado.
        Abre um diálogo 'Salvar Como...' e salva os dados do GRÁFICO (últimos 60s)
        """
        print("Iniciando salvamento de log...")
        
        # Tira uma 'foto' dos dados atuais do gráfico
        data_snapshot = list(self.data_buffer_grafico)
        
        if not data_snapshot:
            QMessageBox.warning(self, "Sem Dados", "Não há dados no histórico para salvar.")
            return

        # Abre o diálogo "Salvar Como..."
        # O 'self' faz o diálogo aparecer sobre a janela principal
        caminho, _ = QFileDialog.getSaveFileName(
            self, 
            "Salvar Log do Sensor", 
            "log_sensor_60s.csv", # Nome padrão
            "CSV Files (*.csv)"   # Filtro
        )
        
        # Se o usuário não cancelou (caminho não é vazio)
        if caminho:
            try:
                with open(caminho, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Escreve o cabeçalho
                    writer.writerow(['leitura_index', 'valor_temperatura'])
                    
                    # Escreve os dados (do mais antigo ao mais novo)
                    for i, valor in enumerate(data_snapshot):
                        writer.writerow([i, valor])
                
                print(f"Log salvo com sucesso em: {caminho}")
                QMessageBox.information(self, "Sucesso", f"Log salvo com sucesso em:\n{caminho}")

            except Exception as e:
                print(f"Erro ao salvar ficheiro: {e}")
                QMessageBox.critical(self, "Erro", f"Não foi possível salvar o ficheiro:\n{e}")

    # -------------------------------

    def update_data(self, data_dict):
        """Slot chamado quando novos dados chegam."""
        try:
            # --- 1. Extrai dados ---
            sensor = data_dict.get('sensor_id', 'N/A')
            valor = data_dict.get('value', 0.0)
            unidade = data_dict.get('unit', '')
            timestamp_unix = data_dict.get('timestamp', 0)
            
            qdt = QDateTime.fromSecsSinceEpoch(timestamp_unix)
            timestamp_str = qdt.toString("hh:mm:ss")

            # --- 2. Atualiza Painel Destaque (Esquerda) ---
            self.label_sensor_id.setText(f"Sensor: {sensor}")
            self.label_valor_atual.setText(f"{valor:.1f} {unidade}")

            # --- 3. Lógica de Alerta Visual ---
            base_style = f"""
                font-size: {TAMANHO_FONTE_VALOR}px;
                font-weight: bold;
            """
            
            if valor < TEMP_MIN_NORMAL or valor > TEMP_MAX_NORMAL:
                self.label_valor_atual.setStyleSheet(base_style + f"color: {COR_DESTAQUE_ALERTA};")
                self.label_status.setText("ALERTA: Valor fora dos limites!")
                self.label_status.setStyleSheet(f"color: {COR_DESTAQUE_ALERTA};")
            else:
                self.label_valor_atual.setStyleSheet(base_style + f"color: {COR_DESTAQUE_NORMAL};")
                self.label_status.setText("Status: Normal")
                self.label_status.setStyleSheet(f"color: {COR_DESTAQUE_NORMAL};")

            # --- 4. Atualiza Painel Detalhes (Direita) ---
            self.data_buffer_grafico.append(valor)
            self.plot_curve.setData(list(self.data_buffer_grafico))
            
            self.data_buffer_tabela.appendleft((timestamp_str, f"{valor:.2f} {unidade}"))
            
            self.tabela_historico.clearContents() 
            for i, (ts, val) in enumerate(self.data_buffer_tabela):
                self.tabela_historico.setItem(i, 0, QTableWidgetItem(ts))
                self.tabela_historico.setItem(i, 1, QTableWidgetItem(val))
            
            # (Removido o log automático)
                
        except Exception as e:
            self.label_valor_atual.setText("Erro!")
            self.label_status.setText(f"Erro: {e}")

    def closeEvent(self, event):
        """Garante que a thread do listener pare ao fechar a janela."""
        print("A fechar a aplicação...")
        self.listener.stop()
        self.listener.wait()
        event.accept()