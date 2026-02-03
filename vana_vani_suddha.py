import os
import json
import re
import google.generativeai as genai
from typing import List, Dict

# CONFIGURAÇÕES DE API (Devem estar no GitHub Secrets)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class VanaVaniSuddha:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def get_forensic_prompt(self, raw_text: str) -> str:
        """
        Prompt especializado para formatar o texto para o Plugin Vana V19.
        """
        return f"""
        ROLE: Expert Vaishnava Editor and Sanskrit Scholar.
        GOAL: Transcribe and purify the following lecture for the Vana V19 Platform.

        RULES:
        1. NO INVENTION: Do not add external info. If audio is unclear, use [UNAUDIBLE].
        2. SANSKRIT (IAST): Use proper diacritics (e.g., Kṛṣṇa, Śrīla Prabhupāda, bhakti).
        3. FORMATTING: 
           - Use **bold** for Divine Names and key Acharyas.
           - NEVER use standard markdown quotes (>). 
           - ALWAYS use the Vana Shortcode for verses: 
             [hk_passage type="verse" ref="SOURCE_IF_KNOWN"]
             Sanskrit text here
             [/hk_passage]
        4. STRUCTURE:
           - Maintain the flow of the speaker.
           - At the very end, create a section '🦪 PÉROLAS' with 3-5 high-impact quotes.

        RAW TEXT TO PURIFY:
        {raw_text}
        """

    def process_transcription(self, raw_text: str, target_lang: str = "pt-br"):
        """
        Executa a purificação e tradução.
        """
        prompt = self.get_forensic_prompt(raw_text)
        if target_lang == "pt-br":
            prompt += "\nOUTPUT LANGUAGE: Portuguese (Brazil) with a reverent tone."
        
        response = self.model.generate_content(prompt)
        return response.text

    def extract_metadata(self, raw_text: str) -> Dict:
        """
        Simula a extração de metadados para os campos ACF do WordPress.
        """
        # Exemplo de lógica para preencher os campos mapeados no plugin
        return {
            "aula_local": "Vrindavana, India", # Placeholder - expandir com IA
            "aula_tempo": 45,                  # Placeholder
            "idioma_original": "en"            # [cite: 201, 203, 206]
        }

# MÓDULO DE EXECUÇÃO (Para o GitHub Actions)
if __name__ == "__main__":
    # 1. Simulação de entrada (No GHA isso viria do Whisper/yt-dlp)
    raw_audio_transcript = "Bhaktir uttamā... Srila Rupa Goswami explains anyabhilasita sunyam..."
    
    pipeline = VanaVaniSuddha()
    
    print("🚀 Iniciando Purificação Vāṇī-Śuddha v6.0...")
    
    # Gerar versão em Português para o Plugin
    final_text_pt = pipeline.process_transcription(raw_audio_transcript, "pt-br")
    metadata = pipeline.extract_metadata(raw_audio_transcript)

    # 2. Preparar Payload para o WordPress REST API
    # Este objeto casa com o includes/rest-api.php do seu plugin [cite: 351, 437]
    payload = {
        "title": "A Essência de Bhakti-rasāmṛta-sindhu",
        "content": final_text_pt,
        "status": "publish",
        "meta": {
            "aula_local": metadata["aula_local"],
            "aula_tempo": metadata["aula_tempo"],
            "translation_group_id": "VID_nLrj2bDhZIU" # ID do YouTube [cite: 199]
        }
    }

    # No GHA, aqui dispararíamos o POST para beta.vanamadhuryamdaily.com
    print("\n--- TEXTO GERADO (VANA V19 READY) ---")
    print(final_text_pt)
    print("\n--- METADADOS PARA INGESTÃO ---")
    print(json.dumps(payload, indent=2))
    import requests

# Dados para o Handshake (Vindo do GitHub Secrets)
wp_url = "https://beta.vanamadhuryamdaily.com/wp-json/wp/v2/vana_aula"
user = os.getenv("WP_USER")
password = os.getenv("WP_APP_PASSWORD") # Aquela senha de 16 dígitos gerada no perfil

# Realizando o envio real
response = requests.post(wp_url, json=payload, auth=(user, password))

if response.status_code == 201:
    print(f"✅ SUCESSO! Aula postada. ID: {response.json().get('id')}")
else:
    print(f"❌ ERRO na postagem: {response.status_code} - {response.text}")

# No final do seu arquivo vana_vani_suddha.py

import requests

# Dados para o Handshake
# Tente 'vana_aula' ou apenas 'aulas', dependendo do rest_base do seu plugin
wp_url = "https://beta.vanamadhuryamdaily.com/wp-json/wp/v2/vana_aula"
user = os.getenv("WP_USER")
password = os.getenv("WP_APP_PASSWORD")

print(f"\n📡 Tentando postagem em: {wp_url}")

try:
    response = requests.post(wp_url, json=payload, auth=(user, password))
    
    if response.status_code == 201:
        print(f"✅ SUCESSO! Aula postada. ID: {response.json().get('id')}")
    elif response.status_code == 404:
        print("❌ ERRO 404: O WordPress não encontrou a rota 'vana_aula'.")
        print("👉 AÇÃO: Vá em Configurações > Links Permanentes no WP e clique em SALVAR.")
    else:
        print(f"❌ ERRO na postagem: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"💥 Falha crítica na conexão: {e}")
