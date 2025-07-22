# 🤖 REI — Agente Inteligente para Automação de Rotinas

**REI** (Referência, Execução e Inteligência) é uma IA local criada para interpretar comandos de texto em linguagem natural e automatizar rotinas do dia a dia com eficiência e discrição.

Inspirada na personagem **Rei Ayanami** do anime *Neon Genesis Evangelion*, REI possui uma personalidade calma, lógica e respeitosa — respondendo de forma clara, direta e acolhedora.

---

## 🧠 Funcionalidades

REI reconhece e executa os seguintes comandos:

- `insert_metas` — Requer parâmetro `ano_mes`
- `delete_metas` — Requer `ano_mes`
- `update_metas` — Requer `ano_mes`
- `atualiza_clientes`
- `atualiza_produtos`
- `atualiza_regional`
- `sincroniza_rls`
- `atualiza_carro` *(exemplo adicional)*

---

## 💬 Interação com o Usuário

REI interpreta mensagens em português do Brasil e responde com um resumo da ação, sempre finalizando com um JSON para execução da automação.

### 📝 Exemplo

**Entrada do usuário:**
> Por favor, atualize os clientes e remova as metas de 2025-05.

**Resposta da REI:**
```json
[
  {"comando": "atualiza_clientes"},
  {"comando": "delete_metas", "ano_mes": "2025-05"}
]
