# -*- coding: utf-8 -*-
"""
Cria um backup de toda a pasta raiz, exceto:
- .venv
- Pasta z_backup
- Este próprio script e o de restauração
O arquivo gerado vai para a pasta z_backup, nomeado como aaaammdd_hhmmss.zip
"""

import os
import zipfile
from datetime import datetime

# ─── Caminhos ─────────────────────────────────────────────────────
PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PASTA_BACKUP = os.path.join(PASTA_RAIZ, 'z_backup')

# ─── Garante que a pasta de backup exista ────────────────────────
os.makedirs(PASTA_BACKUP, exist_ok=True)

# ─── Nome do arquivo zip ──────────────────────────────────────────
nome_zip = datetime.now().strftime('%Y%m%d_%H%M%S') + '.zip'
caminho_zip = os.path.join(PASTA_BACKUP, nome_zip)

# ─── Faz o backup ─────────────────────────────────────────────────
with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for raiz, pastas, arquivos in os.walk(PASTA_RAIZ):
        # Ignora pastas específicas
        if any(p in raiz for p in ['.venv', 'z_backup', 'zFazBackup', 'zRestauraUltimoBackup']):
            continue
        for arquivo in arquivos:
            caminho_completo = os.path.join(raiz, arquivo)
            caminho_relativo = os.path.relpath(caminho_completo, PASTA_RAIZ)
            zipf.write(caminho_completo, caminho_relativo)

print(f"\n✅ Backup criado com sucesso em:\n{caminho_zip}")
