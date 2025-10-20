class ModelGoogleToken:
    """
    Modelo de dados para representar os tokens de autenticação do Google.

    Atributos:
        expires_in (int): Tempo em segundos para expiração do token.
        scope (str): Escopo(s) autorizado(s) para o token.
        token_type (str): Tipo do token (ex. "Bearer").
        created (str): Data de criação do token.
        user_id (str): ID do usuário associado ao token.
        access_token (str): Token de acesso usado para autenticação.
        refresh_token (str): Token de atualização para obter um novo token de acesso.
    """

    def __init__(self, expires_in, scope, token_type, created, user_id, access_token, refresh_token):
        """
        Inicializa uma nova instância de ModelGoogleToken com os dados do token.

        Parâmetros:
            expires_in (int): Tempo de expiração em segundos.
            scope (str): Escopo autorizado.
            token_type (str): Tipo do token.
            created (str): Data de criação.
            user_id (str): ID do usuário do token.
            access_token (str): Token de acesso.
            refresh_token (str): Token de atualização.
        """

        self.expires_in = expires_in
        self.scope = scope
        self.token_type = token_type
        self.created = created
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __repr__(self):
        """
        Retorna uma representação de string para depuração com todos os atributos do token.

        Formato:
            GoogleToken(expires_in=..., scope=..., token_type=..., created=..., user_id=..., access_token=..., refresh_token=...)
        """

        return (f'GoogleToken(expires_in={self.expires_in}, scope={self.scope}, '
                f'token_type={self.token_type}, created={self.created}, '
                f'user_id={self.user_id}, access_token={self.access_token}, '
                f'refresh_token={self.refresh_token})')
