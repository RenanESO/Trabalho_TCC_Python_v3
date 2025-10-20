import sys
import os
import shutil
from datetime import datetime

# Lista global para armazenar logs temporários que serão gravados posteriormente
logs = []

# Argumentos passados pela linha de comando
args = sys.argv[1:]
opcaoRotina = args[0] if len(args) > 0 else None
caminhoPastaPublic = args[1] if len(args) > 1 else None
usuarioId = args[2] if len(args) > 2 else None

# Definindo caminhos padrão com base no usuário e na pasta pública
caminhoPastaUsuario = f'{caminhoPastaPublic}/{usuarioId}'
caminhoPastaTemp = f'{caminhoPastaUsuario}/resultado'
caminhoArquivoLog = f'{caminhoPastaUsuario}/log.txt'
caminhoArquivoPickle = f'{caminhoPastaUsuario}/indicesTreinamento.pickle'
caminhoArquivoNpy = f'{caminhoPastaUsuario}/fotosTreinamento.npy'

# ------------------------------------------------ validarParametro -------------------------------------------------- #
def validarParametro(index, tipo, optional=False, default=None):
    """
    Valida e converte o parâmetro de um tipo específico, conforme indicado.

    Args:
        index (int): Índice do parâmetro a ser validado.
        tipo (type): Tipo para o qual o valor será convertido.
        optional (bool): Indica se o parâmetro é opcional.
        default (any): Valor padrão para parâmetros opcionais.

    Returns:
        any: Valor do parâmetro convertido para o tipo especificado.

    Raises:
        ValueError: Se o parâmetro não estiver presente ou não puder ser convertido.
    """
    try:
        valor = args[index]
        if valor == 'None':
            if optional:
                return default
            raise ValueError(f'Parâmetro {index} não pode ser None.')
        return tipo(valor)  # Tenta converter para o tipo especificado

    except (IndexError, ValueError) as e:
        raise ValueError(f'Erro ao validar o parâmetro {index}: {e}')

# --------------------------------------------------- AdicionarLog --------------------------------------------------- #
def adicionarLog(msgLog):
    """
    Adiciona uma mensagem à lista de logs com a data e hora atuais.

    Args:
        msgLog (str): Mensagem a ser adicionada ao log.
    """
    dataHoraAtuais = datetime.now().strftime('%d/%m/%Y %H:%M')
    print(f'{dataHoraAtuais} {msgLog}')
    logs.append(f'{dataHoraAtuais} {msgLog}')

# ------------------------------------------------- apagarArquivoLog ------------------------------------------------- #
def apagarArquivoLog():
    """
    Apaga o arquivo de log existente, se houver.
    """
    if os.path.exists(caminhoArquivoLog):
        os.remove(caminhoArquivoLog)

# ------------------------------------------------- gravarArquivoLog ------------------------------------------------- #
def gravarArquivoLog():
    """
    Grava o conteúdo da lista de logs no arquivo de log e, em seguida, limpa a lista de logs.
    """
    if logs and caminhoArquivoLog:
        with open(caminhoArquivoLog, 'a+') as arquivo:
            arquivo.write('\n'.join(logs) + '\n')
        logs.clear()

# --------------------------------------------- moverImagemPastaResultado -------------------------------------------- #
def moverImagemPastaResultado(caminhoImagem, caminhoResultado, filtroDataInicio, filtroDataFinal,
                              filtroRecortarCopiarArquivo):
    """
    Move ou copia uma imagem para uma pasta de destino, organizando-a em subpastas baseadas na data de modificação.

    Args:
        caminhoImagem (str): Caminho completo da imagem a ser movida.
        caminhoResultado (str): Pasta de destino para a imagem.
        filtroDataInicio (datetime or None): Data de início do filtro.
        filtroDataFinal (datetime or None): Data de fim do filtro.
        filtroRecortarCopiarArquivo (int): Flag indicando se deve recortar (1) ou copiar (0).

    Returns:
        bool: Indica se a movimentação foi bem-sucedida.
    """
    try:
        adicionarLog(f' ---> Iniciando a movimentação da imagem {caminhoImagem} para a pasta {caminhoResultado}')

        # Obtém a data de modificação do arquivo
        data_modificacao = datetime.fromtimestamp(os.path.getmtime(caminhoImagem))

        # Define o caminho de destino com base em ano e mês
        ano = str(data_modificacao.year)
        mes = str(data_modificacao.month).zfill(2)
        caminhoDestinoData = os.path.join(caminhoResultado, ano, mes)
        os.makedirs(caminhoDestinoData, exist_ok=True)

        # Mover ou copiar o arquivo conforme o filtro especificado
        caminhoDestinoArquivo = os.path.join(caminhoDestinoData, os.path.basename(caminhoImagem))
        if filtroRecortarCopiarArquivo == 0:
            shutil.copy(caminhoImagem, caminhoDestinoArquivo)
        elif filtroRecortarCopiarArquivo == 1:
            shutil.move(caminhoImagem, caminhoDestinoArquivo)

        adicionarLog(f' <--- Finalizando a movimentação da imagem {caminhoImagem} para {caminhoResultado} \n')
        return True

    except Exception as e:
        encontrouError(f'Erro ao mover a imagem: {caminhoImagem}. Erro: {str(e)}')
        return False

# ----------------------------------------------- resetarPastaResultado ---------------------------------------------- #
def resetarPastaResultado(caminhoResultado):
    """
    Remove e recria a pasta de resultados.

    Args:
        caminhoResultado (str): Caminho da pasta a ser resetada.
    """
    try:
        adicionarLog(f' ---> Resetando a pasta: {caminhoResultado}')

        if os.path.isdir(caminhoResultado):
            shutil.rmtree(caminhoResultado)
        os.mkdir(caminhoResultado)

        adicionarLog(f' <--- Pasta resetada com sucesso: {caminhoResultado} \n')

    except Exception as e:
        encontrouError(f'Erro ao resetar a pasta: {caminhoResultado}. Erro: {str(e)} \n')

# -------------------------------------------------- encontrouError -------------------------------------------------- #
def encontrouError(mensagem):
    """
    Registra um erro no log, grava o log e encerra o programa.

    Args:
        mensagem (str): Mensagem de erro a ser registrada.
    """
    print(mensagem)
    adicionarLog(mensagem)
    gravarArquivoLog()
    sys.exit(1)
