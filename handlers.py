async def send_alteration(bot, chat_id, demand_data):
    client = demand_data["client"]
    demanda = demand_data["demanda"]
    copy_text = demand_data["copy"]
    link = demand_data["link"]

    text = f"🔄 ALTERAÇÃO DETECTADA!\n\n👤 Cliente: {client}\n📝 Demanda original: {demanda}\n\n💬 O que mudou:\n{copy_text}\n\n🔗 Link: {link}"

    keyboard = [
        [InlineKeyboardButton("Designer 1", callback_data="alter_designer1")],
        [InlineKeyboardButton("Designer 2", callback_data="alter_designer2")],
        [InlineKeyboardButton("✅ Eu faço", callback_data="alter_me")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

# No button_handler, adicione lógica para 'alter_*' similar à de assign, mas mova card no Trello para "Alterações"
