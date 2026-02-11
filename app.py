import streamlit as st
import sqlite3
import os
import difflib

# --- 1. CONFIGURAÇÃO VISUAL E AMBIENTE ---
st.set_page_config(page_title="Tutor UniCV - Mediador", page_icon="🎓")

def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

local_css("style.css")

def get_db_connection():
    conn = sqlite3.connect('tutor_inteligente.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- 2. AUTO-INICIALIZAÇÃO DO BANCO (CORREÇÃO PARA O SERVIDOR) ---
def inicializar_ambiente():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Testa se a tabela de tutores existe e tem dados
        cursor.execute("SELECT count(*) FROM tutores")
        if cursor.fetchone()[0] == 0:
            raise Exception("Banco Vazio")
    except:
        # Se falhar, recria tudo automaticamente usando seus arquivos .py de dados
        from tutores import TUTORES_DATA 
        from dados_unicv import DADOS_UNICV
        
        cursor.execute('DROP TABLE IF EXISTS tutores')
        cursor.execute('DROP TABLE IF EXISTS faqs')
        cursor.execute('DROP TABLE IF EXISTS feedbacks')
        
        cursor.execute('CREATE TABLE tutores (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, area TEXT, avatar_url TEXT, personalidade TEXT)')
        cursor.execute('CREATE TABLE faqs (id INTEGER PRIMARY KEY AUTOINCREMENT, tutor_id INTEGER, pergunta_chave TEXT, resposta_base TEXT)')
        cursor.execute('CREATE TABLE feedbacks (id INTEGER PRIMARY KEY AUTOINCREMENT, tutor_id INTEGER, pergunta_usuario TEXT, data_hora DATETIME DEFAULT CURRENT_TIMESTAMP)')

        for tutor in TUTORES_DATA:
            cursor.execute('INSERT INTO tutores (nome, area, avatar_url, personalidade) VALUES (?, ?, ?, ?)', 
                           (tutor['nome'], tutor['area'], tutor['avatar'], tutor['persona']))
            id_tutor = cursor.lastrowid
            for info in DADOS_UNICV:
                cursor.execute('INSERT INTO faqs (tutor_id, pergunta_chave, resposta_base) VALUES (?, ?, ?)', 
                               (id_tutor, info['pergunta'].lower(), info['resposta']))
        conn.commit()
    finally:
        conn.close()

# Garante que o banco esteja pronto antes de carregar o restante da página
inicializar_ambiente()

# --- 3. BARRA LATERAL ---
try:
    conn = get_db_connection()
    tutores = conn.execute('SELECT * FROM tutores').fetchall()
    conn.close()
except:
    st.error("Erro crítico ao carregar os mediadores.")
    st.stop()

st.sidebar.header("Mediadores UniCV")
area_sel = st.sidebar.selectbox("Escolha a Área:", [t['area'] for t in tutores])
tutor_atual = next(t for t in tutores if t['area'] == area_sel)

st.sidebar.divider()
if st.sidebar.button("🗑️ Limpar Chat"):
    st.session_state.messages = []
    st.rerun()

# --- 4. ÁREA DE CHAT ---
st.title(f"Mediador(a) de {tutor_atual['area']}")

if "messages" not in st.session_state or "tutor_id" not in st.session_state or st.session_state.tutor_id != tutor_atual['id']:
    st.session_state.messages = []
    st.session_state.tutor_id = tutor_atual['id']

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. LÓGICA DE BUSCA APROXIMADA E FEEDBACK ---
prompt = st.chat_input("Tire sua dúvida sobre o UniCV...")

if prompt:
    user_input = prompt.lower().strip()
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    conn = get_db_connection()
    faqs = conn.execute("SELECT pergunta_chave, resposta_base FROM faqs WHERE tutor_id = ?", (tutor_atual['id'],)).fetchall()
    
    resposta_final = None
    todas_as_chaves = []
    mapeamento_respostas = {}

    for item in faqs:
        termos = [c.strip() for c in item['pergunta_chave'].split('/')]
        for t in termos:
            todas_as_chaves.append(t)
            mapeamento_respostas[t] = item['resposta_base']

    # Busca Aproximada (Fuzzy)
    matches = difflib.get_close_matches(user_input, todas_as_chaves, n=1, cutoff=0.6)

    if matches:
        resposta_final = mapeamento_respostas[matches[0]]
    else:
        # Busca por Substring (fallback)
        for chave, resposta in mapeamento_respostas.items():
            if chave in user_input or user_input in chave:
                resposta_final = resposta
                break

    # SE NÃO ENCONTRAR: Salva a dúvida para revisão futura
    if not resposta_final:
        conn.execute(
            "INSERT INTO feedbacks (tutor_id, pergunta_usuario) VALUES (?, ?)",
            (tutor_atual['id'], prompt)
        )
        conn.commit()
        resposta_final = "Ainda não tenho essa informação exata. Mas já anotei aqui para aprender! Tente perguntar sobre **preços, cursos ou localização**."

    conn.close()

    with st.chat_message("assistant"):
        st.markdown(resposta_final)
    st.session_state.messages.append({"role": "assistant", "content": resposta_final})