# 📊 Monitor de Sensor UDP (Grupo 6)

Interface gráfica em Python (PyQt6) destinada a receber, processar e exibir dados de um sensor (STM32) enviados via protocolo UDP.

Este projeto recebe pacotes JSON do dispositivo embarcado e atualiza a interface em tempo real.

## Status do Projeto

Em desenvolvimento. A interface é capaz de:
* Escutar uma porta UDP específica (configurável).
* Receber pacotes JSON enviados pelo C++ (STM32).
* Processar o JSON e extrair os dados (`value`, `unit`, `sensor_id`).
* Atualizar a GUI em tempo real com o valor do sensor.
* Executar o "ouvido" UDP numa thread separada para não congelar a interface.

---

## 🚀 Como Executar

### Pré-requisitos
* Python 3.10+
* O dispositivo embarcado (STM32) que envia os dados na mesma rede.

### 1. Configurar o Ambiente

Primeiro, clone o repositório e crie um ambiente virtual:

```bash
# Clone o repositório (exemplo)
git clone URL_DO_SEU_REPO_AQUI
cd nome-do-repositorio

# Crie e ative o ambiente virtual
python -m venv .venv

# No Windows (PowerShell):
.\.venv\Scripts\Activate-ps1

# No Mac/Linux:
source .venv/bin/activate
```

### 2. Instalar Dependências

Instale as bibliotecas necessárias (PyQt6):

```bash
pip install -r requirements.txt
```

### 3. Configurar a Rede

Edite o ficheiro `config.ini` para definir onde a aplicação deve escutar.

```ini
[Network]
# 0.0.0.0 (recomendado) ou o IP específico deste PC
UDP_IP = 0.0.0.0
# A porta deve ser a mesma do C++ (STM32)
UDP_PORT = 5000
```

**Importante:** O C++ no STM32 deve estar configurado para enviar os dados para o IP *deste PC* (ex: `192.168.1.10`) e para a porta `5000`.

### 4. Executar

Com o ambiente ativo, execute o `main.py`:

```bash
python main.py
```
