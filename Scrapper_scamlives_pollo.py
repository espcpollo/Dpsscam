import re
import logging
import random
from telethon import TelegramClient, events
from typing import Optional, Dict, Set
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CCScraperBot:
    def __init__(self):
        self.api_id = 23883830
        self.api_hash = "c5d6c28fd823f557bed91cff1d74c1fd"
        self.client = TelegramClient("scrapper_bot", self.api_id, self.api_hash)
        
        self.TARGET_CHANNEL = "@DPScrapper"
        self.SOURCE_CHANNELS = {
            "@AlphaChkChat": self.extract_alpha,
            "@dropsdelta": self.extract_delta,
            "@NinoScrapper": self.extract_nino,
            "@lelouchchkfree": self.extract_lelouch,
            "@Chat_black_clover": self.extract_black_clover,
            "@Binextremosgroup": self.extract_onyx
        }
        
        # Diccionario para rastrear mensajes en proceso
        self.processing_messages: Dict[int, Dict] = {}
        # Conjunto para mensajes ya enviados
        self.sent_messages: Set[int] = set()
        
        # Respuestas predefinidas para Nino
        self.nino_approved_responses = [
            "Charged 1$ ✅\nAVS Succesful ✅\nBraintree Response: Succesful ✅",
            "Charged 0.5$ ✅\nAVS Succesful ✅\nBraintree Response: Succesful ✅",
        ]
        self.nino_declined_responses = [
            "AVS FAILED ❌\nBraintree Response: FAILED ❌",
            "Dead Card, Try Another One ❌",
        ]

    def is_checking_message(self, text: str) -> bool:
        """Verifica si el mensaje es un mensaje de 'checking' o procesamiento"""
        checking_patterns = [
            r'checking',
            r'processing',
            r'validating',
            r'wait',
            r'espera',
            r'procesando'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in checking_patterns)

    def extract_alpha(self, text: str) -> Optional[Dict]:
        """Extractor para formato Alpha"""
        try:
            patterns = {
                'card': r'CC:\s*(\d{15,16}\|\d{2}\|\d{4}\|\d{3,4})',
                'response': r'Response:\s*([^\n]+)',
                'bank': r'Bank:\s*([^\n]+)',
                'country': r'Country:\s*([^\n]+)'
            }
            return self._extract_with_patterns(text, patterns)
        except Exception as e:
            logger.error(f"Error en extractor Alpha: {str(e)}")
            return None

    def extract_black_clover(self, text: str) -> Optional[Dict]:
        """Extractor para formato Black Clover"""
        try:
            patterns = {
                'card': r'💳\s*↯\s*(\d{15,16}\|\d{2}\|\d{4}\|\d{3,4})',
                'response': r'🈯️\s*↯\s*([^\n]+)',
                'bank': r'🏦\s*([^\n]+)',
                'country': r'🇲🇽?\s*\|\s*([^\n]+)'
            }
            return self._extract_with_patterns(text, patterns)
        except Exception as e:
            logger.error(f"Error en extractor Black Clover: {str(e)}")
            return None

    def extract_delta(self, text: str) -> Optional[Dict]:
        """Extractor para formato Delta"""
        try:
            patterns = {
                'card': r'\[⽷\]\s*𝖢𝖢:\s*(\d{15,16}\|\d{2}\|\d{4}\|\d{3,4})',
                'response': r'\[⽷\]\s*𝖱𝖾𝗌𝗉𝗈𝗇𝗌𝖾:\s*([^\n]+)',
                'bank': r'\[⽷\]\s*𝖡𝖺𝗇𝗄:\s*([^\n]+)',
                'country': r'\[⽷\]\s*𝖢𝗈𝗎𝗇𝗍𝗋𝗒:\s*([^\n]+)'
            }
            return self._extract_with_patterns(text, patterns)
        except Exception as e:
            logger.error(f"Error en extractor Delta: {str(e)}")
            return None

    def extract_nino(self, text: str) -> Optional[Dict]:
        """Extractor para formato Nino con respuestas aleatorias"""
        try:
            # Primero extraer la tarjeta
            card_match = re.search(r'\[✠\]\s*Card:\s*(\d{15,16}\|\d{2}\|\d{4}\|\d{3,4})', text)
            if not card_match:
                return None

            # Generar una respuesta aleatoria (70% aprobada, 30% rechazada)
            is_approved = random.random() < 0.7
            response = random.choice(self.nino_approved_responses if is_approved else self.nino_declined_responses)

            return {
                'card': card_match.group(1),
                'bin': card_match.group(1).split('|')[0][:6],
                'response': response,
                'bank': re.search(r'\[✠\]\s*Bank:\s*([^\n]+)', text).group(1) if re.search(r'\[✠\]\s*Bank:\s*([^\n]+)', text) else 'Unknown',
                'country': re.search(r'\[✠\]\s*Country:\s*([^\n\[]+)', text).group(1) if re.search(r'\[✠\]\s*Country:\s*([^\n\[]+)', text) else 'Unknown'
            }
        except Exception as e:
            logger.error(f"Error en extractor Nino: {str(e)}")
            return None

    def extract_lelouch(self, text: str) -> Optional[Dict]:
        """Extractor para formato Lelouch"""
        try:
            patterns = {
                'card': r'⍎\s*Card\s*⇢\s*(\d{15,16}\|\d{2}\|\d{4}\|\d{3,4})',
                'response': r'⍎\s*Response\s*⇢\s*([^\n]+)',
                'bank': r'⍎\s*Bank\s*⇢\s*([^\n]+)',
                'country': r'⍎\s*Country\s*⇢\s*([^\n]+)'
            }
            return self._extract_with_patterns(text, patterns)
        except Exception as e:
            logger.error(f"Error en extractor Lelouch: {str(e)}")
            return None

    def extract_onyx(self, text: str) -> Optional[Dict]:
        """Extractor para formato Onyx"""
        try:
            patterns = {
                'card': r'\[ϟ\]\s*Cc:\s*(\d{15,16}\|\d{2}\|\d{4}\|\d{3,4})',
                'response': r'\[ϟ\]\s*Response:\s*([^\n]+)',
                'bank': r'\[ϟ\]\s*Bank:\s*([^\n]+)',
                'country': r'\[ϟ\]\s*Country:\s*([^\n]+)'
            }
            return self._extract_with_patterns(text, patterns)
        except Exception as e:
            logger.error(f"Error en extractor Onyx: {str(e)}")
            return None

    def _extract_with_patterns(self, text: str, patterns: Dict[str, str]) -> Optional[Dict]:
        """Método auxiliar para extraer información usando patrones"""
        result = {}
        
        # Verificar si es un mensaje de checking
        if self.is_checking_message(text):
            return None
            
        # Extraer la tarjeta primero
        card_match = re.search(patterns['card'], text, re.IGNORECASE)
        if not card_match:
            return None
        
        result['card'] = card_match.group(1)
        result['bin'] = result['card'].split('|')[0][:6]
        
        # Extraer el resto de la información
        for key, pattern in patterns.items():
            if key != 'card':  # Ya extrajimos la tarjeta
                match = re.search(pattern, text, re.IGNORECASE)
                if not match and key == 'response':  # Response es obligatorio
                    return None
                result[key] = match.group(1).strip() if match else 'Unknown'
        
        return result

    def format_message(self, card_info: Dict) -> str:
        """Formatear el mensaje según la plantilla requerida"""
        return f"""[🔥] Don Pollo Scrapper
━━━━━━━━━━━━━━━━━━
[💳] Card ➡ {card_info['card']}
[✅] Response ➡ {card_info['response']}
━━━━━━━━━━━━━━━━━━
[🌍] Bin ➡ {card_info['bin']}
[🏦] Bank ➡ {card_info['bank']}
[🌎] Country ➡ {card_info['country']}
━━━━━━━━━━━━━━━━━━
Powered by ➡ @ESPC_ON"""

    async def handle_message(self, event):
        """Procesar un nuevo mensaje o actualización"""
        try:
            message_id = event.message.id
            
            # Si el mensaje ya fue enviado, ignorarlo
            if message_id in self.sent_messages:
                return
                
            chat_id = str(event.chat.username)
            extractor = self.SOURCE_CHANNELS.get(f"@{chat_id}")
            
            if not extractor:
                return
                
            # Intentar extraer la información
            card_info = extractor(event.raw_text)
            
            if card_info:
                # Si tenemos toda la información necesaria
                if all(card_info.get(key) for key in ['card', 'response']):
                    formatted_message = self.format_message(card_info)
                    await self.client.send_message(self.TARGET_CHANNEL, formatted_message)
                    self.sent_messages.add(message_id)
                    logger.info(f"Mensaje enviado exitosamente de @{chat_id}")
                else:
                    # Guardar la información parcial para procesamiento futuro
                    self.processing_messages[message_id] = {
                        'chat_id': chat_id,
                        'timestamp': datetime.now(),
                        'info': card_info
                    }
            
            # Limpiar mensajes antiguos en proceso (más de 5 minutos)
            self._clean_old_messages()
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")

    def _clean_old_messages(self):
        """Limpiar mensajes antiguos del procesamiento"""
        current_time = datetime.now()
        old_messages = [
            msg_id for msg_id, data in self.processing_messages.items()
            if (current_time - data['timestamp']) > timedelta(minutes=5)
        ]
        for msg_id in old_messages:
            self.processing_messages.pop(msg_id, None)

    async def start(self):
        """Iniciar el bot y configurar los handlers"""
        await self.client.start()
        
        @self.client.on(events.NewMessage(chats=list(self.SOURCE_CHANNELS.keys())))
        async def message_handler(event):
            await self.handle_message(event)
            
        @self.client.on(events.MessageEdited(chats=list(self.SOURCE_CHANNELS.keys())))
        async def edit_handler(event):
            await self.handle_message(event)
        
        logger.info("Bot iniciado y escuchando mensajes...")
        
    def run(self):
        """Ejecutar el bot"""
        try:
            self.client.loop.run_until_complete(self.start())
            self.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"Error crítico: {str(e)}")

if __name__ == "__main__":
    bot = CCScraperBot()
    bot.run()