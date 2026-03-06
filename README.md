<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=soft&color=0:3b82f6,100:1a1a2e&height=250&section=header&text=Renan%20Evilásio&fontSize=70&fontAlignY=35&animation=fadeIn&fontColor=fff&desc=Desenvolvedor%20ERP%20|%20Delphi%20|%20Python%20|%20Laravel&descAlignY=60&descSize=20&descColor=a0c4ff" />
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/renan-evil%C3%A1sio-43b357247">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
  </a>
  <a href="https://github.com/RenanESO">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" />
  </a>
  <img src="https://img.shields.io/badge/status-disponível-brightgreen?style=for-the-badge" />
</p>

# 🧠 FotoPlus - Módulo de Inteligência Artificial (TCC)

Este projeto contém o núcleo de processamento de imagens e reconhecimento facial do sistema **FotoPlus**. Desenvolvido em **Python**, ele atua como um serviço de backend para a aplicação web principal (Laravel), responsável por detectar faces, reconhecer pessoas, organizar fotos e identificar duplicatas no Google Drive.

> **Nota:** Este projeto trabalha em conjunto com o repositório principal: [Trabalho_TCC_v3 FotoPlus](https://github.com/RenanESO/Trabalho_TCC_v3).

---

## 🚀 Tecnologias Utilizadas

- **Linguagem:** Python 3.8+
- **Visão Computacional & IA:**
  - `dlib`: Detecção de faces (HOG/CNN) e extração de pontos faciais (landmarks).
  - `face_recognition`: Reconhecimento facial de alta precisão.
  - `opencv-python` (cv2): Processamento e manipulação de imagens.
  - `numpy`: Operações matemáticas e manipulação de arrays (descritores faciais).
- **Integração:**
  - `google-api-python-client`: Integração com Google Drive API.
  - `python-dotenv`: Gerenciamento de variáveis de ambiente.
  - `mysql-connector-python`: Conexão com banco de dados MySQL.
  - `requests`: Requisições HTTP.
  - `Pillow` (PIL): Manipulação de imagens.

---

## ⚙️ Pré-requisitos

Para rodar este projeto, você precisará de:

1.  **Python 3.8 ou superior** instalado.
2.  **Compiladores C++** (Necessário para compilar o `dlib`):
    - **Windows:** Visual Studio Build Tools (com "Desktop development with C++").
    - **Linux:** `build-essential`, `cmake`.
3.  **Dependências do Sistema** (Linux):
    ```bash
    sudo apt-get install cmake libgtk-3-dev libboost-all-dev
    ```

---

## 🔧 Instalação e Configuração

### 1. Clonar o Repositório
```bash
git clone <URL_DO_REPOSITORIO>
cd Trabalho_TCC_Python_v3
```

### 2. Criar Ambiente Virtual (Recomendado)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Renomeie o arquivo `env-exemplo` para `.env` e configure as credenciais necessárias (Google API, Banco de Dados, etc.):
```bash
cp env-exemplo .env
```
> **Importante:** Configure as credenciais do Google Drive (`CLIENT_ID`, `CLIENT_SECRET`, etc.) para permitir o acesso aos arquivos.

### 5. Configurar Caminhos dos Modelos (Atenção ⚠️)
Os scripts `treinamento.py` e `organiza.py` apontam para os arquivos de modelo do `dlib` (`.dat`). Verifique e ajuste a variável `caminhoBase` nesses arquivos para apontar para a pasta `dataset/` correta no seu ambiente:

```python
# Exemplo em treinamento.py e organiza.py
caminhoBase = 'caminho/absoluto/para/Trabalho_TCC_Python_v3/dataset/'
```
Os arquivos de modelo necessários na pasta `dataset/` são:
- `mmod_human_face_detector.dat`
- `shape_predictor_68_face_landmarks.dat`
- `dlib_face_recognition_resnet_model_v1.dat`

---

## 💻 Como Executar

O script principal é o `principal.py`. Ele é projetado para ser chamado pela aplicação Laravel via linha de comando (ou executável), mas pode ser testado manualmente.

### Sintaxe Geral
```bash
python principal.py <ROTINA> <CAMINHO_PUBLICO> <USER_ID> [ARGUMENTOS_EXTRAS...]
```

### Rotinas Disponíveis

#### 1. Treinamento (`treinamento`)
Realiza o treinamento do reconhecimento facial para uma pessoa específica.
```bash
python principal.py treinamento "C:\Caminho\Storage" "ID_USUARIO" "CAMINHO_FOTO_TREINO" "ID_PESSOA"
```
- **Argumentos:**
  - `CAMINHO_FOTO_TREINO`: Caminho da imagem contendo o rosto da pessoa.
  - `ID_PESSOA`: Identificador único da pessoa sendo treinada.

#### 2. Organização (`organiza`)
Busca fotos no Google Drive, reconhece faces e organiza em pastas.
```bash
python principal.py organiza "C:\Caminho\Storage" "ID_USUARIO" "ID_PASTA_DRIVE" "DATA_INICIO" "DATA_FIM" "ACAO" "RESOLUCAO" "ID_PESSOA_FILTRO"
```
- **Argumentos:**
  - `ID_PASTA_DRIVE`: ID da pasta no Google Drive.
  - `DATA_INICIO` / `DATA_FIM`: (Opcional) Filtro de data (YYYY-MM-DD).
  - `ACAO`: `copiar` ou `recortar`.
  - `RESOLUCAO`: (Opcional) Aumentar resolução (int).
  - `ID_PESSOA_FILTRO`: (Opcional) Filtrar por uma pessoa específica.

#### 3. Duplicidade (`duplicidade`)
Detecta fotos duplicadas visualmente.
```bash
python principal.py duplicidade "C:\Caminho\Storage" "ID_USUARIO" "ID_PASTA_DRIVE" "DATA_INICIO" "DATA_FIM" "ACAO"
```

---

## 📦 Compilação (Gerar Executável)

A aplicação Laravel espera um executável (`principal.exe` no Windows ou binário no Linux) para executar as rotinas sem depender do ambiente Python do servidor web.

Para gerar o executável, utilize o **PyInstaller**:

1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Gere o executável (modo arquivo único):
   ```bash
   pyinstaller --onefile principal.py
   ```

3. O arquivo gerado estará na pasta `dist/`. Mova este arquivo para a pasta esperada pelo Laravel (ex: `FotoPlus/storage/app/public/deteccao/dist/`).

---

## 📂 Estrutura de Arquivos

- `principal.py`: Ponto de entrada (Entry point). Gerencia qual rotina executar.
- `uteis.py`: Funções auxiliares, logs e validação de parâmetros.
- `treinamento.py`: Lógica de detecção facial e geração de encodings (treino).
- `organiza.py`: Lógica de varredura do Drive, reconhecimento e organização.
- `duplicidade.py`: Algoritmo para detectar imagens visualmente semelhantes/iguais.
- `googleServico.py`: Wrapper para autenticação e chamadas à API do Google Drive.
- `dataset/`: Modelos pré-treinados do Dlib.
