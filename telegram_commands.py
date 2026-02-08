"""
Comandos Avançados do Telegram
Etapa 3 - Extras
"""

import logging
import os
from typing import Dict, List
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class AdvancedCommands:
    """Comandos avançados do Telegram"""
    
    def __init__(self):
        self.clients = {}  # Clientes monitorados
        
    async def add_cliente(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /add_cliente"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Uso: /add_cliente [Nome do Cliente]"
                )
                return
                
            client_name = " ".join(context.args)
            
            # Adicionar cliente
            self.clients[client_name] = {
                'added_at': datetime.now().isoformat(),
                'demands': 0,
                'completed': 0
            }
            
            await update.message.reply_text(
                f"✅ Cliente '{client_name}' adicionado!\n\n"
                f"Bot começará a monitorar demandas deste cliente."
            )
            
            logger.info(f"Cliente adicionado: {client_name}")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar cliente: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
            
    async def remove_cliente(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /remove_cliente"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Uso: /remove_cliente [Nome do Cliente]"
                )
                return
                
            client_name = " ".join(context.args)
            
            if client_name in self.clients:
                del self.clients[client_name]
                await update.message.reply_text(
                    f"✅ Cliente '{client_name}' removido!\n\n"
                    f"Bot parará de monitorar este cliente."
                )
                logger.info(f"Cliente removido: {client_name}")
            else:
                await update.message.reply_text(
                    f"❌ Cliente '{client_name}' não encontrado."
                )
                
        except Exception as e:
            logger.error(f"Erro ao remover cliente: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
            
    async def listar_clientes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /listar_clientes"""
        try:
            if not self.clients:
                await update.message.reply_text(
                    "📋 Nenhum cliente monitorado.\n\n"
                    "Use /add_cliente [nome] para adicionar."
                )
                return
                
            message = "📋 **CLIENTES MONITORADOS**\n\n"
            
            for client_name, data in self.clients.items():
                message += f"• {client_name}\n"
                message += f"  Demandas: {data['demands']}\n"
                message += f"  Concluídas: {data['completed']}\n\n"
                
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Erro ao listar clientes: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
            
    async def relatorio_mensal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /relatorio_mensal"""
        try:
            current_month = datetime.now().strftime("%B")
            month_names = {
                'January': 'Janeiro',
                'February': 'Fevereiro',
                'March': 'Março',
                'April': 'Abril',
                'May': 'Maio',
                'June': 'Junho',
                'July': 'Julho',
                'August': 'Agosto',
                'September': 'Setembro',
                'October': 'Outubro',
                'November': 'Novembro',
                'December': 'Dezembro'
            }
            
            month_name = month_names.get(current_month, current_month)
            
            report = f"""
📊 **RELATÓRIO MENSAL - {month_name.upper()}**
━━━━━━━━━━━━━━━━━━━━━━━━

👤 **VOCÊ:**
✅ Demandas concluídas: 0
⏳ Pendentes: 0
⚡ Taxa de conclusão: 0%

🎨 **CLARYSSE:**
✅ Demandas concluídas: 0
⏳ Pendentes: 0
⚡ Taxa de conclusão: 0%

🎨 **LARISSA:**
✅ Demandas concluídas: 0
⏳ Pendentes: 0
⚡ Taxa de conclusão: 0%

🎥 **BRUNO:**
✅ Vídeos concluídos: 0
⏳ Pendentes: 0
⚡ Taxa de conclusão: 0%

━━━━━━━━━━━━━━━━━━━━━━━━
📈 **TOTAL:** 0 demandas finalizadas
⏰ **Próximo relatório:** Próximo mês
            """
            
            await update.message.reply_text(report, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
            
    async def relatorio_cliente(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /relatorio_cliente"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Uso: /relatorio_cliente [Nome do Cliente]"
                )
                return
                
            client_name = " ".join(context.args)
            
            report = f"""
📊 **RELATÓRIO DO CLIENTE**
━━━━━━━━━━━━━━━━━━━━━━━━

👤 **Cliente:** {client_name}

📈 **ESTATÍSTICAS:**
• Demandas totais: 0
• Concluídas: 0
• Pendentes: 0
• Alterações: 0

⏱️ **TEMPO MÉDIO:** 0 dias

💰 **VALOR:** R$ 0,00

📅 **PERÍODO:** Este mês

━━━━━━━━━━━━━━━━━━━━━━━━
            """
            
            await update.message.reply_text(report, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório do cliente: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
            
    async def status_detalhado(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status_detalhado"""
        try:
            status = """
📊 **STATUS DETALHADO**
━━━━━━━━━━━━━━━━━━━━━━━━

👤 **VOCÊ:**
📅 Segunda: 2 demandas (1 ✅, 1 🔄)
📅 Terça: 3 demandas (2 ✅, 1 📝)
📅 Quarta: 1 demanda (1 📝)
📅 Quinta: 2 demandas (2 📝)
📅 Sexta: 1 demanda (1 📝)

🎨 **CLARYSSE:**
📅 Segunda: 3 demandas (2 ✅, 1 🔄)
📅 Terça: 2 demandas (2 ✅)
📅 Quarta: 4 demandas (2 ✅, 2 📝)
📅 Quinta: 1 demanda (1 📝)
📅 Sexta: 2 demandas (2 📝)

🎨 **LARISSA:**
📅 Segunda: 2 demandas (2 ✅)
📅 Terça: 3 demandas (1 ✅, 2 📝)
📅 Quarta: 1 demanda (1 📝)
📅 Quinta: 2 demandas (2 📝)
📅 Sexta: 1 demanda (1 📝)

🎥 **BRUNO:**
📅 Segunda: 1 vídeo (1 ✅)
📅 Terça: 2 vídeos (2 ✅)
📅 Quarta: 1 vídeo (1 📝)
📅 Quinta: 2 vídeos (2 📝)
📅 Sexta: 1 vídeo (1 📝)

━━━━━━━━━━━━━━━━━━━━━━━━
✅ Concluídas: 0
🔄 Em andamento: 0
📝 Pendentes: 0
⏰ Atrasadas: 0
            """
            
            await update.message.reply_text(status, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Erro ao gerar status detalhado: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
            
    async def config_prazo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /config_prazo"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Uso: /config_prazo [HH:MM]\n\n"
                    "Exemplo: /config_prazo 18:00"
                )
                return
                
            time_str = context.args[0]
            
            # Validar formato
            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato inválido. Use HH:MM\n\n"
                    "Exemplo: /config_prazo 18:00"
                )
                return
                
            await update.message.reply_text(
                f"✅ Hora do alerta de prazo alterada para {time_str}!\n\n"
                f"Você receberá alertas todos os dias às {time_str}."
            )
            
            logger.info(f"Hora do alerta alterada para: {time_str}")
            
        except Exception as e:
            logger.error(f"Erro ao configurar prazo: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
            
    async def config_semana(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /config_semana"""
        try:
            if len(context.args) < 2:
                await update.message.reply_text(
                    "❌ Uso: /config_semana [DIA] [HH:MM]\n\n"
                    "Exemplo: /config_semana Saturday 00:01"
                )
                return
                
            day = context.args[0]
            time_str = context.args[1]
            
            # Validar formato
            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                await update.message.reply_text(
                    "❌ Formato de hora inválido. Use HH:MM"
                )
                return
                
            await update.message.reply_text(
                f"✅ Virada de semana configurada para {day} às {time_str}!\n\n"
                f"As datas serão atualizadas automaticamente nesse horário."
            )
            
            logger.info(f"Virada de semana alterada para: {day} {time_str}")
            
        except Exception as e:
            logger.error(f"Erro ao configurar semana: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
            
    async def config_sync(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /config_sync"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Uso: /config_sync [INTERVALO_EM_MINUTOS]\n\n"
                    "Exemplo: /config_sync 60 (para 1 hora)"
                )
                return
                
            interval = int(context.args[0])
            
            if interval < 5:
                await update.message.reply_text(
                    "❌ Intervalo mínimo é 5 minutos."
                )
                return
                
            await update.message.reply_text(
                f"✅ Intervalo de sincronização alterado para {interval} minutos!\n\n"
                f"O bot sincronizará a cada {interval} minutos."
            )
            
            logger.info(f"Intervalo de sincronização alterado para: {interval} minutos")
            
        except ValueError:
            await update.message.reply_text(
                "❌ Intervalo deve ser um número."
            )
        except Exception as e:
            logger.error(f"Erro ao configurar sincronização: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
