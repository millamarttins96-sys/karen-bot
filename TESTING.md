# 🧪 Guia de Testes e Validação

## Visão Geral

Este documento descreve como testar todas as funcionalidades do bot em cada etapa de desenvolvimento.

## Etapa 1: Notificações e Distribuição Básica

### 1.1 Monitoramento do Notion

**Objetivo**: Verificar se o bot detecta novas demandas no Notion

**Passos**:
1. Adicione uma nova demanda no Notion (em uma das 3 páginas monitoradas)
2. Aguarde até 1 hora (intervalo de sincronização)
3. Verifique se recebeu notificação no Telegram

**Resultado Esperado**:
- ✅ Notificação recebida no Telegram
- ✅ Informações corretas (cliente, título, copy)
- ✅ Botões de distribuição funcionando

**Logs**:
```bash
tail -f logs/bot.log | grep "Notion"
```

### 1.2 Monitoramento do Trello

**Objetivo**: Verificar se o bot detecta novos cards no Trello

**Passos**:
1. Crie um novo card em um dos quadros monitorados
2. Adicione a etiqueta "AGUARDANDO DESIGN"
3. Aguarde até 5 minutos
4. Verifique se recebeu notificação

**Resultado Esperado**:
- ✅ Notificação recebida
- ✅ Etiqueta detectada corretamente
- ✅ Informações do card exibidas

**Logs**:
```bash
tail -f logs/bot.log | grep "Trello"
```

### 1.3 Distribuição para Designer

**Objetivo**: Testar fluxo completo de distribuição

**Passos**:
1. Receba uma notificação de nova demanda
2. Clique em [🎨 Design]
3. Escolha um designer (Clarysse ou Larissa)
4. Escolha uma data de entrega
5. Verifique se o card foi criado no Trello do designer

**Resultado Esperado**:
- ✅ Card criado com título correto
- ✅ Descrição com copy completa
- ✅ Data de entrega configurada
- ✅ Designer atribuída
- ✅ Labels adicionadas

**Verificação**:
```bash
# Abra o Trello do designer e verifique
https://trello.com/b/[board_id]/[board_name]
```

### 1.4 Distribuição para Você

**Objetivo**: Testar fluxo de distribuição para você

**Passos**:
1. Receba uma notificação
2. Clique em [✅ Fazer Eu]
3. Escolha um dia da semana
4. Verifique se o card foi criado em "Minhas Demandas"

**Resultado Esperado**:
- ✅ Card criado no dia escolhido
- ✅ Informações corretas
- ✅ Pronto para você executar

### 1.5 Sistema de Semanas

**Objetivo**: Testar virada de semana automática

**Passos**:
1. Aguarde até Sábado 00:01 (ou execute `/virar_semana` manualmente)
2. Verifique se as datas foram atualizadas
3. Verifique se recebeu relatório

**Resultado Esperado**:
- ✅ Nomes das colunas atualizados com novas datas
- ✅ Relatório enviado no Telegram
- ✅ Cards não concluídos movidos corretamente

**Teste Manual**:
```bash
# Envie comando no Telegram
/virar_semana
```

## Etapa 2: Automações

### 2.1 Sistema de Aprovação

**Objetivo**: Testar fluxo de aprovação de demandas

**Passos**:
1. Mova um card para "Pronto" em um quadro de designer
2. Aguarde até 5 minutos
3. Receba notificação no Telegram com preview dos arquivos
4. Clique em [✅ Aprovar tudo]

**Resultado Esperado**:
- ✅ Notificação recebida com arquivos
- ✅ Botões de aprovação funcionando
- ✅ Confirmação após aprovação

### 2.2 Upload para Google Drive

**Objetivo**: Testar upload automático

**Passos**:
1. Aprove um card (conforme 2.1)
2. Bot faz download dos arquivos do Trello
3. Bot cria pasta no Drive com estrutura correta
4. Bot faz upload dos arquivos
5. Receba link do Drive no Telegram

**Resultado Esperado**:
- ✅ Pasta criada: Cliente/Mês/Demanda
- ✅ Arquivos enviados sem ZIP
- ✅ Link do Drive recebido
- ✅ Acesso confirmado

**Verificação**:
```bash
# Abra o link do Drive e verifique
https://drive.google.com/drive/folders/[folder_id]
```

### 2.3 Sistema de Folgas

**Objetivo**: Testar detecção de dias vazios

**Passos**:
1. Distribua demandas deixando um dia vazio para um designer
2. Bot detecta dia vazio
3. Bot pergunta: "Ela vai ter folga nesse dia?"
4. Clique em [✅ Sim, folga]

**Resultado Esperado**:
- ✅ Pergunta recebida
- ✅ Card de folga criado
- ✅ Label de folga adicionada
- ✅ Dia bloqueado para distribuição

### 2.4 Detecção de Alterações

**Objetivo**: Testar detecção inteligente de alterações

**Passos**:
1. Crie um card com etiqueta "ALTERAÇÃO" no Trello
2. Aguarde até 5 minutos
3. Bot detecta alteração
4. Bot move card para coluna "Alterações"
5. Bot comenta mencionando designer

**Resultado Esperado**:
- ✅ Card movido para "Alterações"
- ✅ Comentário adicionado
- ✅ Designer mencionada
- ✅ Notificação enviada

## Etapa 3: Extras

### 3.1 Comandos Avançados

**Objetivo**: Testar comandos do Telegram

**Passos**:
1. Envie `/add_cliente Novo Cliente`
2. Envie `/listar_clientes`
3. Envie `/relatorio_mensal`
4. Envie `/status_detalhado`

**Resultado Esperado**:
- ✅ Cliente adicionado
- ✅ Lista de clientes exibida
- ✅ Relatório gerado
- ✅ Status detalhado exibido

### 3.2 Dashboard Web

**Objetivo**: Testar acesso ao dashboard

**Passos**:
1. Inicie o dashboard: `python etapa3/dashboard_app.py`
2. Acesse: `http://localhost:5000`
3. Verifique as 4 abas (Você, Clarysse, Larissa, Bruno)
4. Verifique se as métricas estão atualizadas

**Resultado Esperado**:
- ✅ Dashboard carrega sem erros
- ✅ 4 abas visíveis
- ✅ Dados exibidos corretamente
- ✅ Responsivo no celular

### 3.3 Análise de Produtividade

**Objetivo**: Testar geração de insights com IA

**Passos**:
1. Aguarde segunda-feira às 09:00 (ou simule)
2. Receba relatório semanal no Telegram
3. Verifique insights gerados

**Resultado Esperado**:
- ✅ Relatório recebido
- ✅ Insights relevantes
- ✅ Métricas corretas
- ✅ Recomendações úteis

### 3.4 Alertas de Prazo

**Objetivo**: Testar alertas automáticos

**Passos**:
1. Configure hora do alerta: `/config_prazo 17:30`
2. Crie demandas com vencimento para hoje
3. Aguarde 17:30
4. Receba alerta no Telegram

**Resultado Esperado**:
- ✅ Alerta recebido na hora correta
- ✅ Demandas atrasadas listadas
- ✅ Botões de ação funcionando
- ✅ Notificação clara

## Testes de Integração

### Teste Completo: Fluxo End-to-End

**Objetivo**: Testar fluxo completo da demanda

**Passos**:
1. Adicione demanda no Notion
2. Bot detecta e notifica
3. Você distribui para designer
4. Designer recebe no Trello
5. Designer executa e move para "Pronto"
6. Bot detecta e notifica
7. Você aprova
8. Bot faz upload no Drive
9. Você recebe link

**Resultado Esperado**:
- ✅ Fluxo completo sem erros
- ✅ Todas as notificações recebidas
- ✅ Arquivo no Drive
- ✅ Tempo total < 10 minutos

### Teste de Carga

**Objetivo**: Testar bot com múltiplas demandas

**Passos**:
1. Crie 10 demandas no Notion
2. Crie 10 cards no Trello
3. Verifique se bot processa todas
4. Verifique performance

**Resultado Esperado**:
- ✅ Todas as demandas processadas
- ✅ Sem erros ou travamentos
- ✅ Tempo de resposta aceitável

### Teste de Resiliência

**Objetivo**: Testar bot com falhas de rede

**Passos**:
1. Desconecte internet por 30 segundos
2. Reconecte
3. Verifique se bot continua funcionando
4. Verifique se sincroniza corretamente

**Resultado Esperado**:
- ✅ Bot se recupera automaticamente
- ✅ Nenhuma demanda perdida
- ✅ Sincronização completa

## Checklist de Validação

### Funcionalidades Críticas

- [ ] Monitoramento Notion funcionando
- [ ] Monitoramento Trello funcionando
- [ ] Notificações Telegram recebidas
- [ ] Distribuição para designers funcionando
- [ ] Distribuição para você funcionando
- [ ] Virada de semana automática funcionando
- [ ] Aprovação de demandas funcionando
- [ ] Upload Google Drive funcionando
- [ ] Sistema de folgas funcionando
- [ ] Alertas de prazo funcionando

### Funcionalidades Secundárias

- [ ] Dashboard Web acessível
- [ ] Análise de IA gerando insights
- [ ] Comandos avançados funcionando
- [ ] Logs sendo gerados corretamente
- [ ] Tratamento de erros funcionando

### Performance

- [ ] Tempo de resposta < 5 segundos
- [ ] Sincronização < 1 minuto
- [ ] Upload < 2 minutos
- [ ] Dashboard carrega < 3 segundos

### Segurança

- [ ] Credenciais não expostas em logs
- [ ] `.env` não commitado
- [ ] Acesso ao dashboard protegido
- [ ] Dados sensíveis encriptados

## Relatório de Testes

Após completar todos os testes, preencha o relatório:

```markdown
# Relatório de Testes - [Data]

## Etapa 1: Notificações e Distribuição
- Notion: ✅ / ❌
- Trello: ✅ / ❌
- Distribuição: ✅ / ❌
- Semanas: ✅ / ❌

## Etapa 2: Automações
- Aprovação: ✅ / ❌
- Google Drive: ✅ / ❌
- Folgas: ✅ / ❌
- Alterações: ✅ / ❌

## Etapa 3: Extras
- Comandos: ✅ / ❌
- Dashboard: ✅ / ❌
- IA: ✅ / ❌
- Alertas: ✅ / ❌

## Problemas Encontrados
- [Problema 1]
- [Problema 2]

## Recomendações
- [Recomendação 1]
- [Recomendação 2]
```

## Troubleshooting

### Bot não inicia

```bash
# Verificar erros
python etapa1/main.py

# Verificar logs
tail -f logs/bot.log
```

### Notificações não chegam

```bash
# Verificar token
echo $TELEGRAM_TOKEN

# Verificar chat ID
echo $TELEGRAM_CHAT_ID
```

### Trello não sincroniza

```bash
# Verificar credenciais
echo $TRELLO_API_KEY
echo $TRELLO_TOKEN

# Verificar nomes dos quadros
# Devem estar exatos
```

### Google Drive não funciona

```bash
# Verificar arquivo de credenciais
ls -la config/service_account.json

# Verificar permissões
# Pasta deve estar compartilhada com o email da Service Account
```

## Suporte

Para reportar problemas encontrados durante os testes, abra uma issue no GitHub com:

- Descrição do problema
- Passos para reproduzir
- Logs relevantes
- Ambiente (SO, versão Python, etc)

---

**Desenvolvido com ❤️ para garantir qualidade**
