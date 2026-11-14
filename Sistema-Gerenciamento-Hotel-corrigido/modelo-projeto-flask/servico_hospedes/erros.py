class RegraDeNegocioError(Exception):
    def __init__(self, mensagem, status_code=400):
        super().__init__(mensagem)
        self.status_code = status_code


class ErroIntegracao(Exception):
    def __init__(self, mensagem, status_code=503):
        super().__init__(mensagem)
        self.status_code = status_code
