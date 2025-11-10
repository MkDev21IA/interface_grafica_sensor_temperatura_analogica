"""!
@file main_window.py
@brief Implementação da janela principal (Dashboard) da interface gráfica.
@details Esta classe é o coração da UI. Ela usa PyQt6 e pyqtgraph
         para criar um dashboard que exibe dados de sensores em tempo real,
         incluindo valor atual, gráfico histórico, alertas e opções de log.
"""

# Importando bibliotecas necessárias
import configparser
import csv
import os
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QPushButton, QFileDialog, QMessageBox, QDoubleSpinBox,
    QCheckBox, QFrame, QFormLayout
)
from PyQt6.QtCore import Qt, QDateTime 
from PyQt6.QtGui import QFont, QColor
import pyqtgraph as pg
from collections import deque

from src.udp_listener import UDPListener

# --- Constantes de Alerta (Valores Padrão) ---
DEFAULT_TEMP_MIN = 15.0
DEFAULT_TEMP_MAX = 30.0
# ---------------------------------------------

HISTORICO_SEGUNDOS = 60
TAMANHO_TABELA = 10 

LOG_FILENAME = "sensor_log_continuo.csv"
# Cabeçalho do CSV
CSV_HEADER = ['ts', 'group', 'sensor_id', 'value', 'unit']

# --- Cores ---
COR_FUNDO = "#1E1E1E"       
COR_TEXTO = "#D4D4D4"       
COR_DESTAQUE_NORMAL = "#00A896" 
COR_DESTAQUE_ALERTA = "#E53D00" 
COR_GRAFICO = "#00A896"
COR_GRID = "#555555"
COR_FUNDO_PAINEL = "#2A2A2A" 

TAMANHO_FONTE_VALOR = 120

class MainWindow(QMainWindow):
    """!
    @brief Classe principal da interface gráfica.
    @details Herda de QMainWindow e compõe todos os widgets da UI,
             inicia o listener UDP e atualiza a interface com os dados recebidos.
    """
    def __init__(self):
        """!
        @brief Construtor da MainWindow.
        @details Inicializa a UI, lê o ficheiro de configuração, aplica estilos,
                 cria os layouts, inicializa os buffers de dados e inicia o listener UDP.
        """
        super().__init__()

        # --- 1. Ler Configuração ---
        config = configparser.ConfigParser()
        config.read('config.ini')
        udp_ip = config['Network']['UDP_IP']
        udp_port = int(config['Network']['UDP_PORT'])

        # --- 2. Configurações da Janela ---
        self.setWindowTitle("Monitor de Sensor (Grupo 6) - v5.3")
        self.setGeometry(100, 100, 1100, 700) 

        # --- 3. Aplicar Estilo/Cores (Modo Escuro) ---
        self.aplicar_estilo_escuro()

        # --- 4. Buffers de Dados e Flags ---
        """!
        @brief Buffers de dados para o gráfico/tabela e flags de controlo.
        """
        self.data_buffer_grafico = deque(maxlen=HISTORICO_SEGUNDOS)
        self.data_buffer_tabela = deque(maxlen=TAMANHO_TABELA) 
        self.is_logging_auto = False 
        self.limite_min = DEFAULT_TEMP_MIN
        self.limite_max = DEFAULT_TEMP_MAX

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

# -- Funções de Estilo e Criação de Componentes ---
    def aplicar_estilo_escuro(self):
        """!
        @brief Aplica a folha de estilo (CSS/QSS) de modo escuro à aplicação.
        @details Define as cores de fundo, texto, botões e outros widgets
                 usando as constantes de cor globais.
        """
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COR_FUNDO}; }}
            QLabel {{ color: {COR_TEXTO}; font-size: 14px; }}
            QTableWidget {{
                background-color: {COR_FUNDO_PAINEL};
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
                background-color: {COR_FUNDO_PAINEL};
                border-radius: 5px;
            }}
            QPushButton {{
                background-color: {COR_DESTAQUE_NORMAL};
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }}
            QPushButton:hover {{ background-color: #007A6B; }}
            QCheckBox {{
                color: {COR_TEXTO};
                font-size: 14px;
                padding: 5px;
            }}
            QCheckBox::indicator {{ width: 15px; height: 15px; }}
            
            QDoubleSpinBox {{
                background-color: {COR_FUNDO_PAINEL};
                color: {COR_TEXTO};
                font-size: 14px;
            }}
            
            QFrame[objectName="config_panel"] {{
                background-color: {COR_FUNDO_PAINEL};
                border-radius: 5px;
            }}
        """)

    def criar_painel_destaque(self):
        """!
        @brief Cria o painel da esquerda (Destaque).
        @details Constrói o layout vertical que contém o valor atual (grande),
                 o status do alerta e o timestamp da última atualização.
        @return (QVBoxLayout): O layout do painel de destaque pronto a ser adicionado.
        """
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

        self.label_ultima_atualizacao = QLabel("Última Atualização: --:--:--")
        self.label_ultima_atualizacao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_ultima_atualizacao.setStyleSheet(f"color: {COR_TEXTO}; font-size: 16px;")

        layout.addWidget(self.label_sensor_id)
        layout.addWidget(self.label_valor_atual)
        layout.addWidget(self.label_status)
        layout.addWidget(self.label_ultima_atualizacao)
        
        return layout

    def criar_painel_detalhes(self):
        """!
        @brief Cria o painel da direita (Detalhes e Controlo).
        @details Constrói o layout que contém o painel de configuração (limites, log auto),
                 o gráfico histórico e a tabela de leituras recentes.
        @return (QVBoxLayout): O layout do painel de detalhes pronto a ser adicionado.
        """
        layout_principal_detalhes = QVBoxLayout()

        config_frame = QFrame()
        config_frame.setObjectName("config_panel")
        config_layout = QFormLayout(config_frame) 
        config_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.spin_min = QDoubleSpinBox()
        self.spin_min.setRange(-100, 200)
        self.spin_min.setValue(DEFAULT_TEMP_MIN)
        self.spin_min.valueChanged.connect(self.limite_dinamico_mudou)
        
        self.spin_max = QDoubleSpinBox()
        self.spin_max.setRange(-100, 200)
        self.spin_max.setValue(DEFAULT_TEMP_MAX)
        self.spin_max.valueChanged.connect(self.limite_dinamico_mudou)
        
        config_layout.addRow("Limite Mín. Alerta:", self.spin_min)
        config_layout.addRow("Limite Máx. Alerta:", self.spin_max)
        
        self.log_auto_checkbox = QCheckBox(f"Log Automático ({LOG_FILENAME})")
        self.log_auto_checkbox.toggled.connect(self.on_auto_logging_toggled)
        config_layout.addRow(self.log_auto_checkbox)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Histórico (Últimos 60s)")
        self.plot_curve = self.plot_widget.plot(
            pen=pg.mkPen(COR_GRAFICO, width=2)
        )
        
        self.tabela_historico = QTableWidget()
        self.tabela_historico.setRowCount(TAMANHO_TABELA)
        self.tabela_historico.setColumnCount(2)
        self.tabela_historico.setHorizontalHeaderLabels(["Timestamp", "Valor"])
        self.tabela_historico.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        
        self.save_log_button = QPushButton("Salvar Histórico (60s) em CSV")
        self.save_log_button.clicked.connect(self.save_log_file_manual)
        
        layout_principal_detalhes.addWidget(config_frame)
        layout_principal_detalhes.addWidget(self.plot_widget, 60)
        layout_principal_detalhes.addWidget(self.tabela_historico, 30)
        layout_principal_detalhes.addWidget(self.save_log_button, 5) 
        
        return layout_principal_detalhes

    # --- Funções de Callback (Slots) ---

    def limite_dinamico_mudou(self):
        """!
        @brief Slot: Chamado quando o valor do QDoubleSpinBox (limites) é alterado.
        @details Atualiza as variáveis `self.limite_min` e `self.limite_max`
                 com os novos valores da UI.
        """
        self.limite_min = self.spin_min.value()
        self.limite_max = self.spin_max.value()
        print(f"Novos limites de alerta: Mín={self.limite_min}, Máx={self.limite_max}")
        if self.limite_min >= self.limite_max:
            self.spin_max.setValue(self.limite_min + 1)

    def save_log_file_manual(self):
        """!
        @brief Slot: Chamado quando o botão "Salvar Histórico" é clicado.
        @details Abre um diálogo 'Salvar Como...' (QFileDialog) e salva os
                 dados atuais do buffer do gráfico (`data_buffer_grafico`)
                 num ficheiro CSV.
        """
        print("Iniciando salvamento manual de log...")
        data_snapshot = list(self.data_buffer_grafico)
        
        if not data_snapshot:
            QMessageBox.warning(self, "Sem Dados", "Não há dados no histórico para salvar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Log do Sensor (60s)", "log_sensor_60s.csv", "CSV Files (*.csv)"
        )
        
        if caminho:
            try:
                with open(caminho, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['leitura_index', 'valor_temperatura'])
                    for i, valor in enumerate(data_snapshot):
                        writer.writerow([i, valor])
                QMessageBox.information(self, "Sucesso", f"Log salvo com sucesso em:\n{caminho}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível salvar o ficheiro:\n{e}")

    # --- Funções de Log Automático ---
    
    def on_auto_logging_toggled(self, is_checked):
        """!
        @brief Slot: Chamado quando o checkbox "Log Automático" é (des)marcado.
        @param is_checked (bool): O novo estado do checkbox (True se marcado).
        """
        self.is_logging_auto = is_checked
        if self.is_logging_auto:
            print(f"Log automático iniciado: {LOG_FILENAME}")
            self.check_and_write_header()
        else:
            print("Log automático parado.")

    def check_and_write_header(self):
        """!
        @brief Verifica se o ficheiro de log automático (`LOG_FILENAME`) existe.
        @details Se o ficheiro não existir, cria-o e escreve a linha de
                 cabeçalho (CSV_HEADER).
        """
        if not os.path.exists(LOG_FILENAME):
            try:
                with open(LOG_FILENAME, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(CSV_HEADER)
            except Exception as e:
                print(f"Erro ao criar cabeçalho do log: {e}")
                self.log_auto_checkbox.setChecked(False) 

    def append_log_data_auto(self, data_dict):
        """!
        @brief Anexa uma linha de dados ao ficheiro de log automático.
        @param data_dict (dict): O dicionário de dados JSON recebido do sensor.
        """
        try:
            # [MUDANÇA] Usa as novas chaves 'ts' e 'group'
            row = [
                data_dict.get('ts', ''), # Pega a string ISO
                data_dict.get('group', 'N/A'),
                data_dict.get('sensor_id', 'N/A'),
                data_dict.get('value', 0.0),
                data_dict.get('unit', '')
            ]
            with open(LOG_FILENAME, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        except Exception as e:
            print(f"Erro ao salvar linha no log automático: {e}")
            self.log_auto_checkbox.setChecked(False)
    
    # -----------------------------------

    def update_data(self, data_dict):
        """!
        @brief Slot: O "coração" da UI. Chamado quando o listener UDP emite novos dados.
        @details Processa o dicionário de dados, atualiza todos os QLabels,
                 verifica os alertas, adiciona dados ao gráfico e à tabela,
                 e chama o log automático (se ativo).
        @param data_dict (dict): O dicionário de dados JSON recebido do sensor.
        """
        try:
            # --- [MUDANÇA] 1. Extrai dados com as novas chaves ---
            sensor = data_dict.get('sensor_id', 'N/A')
            valor = data_dict.get('value', 0.0)
            unidade = data_dict.get('unit', '')
            # Pega a string ISO
            timestamp_iso_str = data_dict.get('ts', '') 

            # --- [MUDANÇA] 2. Converte a string ISO para QDateTime ---
            # O Qt.DateFormat.ISODate sabe lidar com o formato "Z" (UTC)
            qdt = QDateTime.fromString(timestamp_iso_str, Qt.DateFormat.ISODate)
            if not qdt.isValid():
                # Tenta de novo se tiver milissegundos
                qdt = QDateTime.fromString(timestamp_iso_str, Qt.DateFormat.ISODateWithMs)

            # Formata para 'hh:mm:ss'
            timestamp_str = qdt.toString("hh:mm:ss")
            # ----------------------------------------------------

            # --- 2. Atualiza Painel Destaque (Esquerda) ---
            self.label_sensor_id.setText(f"Sensor: {sensor}")
            self.label_valor_atual.setText(f"{valor:.1f} {unidade}")
            self.label_ultima_atualizacao.setText(f"Última Atualização: {timestamp_str}")

            # --- 3. Lógica de Alerta Visual (com limites dinâmicos) ---
            base_style = f"""
                font-size: {TAMANHO_FONTE_VALOR}px;
                font-weight: bold;
            """
            
            if valor < self.limite_min or valor > self.limite_max:
                self.label_valor_atual.setStyleSheet(base_style + f"color: {COR_DESTAQUE_ALERTA};")
                self.label_status.setText(f"ALERTA: Valor fora dos limites ({self.limite_min}-{self.limite_max})")
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
                
                item_ts = QTableWidgetItem(ts)
                item_val = QTableWidgetItem(val)
                item_ts.setForeground(QColor(COR_TEXTO))
                item_val.setForeground(QColor(COR_TEXTO))
                
                self.tabela_historico.setItem(i, 0, item_ts)
                self.tabela_historico.setItem(i, 1, item_val)
            
            # --- 5. Salva no Log Automático ---
            if self.is_logging_auto:
                # Passa o 'data_dict' original para o log
                self.append_log_data_auto(data_dict)
                
        except Exception as e:
            self.label_valor_atual.setText("Erro!")
            self.label_status.setText(f"Erro: {e}")

    # --- Evento de Fecho da Janela ---
    def closeEvent(self, event):
        """!
        @brief Event Handler: Chamado quando o usuário fecha a janela (clica no 'X').
        @details Garante que a thread do listener UDP (`self.listener`)
                 seja parada de forma limpa antes que a aplicação feche.
        @param event (QCloseEvent): O evento de fecho da janela.
        """
        print("A fechar a aplicação...")
        self.listener.stop()
        self.listener.wait()
        event.accept()