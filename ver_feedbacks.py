import sqlite3

def visualizar_feedbacks():
    conn = sqlite3.connect('tutor_inteligente.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Puxa os feedbacks e o nome do tutor que estava ativo na hora
    query = """
    SELECT f.id, t.nome as tutor, f.pergunta_usuario, f.data_hora 
    FROM feedbacks f
    JOIN tutores t ON f.tutor_id = t.id
    ORDER BY f.data_hora DESC
    """
    
    feedbacks = cursor.execute(query).fetchall()
    conn.close()

    if not feedbacks:
        print("✅ Nenhuma pergunta sem resposta por enquanto. O bot está afiado!")
        return

    print(f"{'ID':<4} | {'TUTOR':<15} | {'PERGUNTA DO ALUNO':<40} | {'DATA'}")
    print("-" * 80)
    for f in feedbacks:
        print(f"{f['id']:<4} | {f['tutor']:<15} | {f['pergunta_usuario']:<40} | {f['data_hora']}")

if __name__ == "__main__":
    visualizar_feedbacks()
    