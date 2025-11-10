"""!
@file main.py
@brief Ponto de entrada principal da aplicação (Dashboard do Sensor).
@details Este script inicializa a QApplication do PyQt6,
         cria a instância da MainWindow (a interface gráfica principal)
         e inicia o loop de eventos da aplicação.
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow 

if __name__ == "__main__":
    """!
    @brief Função principal que executa a aplicação.
    
    Cria a aplicação, instancia a janela principal (MainWindow),
    exibe-a e entra no loop de execução do Qt.
    """
    
    # 1. Cria a "aplicação"
    app = QApplication(sys.argv)

    # 2. Cria a nossa janela principal
    window = MainWindow()

    # 3. Mostra a janela
    window.show()

    # 4. Inicia o loop da aplicação
    # (Faz o programa esperar por cliques, etc., e não fechar)
    sys.exit(app.exec())