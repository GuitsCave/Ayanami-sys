import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from telegram import Update

# Importa a lógica da IA
from rei import processar_texto_usuario

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN_REI")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN não encontrado no .env")

# =========================================================
# Helpers para formatar o retorno pós-execução
# =========================================================
def formatar_resultados(resultados):
    if not resultados:
        return "⚠️ Não consegui identificar nenhum comando executável dessa vez."
    linhas = []
    for nome, ok in resultados:
        if ok:
            linhas.append(f"✅ `{nome}` concluído com sucesso.")
        else:
            linhas.append(f"❌ `{nome}` falhou.")
    return "\n".join(linhas)

# =========================================================
# Handlers de comandos básicos
# =========================================================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Eu sou a REI!. "
        "É só me pedir em linguagem natural: *\"atualiza os produtos\"*, "
        "*\"insere as metas de 2025-08 e depois sincroniza o rls\"*.\n\n"
        "Sempre que eu responder, no final executo os comandos pra você.",
        parse_mode="Markdown"
    )

async def cmd_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos que entendo:\n"
        "- insert_metas (ex: 'insere as metas de 2025-07')\n"
        "- delete_metas\n"
        "- update_metas\n"
        "- atualiza_clientes\n"
        "- atualiza_produtos\n"
        "- atualiza_regional\n"
        "- sincroniza_rls\n\n"
        "Pode combinar: 'atualiza clientes e depois produtos'."
    )

# =========================================================
# Handler principal de mensagens
# =========================================================
async def handler_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Passo 1: processa com a IA (resposta natural + execução)
    resposta_yuki, resultados = processar_texto_usuario(user_text)

    # Passo 2: envia a resposta natural ORIGINAL (que inclui o JSON ao final)
    # Se quiser esconder o JSON do usuário, podemos limpar, mas por enquanto mantemos.
    # await update.message.reply_text(resposta_yuki)
    resposta_sem_json = resposta_yuki.rsplit('[', 1)[0].strip()
    await update.message.reply_text(resposta_sem_json)

    # Passo 3: envia um resumo de execução (se quiser, pode omitir; já aparece nos prints do servidor)
    resumo = formatar_resultados(resultados)
    await update.message.reply_text(resumo, parse_mode="Markdown")

# =========================================================
# Inicialização do bot
# =========================================================
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ajuda", cmd_ajuda))

    # Mensagens de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler_texto))

    print("🤖 REI está operando! (Ctrl+C para parar)")
    app.run_polling()

if __name__ == "__main__":
    # Em caso de rodar em ambientes async (ex: notebooks), garantir execução adequada
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrando REI. Até mais!")