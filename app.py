"""
Simulador de Leis de Newton — ADO 2 (Mecânica e Física Moderna)

"""

import streamlit as st

from sistemas import arrasto, centripeta

st.set_page_config(page_title="Leis de Newton", page_icon="🧪", layout="wide")

# Cada sistema: chave -> (texto do botão, módulo com a função renderizar()).
SISTEMAS = {
    "centripeta": ("Força centrípeta", centripeta),
    "arrasto": ("Força de arrasto", arrasto),
}

st.title("Leis de Newton — Simulador Interativo")

# O sistema escolhido fica guardado em session_state para sobreviver às
# reexecuções do script (o Streamlit roda o arquivo de novo a cada clique).
if "sistema" not in st.session_state:
    st.session_state.sistema = None

# Três botões lado a lado; o do sistema ativo aparece destacado.
colunas = st.columns(3)
for coluna, (chave, (titulo, _)) in zip(colunas, SISTEMAS.items()):
    ativo = st.session_state.sistema == chave
    if coluna.button(titulo, type="primary" if ativo else "secondary", key=f"btn_{chave}"):
        st.session_state.sistema = chave
        st.rerun()

st.divider()

if st.session_state.sistema is None:
    st.info("Escolha um dos sistemas acima para começar.")
else:
    SISTEMAS[st.session_state.sistema][1].renderizar()
