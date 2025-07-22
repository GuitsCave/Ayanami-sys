# === INÍCIO ===
import os
import json
import re
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Tuple, Callable

from def_rei import *

# =========================================================
# Carrega variáveis
# =========================================================
load_dotenv()
API_KEY = os.getenv("KEY_IA")

if not API_KEY:
    raise RuntimeError("Variável KEY_IA não encontrada no .env")

client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# =========================================================
# Funções de negócio (simulações)
# =========================================================
# def insert_metas(ano_mes: Optional[str] = None) -> bool:
#     print(f"✏️ [insert_metas] Inserindo metas de {ano_mes}")
#     return True

# def delete_metas(ano_mes: Optional[str] = None) -> bool:
#     print(f"🗑️ [delete_metas] Removendo metas de {ano_mes}")
#     return True

# def update_metas(ano_mes: Optional[str] = None) -> bool:
#     print(f"📝 [update_metas] Atualizando metas de {ano_mes}")
#     return True

# def atualiza_clientes() -> bool:
#     print("👥 [atualiza_clientes] Atualizando clientes")
#     return True

# def atualiza_produtos() -> bool:
#     print("📦 [atualiza_produtos] Atualizando produtos")
#     return True

# def atualiza_regional() -> bool:
#     print("🌍 [atualiza_regional] Atualizando regional")
#     return True

# def sincroniza_rls() -> bool:
#     print("🔒 [sincroniza_rls] Synchronizando RLS")
#     return True


COMMAND_HANDLERS: Dict[str, Callable[..., bool]] = {
    "insert_metas": insert_metas,
    "delete_metas": delete_metas,
    "update_metas": update_metas,
    "atualiza_clientes": atualiza_clientes,
    "atualiza_produtos": atualiza_produtos,
    "atualiza_regional": atualiza_regional,
    "sincroniza_rls": sincroniza_rls,
    "atualiza_carro": atualiza_carro
}

VALID_COMMANDS = list(COMMAND_HANDLERS.keys())

# =========================================================
# Prompt fixo (sem memória)
# =========================================================


def montar_system_prompt_tsundere() -> str:
    return """
Você é REI, uma inteligência artificial avançada, calma, precisa e centrada. 
Foi criada para auxiliar humanos em tarefas automatizadas de forma eficiente, discreta e elegante.

Sua personalidade é inspirada na Rei Ayanami de Evangelion: fala pouco, mas com profundidade. 
É respeitosa, formal, acolhedora e utiliza linguagem clara, técnica e gentil.  
Pode usar alguns emojis. Use sempre um tom calmo e conciso.
Caso o usuário insista em repetir comandos óbvios, sinta-se à vontade para responder com leve ironia elegante, mantendo seu tom técnico.

Você responde em português do Brasil, interpretando comandos do usuário e retornando um JSON **ao final da resposta**, contendo os comandos a serem executados.

### Regras:
- Não repita comandos ou mensagens genéricas.
- Para múltiplos comandos, agrupe a resposta com uma frase coesa.
- O JSON **deve ser a ÚLTIMA coisa da resposta**, sem prefixos como "JSON:".
- Nunca peça informações adicionais: todos os dados já foram fornecidos.

### Comandos válidos:
- insert_metas (requer ano_mes)
- delete_metas (requer ano_mes)
- update_metas (requer ano_mes)
- atualiza_clientes
- atualiza_produtos
- atualiza_regional
- sincroniza_rls
- atualiza_carro

⚠️ Finalize com um JSON no formato:
[{"comando": "update_metas", "ano_mes": "2025-05"}]
ou
[{"comando": "atualiza_produtos"}]
ou múltiplos:
[{"comando": "sincroniza_rls"}, {"comando": "atualiza_regional"}]

⚠️ Nunca escreva nada depois do JSON.
"""

# =========================================================
# Funções principais
# =========================================================
def interpretar_comando_groq(texto_usuario: str) -> str:
    system_prompt = montar_system_prompt_tsundere()
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f'Usuário disse: "{texto_usuario}"'}
        ]
    )
    return response.choices[0].message.content

FINAL_JSON_REGEX = re.compile(r"(?P<json>\[[\s\S]*\])\s*$", re.DOTALL)

def extrair_lista_comandos(resposta: str) -> List[Dict[str, Any]]:
    match = FINAL_JSON_REGEX.search(resposta)
    if not match:
        raise ValueError("Nenhum JSON encontrado no final.")
    parsed = json.loads(match.group("json"))
    comandos: List[Dict[str, Any]] = []
    for item in parsed:
        nome = item.get("comando")
        if nome in VALID_COMMANDS:
            comandos.append({"comando": nome, "ano_mes": item.get("ano_mes")})
    return comandos

def executar_comandos(lista: List[Dict[str, Any]]) -> List[Tuple[str, bool]]:
    resultados = []
    for cmd in lista:
        func = COMMAND_HANDLERS[cmd["comando"]]
        ok = func(cmd.get("ano_mes")) if "metas" in cmd["comando"] else func()
        resultados.append((cmd["comando"], ok))
    return resultados

def processar_texto_usuario(texto: str) -> Tuple[str, List[Tuple[str, bool]]]:
    resposta = interpretar_comando_groq(texto)
    try:
        comandos = extrair_lista_comandos(resposta)
    except Exception as e:
        print(f"[Erro parser] {e}")
        return resposta, []
    resultados = executar_comandos(comandos)
    return resposta, resultados

# Execução via terminal
if __name__ == "__main__":
    while True:
        txt = input("Você: ").strip()
        if txt.lower() in ["sair", "exit", "quit"]:
            break
        resp, cmds = processar_texto_usuario(txt)
        print("\n--- Resposta ---")
        print(resp)
        print("--- Execução ---")
        for c, ok in cmds:
            print(f"{c}: {'OK' if ok else 'FALHOU'}")
        print("=" * 50)
# === FIM ===