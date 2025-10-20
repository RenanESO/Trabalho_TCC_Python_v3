import uteis
import cv2
import requests
import numpy as np
from PIL import Image
from googleServico import GoogleServico
from io import BytesIO
from typing import List, Dict

class Duplicidade:
    # -------------------------------------------------- construtor -------------------------------------------------- #
    def __init__(self):
        # Inicializa o serviço Google para interações com o Google Drive.
        self.googleDrive = GoogleServico()

        # Definindo atributos para configuração da verificação de duplicidade.
        self.pastaId = None
        self.filtroDataInicio = None
        self.filtroDataFinal = None
        self.filtroRecortarCopiarArquivo = 'copiar'  # Default para "copiar" arquivos duplicados; pode ser configurado para "recortar".

        # Armazena ss imagens duplicadas encontradas.
        self.imagensDuplicadas: List[Dict] = []

    # ---------------------------------------------- configurarDescritor --------------------------------------------- #
    @staticmethod
    def configurarDescritor(descritorKeypoint_I, descritorKeypoint_J):
        # Converte descritores para arrays NumPy para garantir consistência no formato.
        descritorKeypoint_I = [df for df in descritorKeypoint_I]
        descritorKeypoint_J = [df for df in descritorKeypoint_J]

        # Define o tipo dos dados do Array para Float.
        descritorKeypoint_I = np.asarray(descritorKeypoint_I, dtype=np.float64)
        descritorKeypoint_J = np.asarray(descritorKeypoint_J, dtype=np.float64)

        # Ajusta o número de linhas para que ambos os descritores tenham o mesmo tamanho
        if descritorKeypoint_I.shape[0] > descritorKeypoint_J.shape[0]:
            descritorKeypoint_I = descritorKeypoint_I[:descritorKeypoint_J.shape[0], :]
        elif descritorKeypoint_J.shape[0] > descritorKeypoint_I.shape[0]:
            descritorKeypoint_J = descritorKeypoint_J[:descritorKeypoint_I.shape[0], :]

        return descritorKeypoint_I, descritorKeypoint_J

    # ------------------------------------------- carregarImagemPretoBranco ------------------------------------------ #
    @staticmethod
    def carregarImagemPretoBranco(imagemConteudo):
        # Carrega imagem a partir de bytes e redimensiona para um tamanho padrão.
        imagem = Image.open(BytesIO(imagemConteudo))
        imagem = imagem.resize((800, 600))

        # Converta a imagem para um array NumPy.
        imagem_np = np.array(imagem)

        # Verifique o número de canais da imagem.
        if len(imagem_np.shape) == 2:  # Imagem já está em escala de cinza.
            imagemPretoBranco = imagem_np
        elif len(imagem_np.shape) == 3 and imagem_np.shape[2] == 3:  # Imagem RGB.
            imagemPretoBranco = cv2.cvtColor(imagem_np, cv2.COLOR_RGB2GRAY)
        else:
            raise ValueError("Formato de imagem inválido ou número de canais não suportado.")

        # Aplica equalização de histograma para melhorar o contraste.
        imagemPretoBranco = cv2.equalizeHist(imagemPretoBranco)

        return imagemPretoBranco

    # ------------------------------------------ calcularDistanciaEuclidiana ----------------------------------------- #
    @staticmethod
    def calcularDistanciaEuclidiana(descritor1, descritor2):
        try:
            uteis.adicionarLog(f' ---> Comecando o calculo de distancia euclidiana entre os descritores')

            # Calcula a distância Euclidiana entre descritores
            distancias = np.linalg.norm(descritor1 - descritor2, axis=1)
            uteis.adicionarLog(f' + distancia(s): {distancias}')

            uteis.adicionarLog(f' <--- Encerrando o calculo de distancia euclidiana entre os descritores')

            return distancias

        except Exception as e:
            uteis.encontrouError(f' Error: Falha no calculo de distancia euclidiana entre os descritores: {descritor1} :: {descritor2}. Erro: {str(e)} \n')

    # ------------------------------------------------ compararLimiar ------------------------------------------------ #
    @staticmethod
    def compararLimiar(distancias, limiar):
        try:
            uteis.adicionarLog(f' ---> Comecando a comparacao do limiar com a distancia minima')

            # Identifica a menor distância e compara com o limiar para verificar duplicidade.
            minimo = np.argmin(distancias)
            uteis.adicionarLog(f' + indice minimo: {minimo}')
            distanciaMinima = distancias[minimo]
            uteis.adicionarLog(f' + distancia minima: {distanciaMinima}')

            uteis.adicionarLog(f' <--- Encerrando a comparacao do limiar com a distancia minima')

            # Retorna True se a distância mínima estiver abaixo do limiar.
            if distanciaMinima < limiar:
                return True, distanciaMinima, minimo
            else:
                return False, distanciaMinima, minimo

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na comparacao do limiar com a distancia minima. Erro: {str(e)} \n')

    # --------------------------------------------- compararDescritores ---------------------------------------------- #
    def compararDescritores(self, descritoresImagemI, descritoresImagemJ, imagemI, imagemJ):
        try:
            achou = False

            uteis.adicionarLog(f' ---> Comecando a comparacao dos descritores da imagem I: {imagemI["id"]} - {imagemI["name"]} e da imagem J: {imagemJ["id"]} - {imagemJ["name"]}')

            distancia = self.calcularDistanciaEuclidiana(descritoresImagemI, descritoresImagemJ)
            resultadoComparativo, valorMinimo, indiceMinimo = self.compararLimiar(distancia, 10)

            # Compara descritores de duas imagens e verifica se são duplicadas.
            if resultadoComparativo:
                if imagemJ not in self.imagensDuplicadas:
                    uteis.adicionarLog(f'  - ID: {imagemI["id"]} - Nome: {imagemI["name"]} == ID: {imagemJ["id"]} - Nome: {imagemJ["name"]}')
                    self.imagensDuplicadas.append(imagemJ)
                    achou = True

            uteis.adicionarLog(f' <--- Encerrando a comparacao dos descritores da imagem I: {imagemI["id"]} - {imagemI["name"]} e da imagem J: {imagemJ["id"]} - {imagemJ["name"]} \n')

            if achou:
                return True
            else:
                return False

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na comparacao dos descritores. Erro: {str(e)} \n')

    # ------------------------------------------- verificarFotosDuplicada -------------------------------------------- #
    def verificarFotosDuplicadas(self):
        uteis.adicionarLog(f' ===> Comecando a listagem das imagens recursivamente da pasta: {self.pastaId}')

        # Recupera imagens da pasta e inicializa SIFT para extrair descritores.
        imagens = self.googleDrive.obterImagensRecursivamente(self.pastaId, self.filtroDataInicio, self.filtroDataFinal)

        uteis.adicionarLog(f' ===> Encerrando a listagem das imagens recursivamente da pasta: {self.pastaId} \n')


        uteis.adicionarLog(f' ===> Verificando duplicidade na pasta: {self.pastaId} \n')

        sift = cv2.SIFT_create()

        listaKeypoints = []
        listaDescritoresImagem = []
        listaImagem = []

        # Itera sobre imagens, convertendo-as para escala de cinza e extraindo descritores.
        for imagem in imagens:
            url = f'https://www.googleapis.com/drive/v3/files/{imagem["id"]}?alt=media'
            response = requests.get(url, headers={'Authorization': f'Bearer {self.googleDrive.googleTokens.access_token}'})

            imagemConteudoCarregado = self.carregarImagemPretoBranco(response.content)
            keypoints, descritores = sift.detectAndCompute(imagemConteudoCarregado, None)

            listaKeypoints.append(keypoints)
            listaDescritoresImagem.append(descritores)
            listaImagem.append(imagem)

        # Compara descritores de cada imagem para verificar duplicidade.
        for i in range(len(listaDescritoresImagem)):
            descritoresImagemI = listaDescritoresImagem[i]
            imagemI = listaImagem[i]
            for j in range(i + 1, len(listaDescritoresImagem)):
                descritoresImagemJ = listaDescritoresImagem[j]
                imagemJ = listaImagem[j]
                descritoresImagemI, descritoresImagemJ = self.configurarDescritor(descritoresImagemI, descritoresImagemJ)
                self.compararDescritores(descritoresImagemI, descritoresImagemJ, imagemI, imagemJ)

        # Baixa e deleta imagens duplicadas conforme configuração.
        self.googleDrive.baixarListaImagens(self.imagensDuplicadas)
        if self.filtroRecortarCopiarArquivo == 'recortar':
            self.googleDrive.deletarListaImagens(self.imagensDuplicadas)

        uteis.adicionarLog(f' Verificacao duplicidade concluido com sucesso na pasta: {self.pastaId} \n')

    # ------------------------------------------ configurarFotosDuplicadas ------------------------------------------- #
    def configurarDuplicidade(self):
        try:
            uteis.adicionarLog(' ===> Comecando a configuracao')

            # Configura parâmetros de duplicidade a partir de entrada de usuário e recupera tokens de autenticação
            self.googleDrive.buscarTokensGoogloBanco()
            self.pastaId = uteis.validarParametro(3, str)
            self.filtroDataInicio = uteis.validarParametro(4, str, optional=True, default=None)
            self.filtroDataFinal = uteis.validarParametro(5, str, optional=True, default=None)
            self.filtroRecortarCopiarArquivo = uteis.validarParametro(6, str, optional=True, default='copiar')
            uteis.adicionarLog(
                f' Parametros: \n'
                f' + Caminho pasta Id = {uteis.caminhoPastaUsuario}; \n'
                f' + Caminho Arquivo Temp = {uteis.caminhoPastaTemp}; \n'
                f' + Caminho Arquivo Log = {uteis.caminhoArquivoLog}; \n'
                f' + ID Pasta Google Drive = {self.pastaId}; \n'
                f' + Filtro Data Inicial = {self.filtroDataInicio}; \n'
                f' + Filtro Data Final = {self.filtroDataFinal}; \n'
                f' + Filtro Recorta ou Copia = {self.filtroRecortarCopiarArquivo};'
            )

            uteis.adicionarLog(' <=== Encerrando a configuracao \n')

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na configuracao. Erro: {str(e)} \n')
