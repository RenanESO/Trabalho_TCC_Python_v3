from datetime import datetime
import os
import uteis
import requests
import mysql.connector
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from modelGoogleToken import ModelGoogleToken

from urllib.parse import quote

class GoogleServico:

    # -------------------------------------------------- construtor -------------------------------------------------- #
    def __init__(self):
        # Inicializa o serviço Google com o atributo de tokens como None.
        self.googleTokens = None

    # -------------------------------------------- autenticarGoogleDrive --------------------------------------------- #
    def autenticarGoogleDrive(self):
        try:
            # Autentica o Google Drive utilizando credenciais armazenadas em variáveis de ambiente Env.
            credencial = Credentials(
                token=self.googleTokens.access_token,
                refresh_token=self.googleTokens.refresh_token,
                token_uri=os.getenv("TOKEN_URI"),
                client_id=os.getenv("CLIENT_ID"),
                client_secret=os.getenv("CLIENT_SECRET"),
                scopes=os.getenv("SCOPE")
            )

            # Atualiza o token automaticamente se ele estiver expirado e houver um refresh token.
            if credencial.expired and credencial.refresh_token:
                credencial.refresh(Request())

            return credencial

        except Exception as e:
            uteis.encontrouError(f'Error: Falha ao autenticar o Google Drive com as credenciais. Erro: {str(e)} \n')

    # ------------------------------------------- buscarTokensGoogloBanco -------------------------------------------- #
    def buscarTokensGoogloBanco(self):
        try:
            # Busca tokens do Google no banco de dados e armazena no atributo googleTokens.
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USERNAME"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_DATABASE"),
                port=os.getenv("DB_PORT"),
                ssl_disabled=True
            )

            cursor = conn.cursor()
            query = """SELECT expires_in, scope, token_type, created, user_id, access_token, refresh_token
                       FROM google_tokens WHERE user_id = %s"""
            cursor.execute(query, (uteis.usuarioId,))
            result = cursor.fetchone()

            # Caso haja resultado, instancia "ModelGoogleToken" com os dados.
            if result:
                # Cria um objeto usuario com os dados retornados
                self.googleTokens = ModelGoogleToken(*result)  # Desempacota a tupla

            cursor.close()
            conn.close()

        except mysql.connector.Error as e:
            uteis.encontrouError(f'Error: Falha ao conectar ao banco de dados. Erro: {str(e)} \n')

    # ----------------------------------------------- listarArquivos ------------------------------------------------- #
    def listarArquivos(self, pastaID, data_inicio=None, data_fim=None):
        # Converte datas
        if isinstance(data_inicio, str):
            try:
                data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
            except ValueError:
                uteis.encontrouError("Formato inválido para data_inicio. Use 'DD/MM/YYYY'.")
                return []
        if isinstance(data_fim, str):
            try:
                data_fim = datetime.strptime(data_fim, "%d/%m/%Y")
            except ValueError:
                uteis.encontrouError("Formato inválido para data_fim. Use 'DD/MM/YYYY'.")
                return []

        if data_inicio:
            data_inicio = data_inicio.isoformat() + 'Z'
        if data_fim:
            data_fim = data_fim.isoformat() + 'Z'

        query = f"'{pastaID}' in parents"
        if data_inicio and data_fim:
            query += f" and modifiedTime >= '{data_inicio}' and modifiedTime <= '{data_fim}'"

        query_encoded = quote(query)
        todos_arquivos = []
        page_token = None

        while True:
            url = f'https://www.googleapis.com/drive/v3/files?q={query_encoded}&fields=nextPageToken,files(id,name,mimeType)&pageSize=1000'
            if page_token:
                url += f"&pageToken={page_token}"

            headers = {'Authorization': f'Bearer {self.googleTokens.access_token}'}

            # Debugging para verificar URL e Token
            print(f'URL chamada: {url}')
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                resultados = response.json()

                # Debugging do resultado da API
                print(f'Resposta recebida: {resultados}')

                todos_arquivos.extend(resultados.get('files', []))
                page_token = resultados.get('nextPageToken')

                # Verifica se a pesquisa está incompleta
                if resultados.get('incompleteSearch'):
                    print("Aviso: a pesquisa está incompleta, mesmo com resultados.")

                if not page_token:
                    break
            else:
                uteis.encontrouError(f'Erro: Código {response.status_code} retornado ao listar arquivos.')
                return []

        return todos_arquivos

        # # Converte as datas de string no formato "DD/MM/YYYY" para datetime, se necessário
        # if isinstance(data_inicio, str):
        #     try:
        #         data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
        #     except ValueError:
        #         uteis.encontrouError("Formato inválido para data_inicio. Use 'DD/MM/YYYY'.")
        #         return []
        #
        # if isinstance(data_fim, str):
        #     try:
        #         data_fim = datetime.strptime(data_fim, "%d/%m/%Y")
        #     except ValueError:
        #         uteis.encontrouError("Formato inválido para data_fim. Use 'DD/MM/YYYY'.")
        #         return []
        #
        # # Formata as datas para o padrão ISO 8601 com timezone UTC
        # if data_inicio:
        #     data_inicio = data_inicio.isoformat() + 'Z'
        # if data_fim:
        #     data_fim = data_fim.isoformat() + 'Z'
        #
        # # Constrói a query para listar arquivos com filtro de pasta e intervalo de datas
        # query = f"'{pastaID}' in parents"
        #
        # if data_inicio and data_fim:
        #     query += f" and modifiedTime >= '{data_inicio}' and modifiedTime <= '{data_fim}'"
        #
        # # Inicializa a lista para armazenar todos os arquivos
        # todos_arquivos = []
        #
        # # Página inicial é None
        # page_token = None
        #
        # while True:
        #     # Lista arquivos em uma pasta específica do Google Drive, utilizando o ID da pasta.
        #     url = f'https://www.googleapis.com/drive/v3/files?q={query}&fields=files(id,name,mimeType)&pageSize=1000'
        #     headers = {'Authorization': f'Bearer {self.googleTokens.access_token}'}
        #
        #     # Log para depurar a URL final que está sendo chamada
        #     print(f'URL chamada: {url}')
        #
        #     response = requests.get(url, headers=headers)
        #     if response.status_code == 200:
        #         # Retorna a lista de arquivos dentro da pasta especificada.
        #         resultados = response.json()
        #
        #         # Adiciona os arquivos retornados à lista total
        #         todos_arquivos.extend(resultados.get('files', []))
        #         #return resultados.get('files', [])
        #
        #         # Obtém o token para a próxima página, se existir
        #         page_token = resultados.get('nextPageToken')
        #
        #         if not page_token:
        #             break  # Sai do loop se não houver mais páginas
        #     else:
        #         uteis.encontrouError(f'Error: Código {response.status_code} retornado ao listar arquivos. \n')
        #         return []
        #
        # return todos_arquivos

    # ----------------------------------------- obterImagensRecursivamente ------------------------------------------- #
    def obterImagensRecursivamente(self, pastaID, data_inicio=None, data_fim=None):
        # Obtém todas as imagens dentro de uma pasta e subpastas do Google Drive recursivamente.
        arquivos = self.listarArquivos(pastaID, data_inicio, data_fim)
        imagens = []

        for arquivo in arquivos:
            # Verifica se é uma pasta
            if arquivo['mimeType'] == 'application/vnd.google-apps.folder':
                # Chamada recursiva para entrar na pasta e pegar arquivos
                sub_arquivos = self.obterImagensRecursivamente(arquivo['id'], data_inicio, data_fim)
                imagens.extend(sub_arquivos)
            else:
                # Se for uma imagem (JPG ou PNG), adiciona à lista de imagens
                if arquivo['mimeType'] in ['image/jpeg', 'image/png']:
                    imagens.append(arquivo)

        return imagens

    # ------------------------------------------------ baixarImagem -------------------------------------------------- #
    def baixarImagem(self, imagem):
        # Baixa uma imagem do Google Drive pelo ID para uma pasta temporária local.
        url = f'https://www.googleapis.com/drive/v3/files/{imagem["id"]}?alt=media'
        headers = {'Authorization': f'Bearer {self.googleTokens.access_token}'}

        # Faz a requisição para baixar a imagem
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Salva a imagem na pasta especificada
            if not os.path.exists(uteis.caminhoPastaTemp):
                os.makedirs(uteis.caminhoPastaTemp)
            caminho_arquivo = os.path.join(uteis.caminhoPastaTemp, f'{imagem["name"]}')
            with open(caminho_arquivo, 'wb') as f:
                f.write(response.content)
            uteis.adicionarLog(f'Imagem: {imagem["id"]} - {imagem["name"]} baixada com sucesso! \n')
        else:
            uteis.encontrouError(f'Error: Falha ao baixar a imagem {imagem["id"]} - {imagem["name"]} com o código {response.status_code} retornado. \n')

    # --------------------------------------------- baixarListaImagens ----------------------------------------------- #
    def baixarListaImagens(self, listaImagens):
        # Baixa uma lista de imagens especificadas por IDs do Google Drive.
        for imagem in listaImagens:
            self.baixarImagem(imagem)

    # ------------------------------------------------ deletarImagem ------------------------------------------------- #
    def deletarImagem(self, imagem, servico):
        try:
            # Deleta uma imagem do Google Drive com base no ID.
            servico.files().delete(fileId=imagem["id"]).execute()
            uteis.adicionarLog(f'Imagem: {imagem["id"]} - {imagem["name"]} deletada com sucesso! \n')

        except Exception as e:
            uteis.encontrouError(f'Error: Falha ao deletar a imagem {imagem["id"]} - {imagem["name"]}. Erro: {str(e)} \n')

    # --------------------------------------------- deletarListaImagens ---------------------------------------------- #
    def deletarListaImagens(self, listaImagens):
        # Deleta uma lista de imagens do Google Drive com base em seus IDs.
        credencial = self.autenticarGoogleDrive()
        servico = build('drive', 'v3', credentials=credencial)
        for imagem in listaImagens:
            self.deletarImagem(imagem, servico)

