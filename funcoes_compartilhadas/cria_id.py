# -*- coding: utf-8 -*-
import socket
from datetime import datetime

def cria_id(sequencia='1', usuario=None) -> str:
    """
    Gera um ID no formato:
    YYYYMMDD_HHMMSS_USUARIO_SEQUENCIA

    Parâmetros:
    - sequencia (str, opcional): valor livre, pode ser número ou texto. Default = '1'
    - usuario (str, opcional): se não informado, usa o IP da máquina (sem pontos)

    Retorna:
    - str: ID gerado
    """
    agora = datetime.now().strftime('%Y%m%d_%H%M%S')

    if not usuario:
        try:
            usuario = socket.gethostbyname(socket.gethostname()).replace('.', '')
        except:
            usuario = '00000000'

    return f"{agora}_{usuario}_{sequencia}"
