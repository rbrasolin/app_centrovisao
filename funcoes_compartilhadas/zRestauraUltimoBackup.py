# -*- coding: utf-8 -*-
"""
Restaura o backup mais recente da pasta z_backup.
O processo:
- Deleta todos os arquivos e pastas, EXCETO:
  .venv, z_backup, zFazBackup.*, zRestauraUltimoBackup.* e os arquivos .bat
- Descompacta o backup mais recente na pasta raiz
"""

import os
import zipfile
from datetime import datetime

# ─── Caminhos ─────────────────────────────────────────────────────
PASTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PASTA_BACKUP = os.path.join(PASTA_RAIZ, 'z_backup')

# ─── Protege pastas e arquivos que NÃO podem ser deletados ────────
EXCECOES = ['.venv', 'z_backup', 'zFazBackup.py', 'zRestauraUltimoBackup.py',
            'zFazBackup.bat', 'zRestauraUltimoBackup.bat']

# ─── Busca o backup mais recente ──────────────────────────────────
arquivos_backup = [f for f in os.listdir(PASTA_BACKUP) if f.endswith('.zip')]
if not arquivos_backup:
    print("\n❌ Nenhum arquivo de backup encontrado na pasta z_backup.")
    exit()

# Ordena e pega o mais recente
arquivo_mais_recente = sorted(arquivos_backup, reverse=True)[0]
caminho_zip = os.path.join(PASTA_BACKUP, arquivo_mais_recente)

print(f"\n🔍 Backup encontrado: {arquivo_mais_recente}")

# ─── Deleta arquivos e pastas (exceto os protegidos) ───────────────
for item in os.listdir(PASTA_RAIZ):
    if item in EXCECOES:
        continue
    caminho = os.path.join(PASTA_RAIZ, item)
    try:
        if os.path.isfile(caminho) or os.path.islink(caminho):
            os.remove(caminho)
        elif os.path.isdir(caminho):
            import shutil
            shutil.rmtree(caminho)
    except Exception as e:
        print(f"⚠️ Erro ao deletar {caminho}: {e}")

print("🗑️ Arquivos antigos deletados.")

# ─── Extrai o backup ───────────────────────────────────────────────
with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
    zip_ref.extractall(PASTA_RAIZ)

print(f"✅ Backup restaurado com sucesso a partir de:\n{arquivo_mais_recente}")
