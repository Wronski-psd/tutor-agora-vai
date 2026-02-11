import sqlite3
import os
from tutores import TUTORES_DATA 
from dados_unicv import DADOS_UNICV

DB_NAME = 'tutor_inteligente.db'

# 1. LIMPEZA TOTAL
if os.path.exists(DB_NAME):
    try:
        os.remove(DB_NAME)
        print("🧹 Banco de dados antigo removido.")
    except PermissionError:
        print("⚠️ Feche o App ou o DBeaver antes de rodar o reset!")
        exit()

conexao = sqlite3.connect(DB_NAME)
cursor = conexao.cursor()

# 2. CRIAÇÃO DAS TABELAS
cursor.execute('CREATE TABLE tutores (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, area TEXT, avatar_url TEXT, personalidade TEXT)')
cursor.execute('CREATE TABLE faqs (id INTEGER PRIMARY KEY AUTOINCREMENT, tutor_id INTEGER, pergunta_chave TEXT, resposta_base TEXT)')
cursor.execute('CREATE TABLE historico (id INTEGER PRIMARY KEY AUTOINCREMENT, tutor_id INTEGER, role TEXT, content TEXT, data_hora DATETIME DEFAULT CURRENT_TIMESTAMP)')

# TABELA DE FEEDBACKS (O que o bot não soube responder)
cursor.execute('''
    CREATE TABLE feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        tutor_id INTEGER, 
        pergunta_usuario TEXT, 
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# 3. POPULANDO DADOS
for tutor in TUTORES_DATA:
    cursor.execute('INSERT INTO tutores (nome, area, avatar_url, personalidade) VALUES (?, ?, ?, ?)', 
                   (tutor['nome'], tutor['area'], tutor['avatar'], tutor['persona']))
    id_tutor = cursor.lastrowid
    for info in DADOS_UNICV:
        cursor.execute('INSERT INTO faqs (tutor_id, pergunta_chave, resposta_base) VALUES (?, ?, ?)', 
                       (id_tutor, info['pergunta'].lower(), info['resposta']))

conexao.commit()
conexao.close()
print("🎉 Banco resetado e pronto para capturar feedbacks!")