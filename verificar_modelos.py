import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega sua chave
load_dotenv()
chave = os.getenv("GEMINI_API_KEY")

if not chave:
    print("❌ ERRO: Não encontrei a chave no arquivo .env")
else:
    print(f"✅ Chave encontrada! (Começa com: {chave[:5]}...)")
    
    try:
        genai.configure(api_key=chave)
        print("🔎 Buscando modelos disponíveis para você...")
        
        # Pede a lista oficial pro Google
        modelos = genai.list_models()
        
        encontrou_algum = False
        for m in modelos:
            # Só queremos modelos que geram texto (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                print(f"   👉 Disponível: {m.name}")
                encontrou_algum = True
        
        if not encontrou_algum:
            print("⚠️ Conectei, mas não achei modelos de texto. Verifique se a API está ativada no Google AI Studio.")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")