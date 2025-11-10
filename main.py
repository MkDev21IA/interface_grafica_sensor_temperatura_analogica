# main.py

import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow 

if __name__ == "__main__":
    # 1. Cria a "aplicação"
    app = QApplication(sys.argv)

    # 2. Cria a nossa janela principal
    window = MainWindow()

    # 3. Mostra a janela
    window.show()

    # 4. Inicia o loop da aplicação
    # (Faz o programa esperar por cliques, etc., e não fechar)
    sys.exit(app.exec())