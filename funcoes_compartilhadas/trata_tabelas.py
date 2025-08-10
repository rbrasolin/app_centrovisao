# -*- coding: utf-8 -*-
"""
Camada UI genérica – exibe, filtra, edita. Não converte dados!

• Exibe DataFrame editável com Streamlit.
• Números sempre com 2 casas decimais.
• Vírgula digitada tratada como ponto.
• Funções especiais: Deletar e Clonar Seleção.
"""

import streamlit as st
import pandas as pd
import re
from typing import Dict, Any, List, Callable
from datetime import datetime
from io import BytesIO

# ──────────────────────────────────────────────────────────────────────────────
# 🔄 FORÇA RERUN
# ──────────────────────────────────────────────────────────────────────────────
def _rerun():
    (st.rerun if hasattr(st, "rerun") else st.experimental_rerun)()


# ──────────────────────────────────────────────────────────────────────────────
# 🗂️ GERENCIAR ESTADO DO GRID
# ──────────────────────────────────────────────────────────────────────────────
def gerenciar_estado_grid(page_id: str):
    if st.session_state.get("_pagina_atual") != page_id:
        for k in list(st.session_state):
            if k.startswith("grid"):
                del st.session_state[k]
        st.session_state["_pagina_atual"] = page_id


# ──────────────────────────────────────────────────────────────────────────────
# 📊 GRID EDITÁVEL COM SELEÇÃO
# ──────────────────────────────────────────────────────────────────────────────
def grid(df: pd.DataFrame, col_visiveis: Dict[str, str | Any],
         id_col: str, key: str = "grid",
         exportar_excel: bool = True, nome_arquivo: str = "dados.xlsx"
         ) -> tuple[pd.DataFrame, List[Any]]:
    if df.empty:
        st.info("Nenhum registro para exibir.")
        return df.copy(), []

    df = df.reset_index(drop=True)
    df.insert(0, "Selecionar", False)
    df["_row"] = df.index

    cfg: Dict[str, Any] = {
        "Selecionar": st.column_config.CheckboxColumn("", width="60"),
        "_row": None,
    }

    for campo, rotulo in col_visiveis.items():
        if not isinstance(rotulo, str):
            cfg[campo] = rotulo
        elif df[campo].dropna().isin([0, 1, True, False]).all():
            cfg[campo] = st.column_config.CheckboxColumn(rotulo)
        elif pd.api.types.is_numeric_dtype(df[campo]):
            cfg[campo] = st.column_config.NumberColumn(rotulo, format="%.2f")
        else:
            cfg[campo] = rotulo

    edit = st.data_editor(
        df[["Selecionar", *col_visiveis, "_row"]],
        hide_index=True,
        num_rows="fixed",
        use_container_width=True,
        column_config=cfg,
        key=key,
    )

    ids = df.loc[edit[edit["Selecionar"]]["_row"], id_col].tolist()



    # 🔽 Botão Exportar Excel logo abaixo, à direita
    if exportar_excel:
        col1, col2, col3 = st.columns([30, 6, 4])
        with col3:
            buffer = BytesIO()
            df.drop(columns=["Selecionar", "_row"], errors="ignore").to_excel(buffer, index=False)
            buffer.seek(0)
            st.download_button(
                label="📥 Excel",
                data=buffer,
                file_name=nome_arquivo if nome_arquivo.endswith(".xlsx") else nome_arquivo + ".xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )




    return edit, ids


# ──────────────────────────────────────────────────────────────────────────────
# 💾 SALVAR EDIÇÕES
# ──────────────────────────────────────────────────────────────────────────────
_num_re = r"\d+(?:[.,]\d+)?"

def _to_float(v):
    if isinstance(v, str) and re.fullmatch(_num_re, v):
        return float(v.replace(",", "."))
    return v


def salvar_edicoes(editado, original, editaveis: List[str], fn_update: Callable, tabela: str, id_col: str, tipos: dict):
    if editado.empty:
        return

    mapa = {c.lower(): c for c in original.columns}
    id_real = mapa[id_col.lower()]
    original = original.reset_index(drop=True)

    changes = []
    for _, row in editado.iterrows():
        o = original.loc[int(row["_row"])]
        diff = {c: _to_float(row[c]) for c in editaveis if str(_to_float(row[c])) != str(o.get(c, ""))}
        if diff:
            changes.append({"id": o[id_real], "val": diff})

    if not changes:
        return

    if st.button("💾 Salvar Alterações"):
        tot = 0
        for ch in changes:
            tot += fn_update(
                tabela,
                list(ch["val"].keys()),
                list(ch["val"].values()),
                where=f"{id_real},eq,{ch['id']}",
                tipos_colunas=tipos,
            )
        st.success(f"✅ {tot} registro(s) atualizado(s).")
        st.cache_data.clear()
        _rerun()


# ──────────────────────────────────────────────────────────────────────────────
# ⚙️ OPÇÕES ESPECIAIS (DELETE + CLONE)
# ──────────────────────────────────────────────────────────────────────────────
def opcoes_especiais(tabela: str, ids: List[Any], fn_delete: Callable, id_col: str, tipos: dict, fn_insert: Callable | None = None):
    if not ids:
        return

    with st.container(border=True):
        st.markdown(f"✅ **{len(ids)} registro(s) selecionado(s)**")
        opcoes = ["selecione...", "🗑️ Deletar Linhas"]
        if fn_insert:
            opcoes.append("📄 Clonar Seleção")

        opcao = st.selectbox("⚙️ Opções", opcoes)

        # Delete
        if opcao == "🗑️ Deletar Linhas":
            if st.button("⚠️ Confirmar Deleção"):
                aviso = st.info("DELETANDO DADOS, AGUARDE...")
                tot = sum(fn_delete(tabela, f"{id_col},eq,{i}", tipos) for i in ids)
                aviso.empty()
                st.success(f"🗑️ {tot} registro(s) deletado(s).")
                st.cache_data.clear()
                _rerun()

        # Clone
        if opcao == "📄 Clonar Seleção" and fn_insert:
            st.markdown("### 📝 Editar antes de clonar")

            from funcoes_compartilhadas import conversa_banco as _cb

            df_total = _cb.select(tabela, tipos)
            df_sel = df_total[df_total[id_col].isin(ids)].reset_index(drop=True)
            if df_sel.empty:
                st.warning("Nada para clonar.")
                return

            df_edit = df_sel.drop(columns=[id_col], errors="ignore")
            st.write("Altere valores (ID será gerado automaticamente).")

            edit = st.data_editor(
                df_edit,
                hide_index=True,
                num_rows="fixed",
                use_container_width=True,
                key="clone_editor",
            )

            qtd = int(st.number_input("Quantidade de cópias", min_value=1, step=1, value=1))

            if st.button("📄 Confirmar Cópia", key="confirmar_clone"):
                aviso = st.info("CLONANDO DADOS, AGUARDE...")
                novos: List[dict] = []
                agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                for _, linha in edit.iterrows():
                    base = linha.to_dict()
                    for col, tp in tipos.items():
                        if tp == "data" and col in base:
                            base[col] = agora
                    for _ in range(qtd):
                        novos.append(base.copy())

                if novos:
                    fn_insert(tabela, pd.DataFrame(novos))

                aviso.empty()
                st.success(f"✅ {len(novos)} registro(s) inserido(s).")
                st.cache_data.clear()
                st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# 🔍 FILTRO DE TABELA
# ──────────────────────────────────────────────────────────────────────────────
def filtrar_tabela(df: pd.DataFrame, campos: List[str], nome: str = "filtro") -> pd.DataFrame:
    with st.popover("🔍 Filtros"):
        st.subheader("Filtrar Dados")
        filtros = {c: st.text_input(f"{c} contém", key=f"{nome}_{c}") for c in campos}
        col1, col2 = st.columns([2, 1.5])
        if col1.button("✅ Aplicar", key=f"{nome}_aplicar"):
            for c, v in filtros.items():
                if v:
                    df = df[df[c].astype(str).str.contains(v, case=False, na=False)]
        if col2.button("🧹 Limpar", key=f"{nome}_limpar"):
            st.session_state.clear()
            _rerun()
    return df

