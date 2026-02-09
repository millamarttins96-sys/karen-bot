def handle_alteration_trello(assignee, demand_data, due_date):
    # Similar a create_trello_card, mas:
    # 1. Busca card existente por título (cliente) e keywords na descrição
    board_id = TRELLO_BOARDS[assignee]
    board = trello.get_board(board_id)
    cards = board.open_cards()  # Ou filtre por listas
    matching_card = None
    for card in cards:
        if demand_data['client'] in card.name and any(word in card.desc for word in demand_data['demanda'].split()):
            matching_card = card
            break

    if matching_card:
        # Move para lista "🔄 Alterações"
        alteration_list = next((l for l in board.list_lists() if "Alterações" in l.name), None)
        if alteration_list:
            matching_card.change_list(alteration_list.id)
        # Adiciona comentário com alteração
        matching_card.comment(f"🔄 ALTERAÇÃO: {demand_data['copy']}\nNova entrega: {due_date.strftime('%d/%m/%Y')}")
        # Atualiza due date
        matching_card.set_due(due_date)
