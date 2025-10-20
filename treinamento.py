import uteis
import cv2
import dlib
import _pickle as cPickle
import numpy as np

class Treinamento:
    # -------------------------------------------------- construtor -------------------------------------------------- #
    def __init__(self):
        # Caminho da imagem a ser usada no treinamento
        self.caminhoImagemTreinamento = None

        # Filtro para identificar o ID da pessoa a ser treinada
        self.filtroIdPessoa = None

        # Define o modo de detecção de faces (pode ser 'tipoHOG' ou 'tipoCNN')
        self.modoDeteccao = 'tipoHOG'

        # Caminhos dos arquivos dos modelos necessários para a detecção e reconhecimento facial
        caminhoBase = '/home/renan/Documentos/Projeto_TCC/Trabalho_TCC_v3/FotoPlus/storage/app/public/deteccao/dataset/' #'/var/www/projetosdevrenan/FotoPlus/storage/app/public/deteccao/dataset/'
        self.dataSet_CNN = f'{caminhoBase}mmod_human_face_detector.dat'
        self.dataSet_68Pontos = f'{caminhoBase}shape_predictor_68_face_landmarks.dat'
        self.dataSet_Face_Recognition = f'{caminhoBase}dlib_face_recognition_resnet_model_v1.dat'

        # Variáveis que armazenarão os detectores após configuração
        self.detectorFace = None
        self.detectorPontos = None
        self.reconhecimentoFacial = None

    # --------------------------------------------- verificarNumeroFaces --------------------------------------------- #
    @staticmethod
    def verificarNumeroFaces(caminhoImagem, facesDetectadas):
        try:
            uteis.adicionarLog(f' ---> Comecando a verificacao do numero de rosto(s) de pessoa(s) na imagem: {caminhoImagem}')

            # Verifica e registra o número de faces detectadas em uma imagem.
            numeroFacesDetectadas = len(facesDetectadas)

            uteis.adicionarLog(f' + num. faces detectadas: {numeroFacesDetectadas}')
            uteis.adicionarLog(f' + {facesDetectadas}')

            uteis.adicionarLog(f' <--- Encerrando a verificacao do numero de rosto(s) de pessoa(s) na imagem: {caminhoImagem} \n')
            return numeroFacesDetectadas

        except Exception as e:
            uteis.encontrouError(f' Error: Falha ao verificar o numero de faces na imagem: {caminhoImagem}. Erro: {str(e)} \n')

    # ------------------------------------------------ carregarImagem ------------------------------------------------ #
    @staticmethod
    def carregarImagem(caminhoImagem):
        try:
            uteis.adicionarLog(f' ---> Comecando o carregamento da imagem: {caminhoImagem} no OpenCV')

            # Usa OpenCV para carregar a imagem
            imagemCarregada = cv2.imread(caminhoImagem)

            uteis.adicionarLog(f' <--- Encerrando o carregamento da imagem: {caminhoImagem} no OpenCV \n')
            return imagemCarregada

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na leitura da imagem: {caminhoImagem}. Erro: {str(e)} \n')

    # -------------------------------------------- gravarArquivoPickleNpy -------------------------------------------- #
    def gravarArquivoPickleNpy(self, nplistaDescritor128Facial):
        # Grava descritores faciais em arquivos .pickle e .npy para armazenamento e futura consulta.
        uteis.adicionarLog(f' <--- Comecando a gravar os arquivos .pickle: {uteis.caminhoArquivoPickle} e o .npy: {uteis.caminhoArquivoNpy}')

        descritoresFaciais = None
        try:
            # Tenta carregar descritores existentes; se não, inicializa com a lista fornecida.
            descritoresFaciais = np.load(uteis.caminhoArquivoNpy)
        except FileNotFoundError:
            descritoresFaciais = None
        finally:
            if descritoresFaciais is None:
                descritoresFaciais = nplistaDescritor128Facial
            else:
                descritoresFaciais = np.concatenate((descritoresFaciais, nplistaDescritor128Facial), axis=0)

        idx = 0
        indice = {}
        try:
            with open(uteis.caminhoArquivoPickle, 'rb') as f:
                # Carrega ou inicializa o índice de pessoas para o arquivo pickle.
                indice = cPickle.load(f)
                idx = list(indice.keys())[-1]
                idx += 1
        except FileNotFoundError:
            idx = 0
            indice = {}
        finally:
            # Atribui o ID da pessoa ao índice
            indice[idx] = self.filtroIdPessoa

        try:
            # Salva descritores no arquivo .npy
            np.save(uteis.caminhoArquivoNpy, descritoresFaciais)

        except Exception as e:
            uteis.encontrouError(f' Error: Falha ao salvar o arquivo .npy: {uteis.caminhoArquivoNpy}, referente a imagem {self.caminhoImagemTreinamento}. Erro: {str(e)} \n')

        try:
            # Salva os índices no arquivo .pickle
            with open(uteis.caminhoArquivoPickle, 'wb') as f:
                cPickle.dump(indice, f)

        except Exception as e:
            uteis.encontrouError(f' Error: Falha ao salvar o arquivo .pickle: {uteis.caminhoArquivoPickle}, referente a imagem {self.caminhoImagemTreinamento}. Erro: {str(e)} \n')

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

    # ------------------------------------------------- detectarFace ------------------------------------------------- #
    def detectarFace(self, caminhoImagem, imagem):
        try:
            uteis.adicionarLog(f' ---> Comecando a deteccao de faces na imagem: {caminhoImagem}')

            # Detecta faces em uma imagem e retorna as regiões onde foram encontradas.
            facesDetectadas = self.detectorFace(imagem)
            uteis.adicionarLog(f' + Faces encontradas: {facesDetectadas}')

            uteis.adicionarLog(f' <--- Encerrando a deteccao de faces na imagem: {caminhoImagem} \n')
            return facesDetectadas

        except Exception as e:
            uteis.encontrouError(f' Error: Falha ao detectar faces na imagem: {caminhoImagem}. Erro: {str(e)} \n')

    # ------------------------------------------ treinarReconhecimentoFacial ----------------------------------------- #
    def treinarReconhecimentoFacial(self):
        # Treina o modelo de reconhecimento facial com uma nova imagem de treinamento.
        caminhoImagem = self.caminhoImagemTreinamento
        uteis.adicionarLog(f' ===> Comecando o treinamento do reconhecimento facial da imagem: {caminhoImagem} \n')

        imagemCarregada = self.carregarImagem(caminhoImagem)
        facesDetectadas = self.detectarFace(caminhoImagem, imagemCarregada)
        numeroFacesDetectadas = self.verificarNumeroFaces(caminhoImagem, facesDetectadas)

        if numeroFacesDetectadas == 1:
            nplistaDescritor128Facial = self.reconhecerFace(caminhoImagem, imagemCarregada, facesDetectadas[0])
            self.gravarArquivoPickleNpy(nplistaDescritor128Facial)
            uteis.adicionarLog(f' Treinamento concluido com sucesso da imagem: {caminhoImagem} \n')

        elif numeroFacesDetectadas > 1:
            uteis.encontrouError(f' Error: Ha mais de uma face na imagem: {caminhoImagem} \n')

        elif numeroFacesDetectadas < 1:
            uteis.encontrouError(f' Error: Nenhuma face encontrada no arquivo: {caminhoImagem} \n')

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

    # ------------------------------------------ configurarFotoTreinamento ------------------------------------------- #
    def configurarTreinamento(self):
        # Configura os parâmetros de treinamento para uma nova pessoa.
        try:
            self.caminhoImagemTreinamento = uteis.validarParametro(3, str)
            self.filtroIdPessoa = uteis.validarParametro(4, str, optional=True)

            uteis.adicionarLog(' ===> Comecando a configuracao')

            self.configurarDetectorFace()

            uteis.adicionarLog(
                f' Parametros: \n'
                f' + Caminho pasta Id = {uteis.caminhoPastaUsuario}; \n'
                f' + Caminho Arquivo Temp = {uteis.caminhoPastaTemp}; \n'
                f' + Caminho Arquivo Log = {uteis.caminhoArquivoLog}; \n'
                f' + Caminho Arquivo Pickle = {uteis.caminhoArquivoPickle}; \n'
                f' + Caminho Arquivo Npy = {uteis.caminhoArquivoNpy}; \n'
                f' + Caminho Imagem Treinamento = {self.caminhoImagemTreinamento}; \n'
                f' + Filtro ID Pessoa = {self.filtroIdPessoa}; \n'
            )

            uteis.adicionarLog(' <=== Encerrando a configuracao \n')

        except Exception as e:
            uteis.encontrouError(f' Error: Falha na configuracao. Erro: {str(e)} \n')
