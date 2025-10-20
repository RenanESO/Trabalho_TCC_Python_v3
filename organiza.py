import uteis
import requests
import cv2
import dlib
import os
import numpy as np
from PIL import Image
from googleServico import GoogleServico
from io import BytesIO
from typing import List, Dict

class Organiza:
    # -------------------------------------------------- construtor -------------------------------------------------- #
    def __init__(self):
        # Inicializa o serviço Google para interações com o Google Drive
        self.googleDrive = GoogleServico()

        # Inicializa os parâmetros para filtros e detecção
        self.pastaId = None
        self.filtroIdPessoa = None
        self.filtroDataInicio = None
        self.filtroDataFinal = None
        self.filtroRecortarCopiarArquivo = 'copiar'  # Default para "copiar" arquivos com faces encontradas; pode ser configurado para "recortar".
        self.filtroAumentarResolucaoImagem = None

        # Define o modo de detecção de faces (pode ser 'tipoHOG' ou 'tipoCNN')
        self.modoDeteccao = 'tipoHOG'

        # Caminhos dos datasets para detecção e reconhecimento facial
        caminhoBase = '/home/renan/Documentos/Projeto_TCC/Trabalho_TCC_v3/FotoPlus/storage/app/public/deteccao/dataset/'
        self.dataSet_CNN = f'{caminhoBase}mmod_human_face_detector.dat'
        self.dataSet_68Pontos = f'{caminhoBase}shape_predictor_68_face_landmarks.dat'
        self.dataSet_Face_Recognition = f'{caminhoBase}dlib_face_recognition_resnet_model_v1.dat'

        # Inicializa as variáveis de detecção e reconhecimento facial
        self.detectorFace = None
        self.detectorPontos = None
        self.reconhecimentoFacial = None

        # Armazena IDs das imagens com faces encontradas.
        self.imagensOrganizadas: List[Dict] = []

    # -------------------------------------------- mostrarImagemResultado -------------------------------------------- #
    @staticmethod
    def mostrarImagemResultado(caminhoImagem, imagem, face, pessoaRetornada):
        # Define as coordenadas para o retângulo em torno do rosto
        e, t, d, b = (int(face.left()), int(face.top()), int(face.right()), int(face.bottom()))
        cv2.rectangle(imagem, (e, t), (d, b), (0, 255, 255), 2)
        texto = f'{pessoaRetornada}'
        cv2.putText(imagem, texto, (d, t), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 255, 255))

        # Exibe a imagem e aguarda o usuário pressionar "ENTER" para fechar
        cv2.imshow(f'Aperte "ENTER" para prosseguir. Imagem Resultado: {caminhoImagem}', imagem)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ------------------------------------------ calcularDistanciaEuclidiana ----------------------------------------- #
    @staticmethod
    def calcularDistanciaEuclidiana(descritor1, descritor2):
        try:
            uteis.adicionarLog(f' ---> Comecando o calculo de distancia euclidiana entre os descritores')
            # Calcula a distância euclidiana entre dois descritores faciais.
            distancias = np.linalg.norm(descritor1 - descritor2, axis=1)
            uteis.adicionarLog(f' + distancia(s): {distancias}')
            uteis.adicionarLog(f' <--- Encerrando o calculo de distancia euclidiana entre os descritores \n')

            return distancias

        except Exception as e:
            uteis.encontrouError(f' Error: Falha no calculo de distancia euclidiana entre os descritores: {descritor1} :: {descritor2}. Erro: {str(e)} \n')

    # ------------------------------------------------ compararLimiar ------------------------------------------------ #
    @staticmethod
    def compararLimiar(distancias, limiar):
        try:
            uteis.adicionarLog(f' ---> Comecando a comparacao do limiar com a distancia minima ')

            # Compara a distância mínima com um limiar para determinar se a face corresponde.
            minimo = np.argmin(distancias)
            uteis.adicionarLog(f' + indice minimo: {minimo}')
            distanciaMinima = distancias[minimo]
            uteis.adicionarLog(f' + distancia minima: {distanciaMinima}')

            uteis.adicionarLog(f' <--- Encerrando a comparacao do limiar com a distancia minima \n')

            if distanciaMinima < limiar:
                return True, distanciaMinima, minimo
            else:
                return False, distanciaMinima, minimo

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na comparacao do limiar com a distancia minima. Erro: {str(e)} \n')

    # ---------------------------------------------- lerArquivoPickleNpy --------------------------------------------- #
    @staticmethod
    def lerArquivoPickleNpy():
        try:
            uteis.adicionarLog(f' ---> Comecando a leitura dos arquivos .pickle: {uteis.caminhoArquivoPickle} e o .npy: {uteis.caminhoArquivoNpy}')

            # Lê os arquivos pickle e npy contendo os índices e descritores faciais.
            indices = np.load(uteis.caminhoArquivoPickle, allow_pickle=True)
            descritoresFaciais = np.load(uteis.caminhoArquivoNpy)

            uteis.adicionarLog(f' <--- Encerrando a leitura dos arquivos .pickle: {uteis.caminhoArquivoPickle} e o .npy: {uteis.caminhoArquivoNpy} \n')
            return indices, descritoresFaciais

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na leitura dos arquivos .pickle: {uteis.caminhoArquivoPickle} e o .npy: {uteis.caminhoArquivoNpy}. Erro: {str(e)} \n')

    # --------------------------------------------- verificarNumeroFaces --------------------------------------------- #
    @staticmethod
    def verificarNumeroFaces(imagem, facesDetectadas):
        try:
            uteis.adicionarLog(f' ---> Comecando a verificacao do numero de rosto(s) de pessoa(s) na imagem: {imagem["id"]} - {imagem["name"]}')

            # Verifica e registra o número de faces detectadas em uma imagem.
            numeroFacesDetectadas = len(facesDetectadas)

            uteis.adicionarLog(f' + num. faces detectadas: {numeroFacesDetectadas}')
            uteis.adicionarLog(f' + {facesDetectadas}')

            uteis.adicionarLog(f' <--- Encerrando a verificacao do numero de rosto(s) de pessoa(s) na imagem: {imagem["id"]} - {imagem["name"]} \n')
            return numeroFacesDetectadas

        except Exception as e:
            uteis.encontrouError(f' Error: Falha ao verificar o numero de faces na imagem: {imagem["id"]} - {imagem["name"]}. Erro: {str(e)} \n')

    # ------------------------------------------------ carregarImagem ------------------------------------------------ #
    @staticmethod
    def carregarImagem(imagem, imagemConteudo):
        try:
            uteis.adicionarLog(f' ---> Comecando o carregamento da imagem: {imagem["id"]} - {imagem["name"]} no OpenCV')

            # Carregar a imagem diretamente dos bytes obtidos do Google Drive
            imagemConteudoCarregado = Image.open(BytesIO(imagemConteudo))
            # Carrega uma imagem do Google Drive para o OpenCV.
            imagemConteudoCarregado = cv2.cvtColor(np.array(imagemConteudoCarregado), cv2.COLOR_RGB2BGR)

            uteis.adicionarLog(f' <--- Encerrando o carregamento da imagem: {imagem["id"]} - {imagem["name"]} no OpenCV')
            return imagemConteudoCarregado

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na leitura da imagem: {imagem["id"]} - {imagem["name"]}. Erro: {str(e)} \n')

    # ------------------------------------------------ reconhecerFace ------------------------------------------------ #
    def reconhecerFace(self, caminhoImagem, imagem, faceDetectada):
        try:
            uteis.adicionarLog(f' ---> Comecando o reconhecimento do rosto da pessoa com id: {self.filtroIdPessoa} na imagem: {caminhoImagem}')

            # Detecta pontos os 64 faciais, para realizar o alinhamento do rosto.
            pontos64Facial = self.detectorPontos(imagem, faceDetectada)
            # Gera um descritor facial de 128 pontos da face rente a pessoa.
            descritor128Facial = self.reconhecimentoFacial.compute_face_descriptor(imagem, pontos64Facial)

            # Converte descritores para arrays NumPy para garantir consistência no formato.
            descritor128Facial = [df for df in descritor128Facial]
            # Define o tipo dos dados do Array para Float.
            descritor128Facial = np.asarray(descritor128Facial, dtype=np.float64)
            # Retorna o descritor como array 2D.
            descritor128Facial = descritor128Facial[np.newaxis, :]

            uteis.adicionarLog(f' <--- Encerrando o reconhecimento do rosto da pessoa com id: {self.filtroIdPessoa} na imagem: {caminhoImagem} \n')
            return descritor128Facial

        except Exception as e:
            uteis.encontrouError(f' Error: Falha no detector de pontos para o reconhecimento facial na imagem {caminhoImagem}. Erro: {str(e)} \n')

    # ------------------------------------------------ procurarPessoa ------------------------------------------------ #
    def procurarPessoa(self, imagem, imagemConteudoCarregado, faceDetectada, indices, descritoresFaciais):
        try:
            uteis.adicionarLog(f' ---> Comecando a procura pela face da pessoa com id: {self.filtroIdPessoa} na imagem: {imagem["id"]} - {imagem["name"]}')


            # Procura uma pessoa específica na imagem, comparando a face detectada com descritores conhecidos.
            npArrayDescritorFacial = self.reconhecerFace(imagem['id'], imagemConteudoCarregado, faceDetectada)
            distancias = self.calcularDistanciaEuclidiana(npArrayDescritorFacial, descritoresFaciais)
            resultadoComparativo, valorMinimo, indiceMinimo = self.compararLimiar(distancias, 0.5)

            # Retorna o nome da pessoa se encontrada, caso contrário, retorna string vazia.
            if resultadoComparativo:
                pessoaRetornada = os.path.split(indices[indiceMinimo])[1].split('.')[0]
            else:
                pessoaRetornada = ''

            uteis.adicionarLog(f' <--- Encerrando a procura pela face da pessoa com id: {self.filtroIdPessoa} na imagem {imagem["id"]} - {imagem["name"]} \n')
            return pessoaRetornada

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na procura da pessoa com id: {self.filtroIdPessoa} na imagem {imagem["id"]} - {imagem["name"]}. Erro: {str(e)} \n')

    # ------------------------------------------------- detectarFace ------------------------------------------------- #
    def detectarFace(self, imagem, imagemConteudoCarregado):
        try:
            uteis.adicionarLog(f' ---> Comecando a deteccao de faces na imagem: {imagem["id"]} - {imagem["name"]}')

            # Detecta faces na imagem utilizando o modelo especificado.
            if self.filtroAumentarResolucaoImagem is None:
                # Modo padrão sem aumento de resolução.
                facesDetectadas = self.detectorFace(imagemConteudoCarregado)
                uteis.adicionarLog(f' + Faces encontradas: {facesDetectadas}')
            else:
                # Modo com aumento de resolução.
                facesDetectadas = self.detectorFace(imagemConteudoCarregado, self.filtroAumentarResolucaoImagem)
                uteis.adicionarLog(f' + Faces encontradas: {facesDetectadas}, resolucao aumentada: {self.filtroAumentarResolucaoImagem}x')

            uteis.adicionarLog(f' <--- Encerrando a deteccao de faces na imagem: {imagem["id"]} - {imagem["name"]} \n')
            return facesDetectadas

        except Exception as e:
            uteis.encontrouError(f' Error: Falha ao detectar faces na imagem: {imagem["id"]} - {imagem["name"]}. Erro: {str(e)} \n')

    # ----------------------------------------- reconhecimentoFacialOrganizar ---------------------------------------- #
    def reconhecimentoFacialOrganizar(self):
        uteis.adicionarLog(f' ===> Comecando a listagem das imagens recursivamente da pasta: {self.pastaId}')

        # Recupera imagens da pasta e inicializa extrair os descritores faciais.
        imagens = self.googleDrive.obterImagensRecursivamente(self.pastaId, self.filtroDataInicio, self.filtroDataFinal)
        uteis.adicionarLog(f' ===> Numero de imagens dentro da pasta: {len(imagens)} \n')

        uteis.adicionarLog(f' ===> Encerrando a listagem das imagens recursivamente da pasta: {self.pastaId} \n')

        uteis.adicionarLog(f' ===> Comecando a organizacao na pasta: {self.pastaId} \n')

        indices, descritoresFaciais = self.lerArquivoPickleNpy()

        for imagem in imagens:
            url = f'https://www.googleapis.com/drive/v3/files/{imagem["id"]}?alt=media'
            response = requests.get(url, headers={'Authorization': f'Bearer {self.googleDrive.googleTokens.access_token}'})

            if response.status_code == 200:
                achouPessoa = False

                # Organiza as imagens na pasta com base nos filtros definidos e detecção facial.
                imagemConteudoCarregado = self.carregarImagem(imagem, response.content)
                facesDetectadas = self.detectarFace(imagem, imagemConteudoCarregado)
                self.verificarNumeroFaces(imagem, facesDetectadas)

                for face in facesDetectadas:
                    if not achouPessoa:
                        # Compara os descritores das faces com as faces ja treinadas,com os descritores salvos.
                        pessoaRetornada = self.procurarPessoa(imagem, imagemConteudoCarregado, face, indices, descritoresFaciais)

                        if pessoaRetornada == self.filtroIdPessoa:
                            self.imagensOrganizadas.append(imagem)

                            achouPessoa = True
                    else:
                        break
            else:
                uteis.adicionarLog(f' Error: Falha ao baixar a imagem com ID {imagem["id"]} - {imagem["name"]}, status: {response.status_code}')

        # Baixa e deleta imagens duplicadas conforme configuração.
        self.googleDrive.baixarListaImagens(self.imagensOrganizadas)
        if self.filtroRecortarCopiarArquivo == 'recortar':
            self.googleDrive.deletarListaImagens(self.imagensOrganizadas)

        uteis.adicionarLog(f' Organizacao concluido com sucesso na pasta: {self.pastaId} \n')

    # ------------------------------------------- configurarDetectorFace --------------------------------------------- #
    def configurarDetectorFace(self):
        if self.modoDeteccao == 'tipoHOG':
            self.detectorFace = dlib.get_frontal_face_detector()
        elif self.modoDeteccao == 'tipoCNN':
            self.detectorFace = dlib.cnn_face_detection_model_v1(self.dataSet_CNN)

        try:
            self.detectorPontos = dlib.shape_predictor(self.dataSet_68Pontos)
        except Exception as e:
            raise RuntimeError(f'Erro ao carregar o modelo de pontos: {e}')

        self.reconhecimentoFacial = dlib.face_recognition_model_v1(self.dataSet_Face_Recognition)

    # ------------------------------------------ configurarFotosOrganizar -------------------------------------------- #
    def configurarOrganiza(self):
        try:
            # Configura parâmetros de duplicidade a partir de entrada de usuário e recupera tokens de autenticação
            self.googleDrive.buscarTokensGoogloBanco()
            self.pastaId = uteis.validarParametro(3, str)
            self.filtroDataInicio = uteis.validarParametro(4, str, optional=True, default=None)
            self.filtroDataFinal = uteis.validarParametro(5, str, optional=True, default=None)
            self.filtroRecortarCopiarArquivo = uteis.validarParametro(6, str, optional=True, default='copiar')
            self.filtroAumentarResolucaoImagem = uteis.validarParametro(7, int, optional=True, default=None)
            self.filtroIdPessoa = uteis.validarParametro(8, str, optional=True)

            uteis.adicionarLog(' ===> Comecando a configuracao')

            self.configurarDetectorFace()

            uteis.adicionarLog(
                f' Parametros: \n'
                f' + Caminho pasta Id = {uteis.caminhoPastaUsuario}; \n'
                f' + Caminho Arquivo Temp = {uteis.caminhoPastaTemp}; \n'
                f' + Caminho Arquivo Log = {uteis.caminhoArquivoLog}; \n'
                f' + Caminho Arquivo Pickle = {uteis.caminhoArquivoPickle}; \n'
                f' + Caminho Arquivo Npy = {uteis.caminhoArquivoNpy}; \n'
                f' + ID Pasta Google Drive = {self.pastaId}; \n'
                f' + ID da pessoa para organizar = {self.filtroIdPessoa}; \n'
                f' + Filtro Data Inicial = {self.filtroDataInicio}; \n'
                f' + Filtro Data Final = {self.filtroDataFinal}; \n'
                f' + Filtro Recorta ou Copia = {self.filtroRecortarCopiarArquivo}; \n'
                f' + Filtro Aumenta Resolucao = {self.filtroAumentarResolucaoImagem};'
            )

            uteis.adicionarLog(' <=== Encerrando a configuracao \n')

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na configuracao. Erro: {str(e)} \n')
