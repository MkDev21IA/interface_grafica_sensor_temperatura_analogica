# 📊 Monitor de Sensor UDP (Grupo 6)

Interface gráfica em **Python (PyQt6)** destinada a receber, processar e exibir dados de um sensor (**STM32**) enviados via protocolo **UDP**.

Este projeto recebe pacotes **JSON** do dispositivo embarcado e atualiza a interface em tempo real, implementando todos os requisitos obrigatórios do projeto.

---

## 📸 Visão Geral da Interface

A interface principal é um **dashboard em modo escuro**, dividido em duas secções:

- **Painel de Destaque (Esquerda):** Focado no valor atual para monitoramento rápido e alertas visuais.  
- **Painel de Detalhes (Direita):** Fornece o contexto histórico com um gráfico em tempo real e uma tabela das últimas leituras.

> **[IMAGEM 1]**: A interface gráfica principal (dashboard) em funcionamento, mostrando a temperatura normal (cor verde/ciano).

---

## ✨ Funcionalidades

Este monitor cumpre todos os requisitos obrigatórios do projeto:

- **Monitoramento em Tempo Real:** Exibe o valor atual do sensor com uma fonte grande e clara.  
- **Alerta Visual:** O valor da temperatura muda de cor (para vermelho/laranja) se ultrapassar os limites pré-definidos (`TEMP_MIN_NORMAL` e `TEMP_MAX_NORMAL`).  
- **Histórico Gráfico:** Um gráfico (**pyqtgraph**) exibe os últimos 60 segundos de dados, permitindo a visualização de tendências.  
- **Tabela de Histórico:** Uma tabela exibe as 10 leituras mais recentes com o seu timestamp exato.  
- **Salvar Log em CSV:** Um botão permite ao usuário salvar os dados dos últimos 60 segundos (do gráfico) num ficheiro `.csv` em qualquer local do computador.  
- **Design Robusto:** A interface utiliza **multithreading** para que a rede não congele a UI e inclui **socket timeouts** para evitar travamentos caso o sensor seja desconectado.

> **[IMAGEM 2]**: A interface em estado de "Alerta", com a temperatura em vermelho e a mensagem de status atualizada.

---

## 🚀 Como Executar

### Pré-requisitos

- **Python 3.10+**  
- O dispositivo embarcado (**STM32**) a enviar dados na mesma rede.

---

### 1. Configurar o Ambiente

Primeiro, clone o repositório e crie um ambiente virtual:

```bash
# Clone o repositório
git clone https://github.com/MkDev21IA/interface_grafica_sensor_temperatura_analogica.git
cd interface_grafica_sensor_temperatura_analogica

# Crie e ative o ambiente virtual
python -m venv .venv

# No Windows (PowerShell):
.\.venv\Scripts\Activate-ps1

# No Mac/Linux:
source .venv/bin/activate
```

---

### 2. Instalar Dependências

Instale todas as bibliotecas necessárias (**PyQt6** e **Pyqtgraph**):

```bash
pip install -r requirements.txt
```

---

### 3. Configurar a Rede

Edite o ficheiro `config.ini` para definir onde a aplicação deve escutar:

```ini
[Network]
# 0.0.0.0 (recomendado) ou o IP específico deste PC
UDP_IP = 0.0.0.0
# A porta deve ser a mesma do C++ (STM32)
UDP_PORT = 5000
```

> **Importante:** O C++ no STM32 deve estar configurado para enviar os dados para o IP **deste PC** (ex: `192.168.1.10`) e para a porta **5000**.

---

### 4. Executar

Com o ambiente ativo, execute o `main.py`:

```bash
python main.py
```

---

### 5. Salvar o Log

Quando tiver dados suficientes no gráfico, clique no botão **"Salvar Histórico (60s) em CSV"**.  
Uma janela “Salvar Como...” aparecerá para você escolher onde salvar o ficheiro.

> **[IMAGEM 3]**: A janela de diálogo “Salvar Como...” (**QFileDialog**) aberta sobre a interface principal, mostrando a opção de salvar o `.csv`.

---
