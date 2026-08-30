import discord
import asyncio
import random
import os
import gc
import aiohttp
import psutil
from datetime import datetime, timezone, timedelta
from threading import Thread
from flask import Flask 
import time as time_module
from io import BytesIO

# --- KEEPALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "ECHO QTY CORE ACTIVE"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURATION (TOKENS FROM ENVIRONMENT) ---
# Get tokens from environment variable "TOKENS" (comma-separated)
TOKENS = os.environ.get("TOKENS", "").split(",")
TOKENS = [t.strip() for t in TOKENS if t.strip() and "TOKEN" not in t]  # filter out placeholders

# If no tokens in env, fallback to hardcoded (but we recommend using env)
if not TOKENS:
    # Keep your old tokens here ONLY for backup – but better to rely on env
    TOKENS = [
        # your tokens here – but we recommend removing them for safety
    ]

SUDO_USERS = [1442911002130907146] 
PREFIX = "!"

# --- Bot Management Globals ---
SELF_REACT_EMOJI = None
lock_targets = {}
lock_messages = {}
react_targets = {}
active_bots = {}          # user_id -> {"name": str, "status": "online"/"offline"}
token_to_user = {}        # token -> user_id
locked_pfp = {}
start_time = None
global_react_target = None
copycat_mode = set()
purge_from_ids = {}
swipe_targets = {}

# --- FULLY MERGED DATA LISTS (unchanged) ---
REX_LIST = [
    "चुदाई Kha 😂❤️", "उठक बैठक लगा 😏🔥", "तेरी माँ चोदू 😍😍", "ओय कमजोर 🤢🤢", 
    "लंड चूस 🥱🤍➿", "पिल्लै 🐕‍", "😱 arey 😉 ye 🤡 kaise 😋 kiya 😏 re 😁 teri 😊 maa 😍 randy 😭100% 😂",
    "कमजोर टट्टा", "👈🏻👆🏻🖖🏻👇🏻🤲🏻👉🏻🤏🏻 Idr Udr Jidr Bhi Dekhega Teri Randi Maa Dikhegi",
    " 𝘽𝙀𝙏𝘼 🤢᭄᭄᭄᭄ 🌟 𝙇𝙐𝙉𝘿 𝘾𝙃𝙐𝙎 🤪᭄᭄", "मदरचोद 🤮🤮", "ro 🤣🤣", "रंडी", "चुप tmr 😒😂",
    "Acha Beta ? Koi Na Mai Teri माँ Coduga 😹💥💯", "चुदकड़", "कमजोर पिल्ले 🤮👞", "Chup Rndyce ⁉", 
    "Tmkc Mein Mist Breathing ☁", "Teri माँ margyi 😂😂😂", "Teri Maa चोदू If Yes Then Reply To My Message 😂😂💯💯",
    "चल तेरी माँ की चुत 🥵🥵", "Tera बाप Rex 🗿🌙💯💯", "Chal Tmkb Me Ghuss Ke Nanga Kruuu 🦈🦈",
    "🔥ꪻꫀ᥅ﺃ ꪑꪖꪖ ꪗꪖꫝꪖ ᥴꪊᦔꪻﺃ ꫝꫀꫀ 💢", "🧬Tmkc random 🤢🤢🖕🏻🖕🏻🖕🏻🧬",
    "𝘼𝙕 𝙉𝙄𝘾𝐇𝙀 𝙍𝙔𝙉𝘿𝙔 𝙆𝙀 𝘽𝘾𝘾𝐇𝐄 🗞️🗞️", "Itna codunga ki 10 din tak tryma hag bhi nhi payegi rndice 🤢🤢🔥🔥🔥",
    "(👑) 𝐁𝐎𝐋 𝐑𝐄𝐗 𝐆𝐀𝐖𝐃 𝐊𝐈 𝐉𝐀𝐈 𝐇𝐎 (👑)", "🔥Likhna sikh low lvl rndy ᛕꪊꪻꪻﺃ ᛕꫀꫀ ᜣﺃꪶꪶꫀ ꪻꪑᛕᥴ 🤢👞👞🔥",
    "Dekh tyri ma sod ke bhgta hua main 🙄😁 👉🏻🏃🏃🏃🏃🏃🏃🏃", "tyri ma chamiya gulaati mrke dikha 🤢🔥😂",
    "Are beta sun पंखा chalu kar तेरी maa ne पाद मारी 🫢🔥😝😦", "song bejhkr tyri maike bosrey mey disco krega cya😅",
    "𝑚𝑎𝑟𝑘𝑒𝑡 𝑠𝑒 𝑙𝑎𝑦𝑎 𝑝𝑎𝑝ི𝑡𝑎 ⚢︎𝒕𝒆𝒓𝒊 𝒎𝒂 𝒌𝒊 𝒄𝒖𝒕 𝒎𝒂𝒓𝒂 𝒄𝒉𝒊𝒕𝒂 🤪🫏💢🎀", "आवाज नीचे कर pille औकात अनुसार बोला kar 🤢🤢🔥",
    "tery buddhi ma ce mu pr mukke mrke गूंगी bnake sodunga 🤢👊🏿💔", "tery ma sudce switch off hogyiss 😈 balle balle 😝✌🔥",
    "tery ma takly भंगी rdy 🤲🔥🤲🔥🤲", "𝘈𝘣𝘦 𝘙𝘥𝘺 𝘒𝘦 पिल्ले 𝘈𝘱𝘯𝘪 𝘔𝘢 𝘒𝘰 𝘎𝘢𝘭𝘪𝘺𝘢 𝘏𝘪 𝘒𝘩𝘪𝘭𝘷𝘢𝘵𝘢 𝘙𝘢𝘩𝘦𝘨𝘢 𝘊𝘺𝘢 𝘏𝘶𝘮𝘴𝘩𝘢 ✌🏻🤢🤣😂💯🔥",
    "tery ma potty pessab🔥😖🔥ᴀɪ✯", "𝘊𝘩𝘢ʟ 𝘵𝘦𝘳𝘪 𝘣𝘩𝘯 𝘬𝘢𝘢 𝘣𝘰𝘴𝘥𝘢 😝🤢✌🏿", "𝘛𝘌𝘙𝘐 𝘔𝘈 𝘒𝘙𝘌 𝘊𝘏𝘈𝘐𝘠𝘈 𝘊𝘏𝘈𝘐𝘠𝘈 🤢👌🏿",
    "𝘾𝙃𝘼𝙇 𝙆𝙐𝙏𝙄𝙔𝙀 𝙎𝘼𝙇𝘼𝙈𝙄 𝙏𝙃𝙊𝙆 👏🏿🔥👏🏿🔥", "❤️𝘛𝘦𝘳𝘪🩵 𝘮𝘢𝘢 🧡𝘬𝘰💚 𝘦𝘴𝘦 🖤𝘤𝘰𝘥𝑎🖤 𝘵𝘩𝑎🖤 𝘥𝑒𝑘𝘩💜 𝘪𝘥𝘩𝘢𝘳 🤍𝘣𝘩𝘦𝘯𝘨𝘦🩷",
    "𝘾𝙃𝘼𝙇 𝙍𝙉𝘿𝙄𝙆𝙀 𝙐𝙏𝙃𝘼𝙆 𝘽𝙀𝙏𝙃𝘼𝙆 𝙇𝘼𝙂𝘼😁🔥"
]

ENG_LIST = [
    "𝘽𝘼𝙇𝘿 𝙉𝙄𝙂𝙂𝘼", "𝙏𝙐𝙁𝙁", "𝙎𝙔𝘽𝘼𝙐", "𝘾𝙍𝙔 𝙈𝙊𝙍𝙀",
    "𝙁𝙐𝘾𝙆 𝙐𝙍 𝙈𝙊𝙈𝙎 𝙂𝙍𝘼𝙑𝙀", "𝙉𝙄𝙂𝙂𝘼", "𝘽𝙄𝙏𝘾𝙃 𝘼𝙎𝙎 𝙐𝙋",
    "𝘼𝙐𝙏𝙄𝙎𝙈 𝙈𝙊𝙉𝙆𝙀𝙔", "𝙐𝙍 𝙎𝙄𝙎 𝘽𝙄𝙏𝘾𝙃", "𝙏𝙃𝙄𝙉 𝘼𝙎𝙎",
    "𝙒𝙀𝙄𝙍𝘿 𝘼𝙎𝙎", "𝘾𝙍𝙀𝙀𝙋 𝙉𝙄𝙂𝙂𝘼", "𝙆𝙔𝙎 𝙐𝙉𝘾",
    "𝙎𝙔𝙁𝙈", "𝙈𝙊𝙏𝙃𝙀𝙍𝙁𝘾𝙆𝙍", "𝙎𝙇𝙐𝙏𝙏𝙔 𝘼𝙎𝙎",
    "𝘼 𝙏𝙍𝘼𝙎𝙃 𝙄𝙎 𝙈𝙊𝙍𝙀 𝙐𝙎𝙀𝙁𝙐𝙇 𝙏𝙃𝘼𝙉 𝙐", "𝘿𝙍𝙄𝙉𝙆 𝙐𝙍𝙄𝙉𝙀 𝙏𝙒𝙄𝙉", "𝙇𝙊𝙒 𝙎𝙋𝙀𝘾𝙄𝙀𝙎"
]

REX_SPAM_LIST = ["𑁍ࠬܓ<🩷>ʟᴀɴᴅ ᴄʜᴏᴏꜱ ɴᴏʀᴍɪᴇ ℘✩₊˚.⋆🕸️", "𑁍ࠬܓ<💜>ᴄʜᴜᴅ ᴊᴀ ɴᴏʀᴍɪᴇ ℘✩₊˚.⋆👾", "𑁍ࠬܓ<💕>ᴛᴇʀɪ ᴍᴀ ᴘᴏᴛᴛʏ ᴘᴇsᴀʙ😖🔥ᴀɪ✯", "𑁍ࠬܓ<🩵>ᴛᴇʀɪ ᴍᴀ ᴄᴜᴅɪ ʀᴇx अब्बू sᴇ"]

REX_SWIPE_LIST = ["Tʀꪗ Bʜɴ तक्ली -😂🤟🏻💕", "𝐓ʀʏ 𝐌ᴀ 𝐂ʏ 𝐂ᴜᴛ 𝐏ʀ चप्पल Mᴀʀᴜɴɢα 🤪᭄🩴🔥", "𝐂ʜαʟ 𝐇αʀᴍ𝐳α𝐝𝐈 𝐊ᴇ लड़के 🤍☁🍃", "Nɪʟᴇ Dᴏʀᴇαᴍᴏɴ Kʏ Sʜᴋ𝐋 Kᴇ लड़के Cʜᴜᴘ Hᴏᴊα 🩴"]

NAME_LIST = [
    "{name} !⭒˚.⋆Lᴜɴ Lᴇ 🤸🏻👐🏻 ִֶָ𓂃 ࣪˖ ִֶָ🦋་༘࿐", "{name} !⭒˚.⋆की बेहन 𝗧𝗔𝗞Ｌ𝗜 🙆🏻",
    "{name} !⭒˚.⋆ki mom ne ᴄʜᴜᴅᴋᴇ ʀᴇx ᴋᴏ ʙᴀᴀᴩ ʙɴᴀ ʟɪʏᴀ 😉🔥", "{name} !⭒˚.⋆ᴩɪʟʟᴇ ᴋɪ ᴍᴀᴀ ᴍᴀʀɪ 👻",
    "{name} !⭒˚.⋆ki mom got 𝗙𝗨𝗖𝗞𝗘𝗗 🥀", "{name} !⭒˚.⋆ʀɴडीᴋe idr ꜱᴇ ᴜᴅʜʀ ᴛᴋ ᴄʜᴜᴅ 😂🔥",
    "{name} !⭒˚.⋆Sᴀʏ Rᴇx 𝘥ꪖ𝘥𝘥ꪗ 🪽", "{name} !⭒˚.⋆𝗕𝗛𝗔𝗚 🏃🏻💨", "{name} !⭒˚.⋆𝗚𝗨ΛΑΑΜ 🐕",
    "{name} !⭒˚.⋆ᴋɪᴛɴα ᴄʜᴜᴅᴇɢα ɢαʀɪʙ? 😧😧💔", "{name} !⭒˚.⋆𝗧𝗠𝗞𝗖 🤢", "{name} !⭒˚.⋆𝐑ɴडीᴋ𝐄 🦶🏻",
    "{name} !⭒˚.⋆Wʜᴏ🇷ᴇ 😜", "{name} !⭒˚.⋆Rɴᴅɪ 😏", "{name} !⭒˚.⋆Cᴠ🇷 𝗞🇷 👞",
    "{name} !⭒˚.⋆Pɪʟ 🤫", "{name} !⭒˚.⋆MɪSᴛʀɪ Kᴇ Lᴀᴅᴋᴇ 🧑🏻‍🔧⛏️",
    "{name} !⭒˚.⋆Try mom stride mh sudi? 🔥🖕🏿🎀🖕🏿", "{name} !⭒˚.⋆uth kuposhit rndyce 🦸‍😂🔥",
    "{name} !⭒˚.⋆𝘾𝙃𝘼𝙇 𝙍𝙉𝘿𝙄𝙆𝙀 𝙐𝙏𝙃𝘼𝙆 𝘽𝙀𝙏𝙃𝘼𝙆 𝙇𝘼𝙂𝘼😁🔥", "{name} !⭒˚.⋆Aʙᴇ Fᴜɴɴʏ Pɪʟʟᴇ JᴏＫER Tʜɪ Kʏᴀ Tᴇʀɪ Mᴀ🔥😂",
    "{name} !⭒˚.⋆Nɪʟᴇ DᴏRᴇ𝐀ＭＯＮ Kʏ Sʜᴋ𝐋 Kᴇ लड़के Cʜᴜ𝐏 Hᴏᴊ𝐀 🩵🩷", "{name} !⭒˚.⋆𝘾𝙮 𝙈𝙖 𝘾𝙤 𝘾𝙮𝙙𝑙𝑒 𝘾𝙝𝙖𝙡𝙖𝙠eke 𝘾𝙤𝙙𝙪𝙣𝐠𝘢 ¡?😁🚴🔥",
    "{name} !⭒˚.⋆oye kutiya k bache", "{name} !⭒˚.⋆Kzmor h dam laga tu"
]

EMO_LIST_1 = ["𓂃६ৎ 𓆩💖𓆪","𓂃६ৎ𓆩💗𓆪","𓂃६ৎ𓆩❤️𓆪"]
EMO_LIST_2 = ["🎐𓍼ֶָ֢⊹ ࣪ ˖","✨𓍼ֶָ֢⊹ ࣪ ˖","🍂𓍼ֶָ֢⊹ ࣪ ˖"]

# ---- LONG PATTERNS ----
BASE_LONG_PATTERNS = [
    "➵⤷⤷❤️⤷⤷🤍⤷⤷🖤⤷⤷❤⤷⤷🤍⤷⤷🖤⤷⤷❤️⤷⤷🖤⤷⤷🤍⤷⤷❤️⤷⤷🤍⤷⤷🖤⤷⤷❤️⤷⤷🤍⤷⤷🖤 ",
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫",
    "𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍𒈙🤍",
    "✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜",
    "⊹❤️⊹🧡⊹💛⊹❤️⊹🧡⊹💛⊹❤️⊹🧡⊹💛⊹🧡⊹💛⊹❤️⊹🧡⊹💛⊹❤️⊹🧡⊹💛⊹❤️⊹💛⊹❤️⊹🧡⊹💛⊹",
    "彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🖤彡🤍彡🩶彡🖤彡 彡🤍彡",
    "◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈🩵◈💙◈🩷◈💙◈🩷◈🩵",
    "❋🧡❋💛❋💚❋🧡❋💛❋💚❋🧡❋💛❋💚❋💛❋💚❋🧡❋💛❋💚❋🧡❋💛❋💚❋🧡❋💚❋🧡❋💛❋💚❋🧡❋💛❋💚❋🧡",
    "✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💙✧🩷✧💜✧💙✧🩷✧💜✧💙✧🩷✧💜"
]

TARGET_LENGTH = len("彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🩶彡🖤彡🤍彡🖤彡🤍彡🩶彡🖤彡 彡🤍彡")

def make_long_pattern(base):
    if not base: return ""
    times = (TARGET_LENGTH // len(base)) + 1
    return (base * times)[:TARGET_LENGTH]

LONGNC_PATTERNS = [make_long_pattern(b) for b in BASE_LONG_PATTERNS]

SPAMNC_PATTERN = "ƇӇƲƤ ƦƝƊƳƘƎ 𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫"
HEART_CYCLE = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🩷", "🩵", "🤍", "🖤"]

HOUR_CLOCKS = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
HALF_CLOCKS = ["🕧", "🕜", "🕝", "🕞", "🕟", "🕠", "🕡", "🕢", "🕣", "🕤", "🕥", "🕦"]

def get_clock_emoji(hour, minute):
    idx = hour % 12
    return HALF_CLOCKS[idx] if minute >= 30 else HOUR_CLOCKS[idx]

class RexMasterBot(discord.Client):
    def __init__(self, token, *args, **kwargs):
        super().__init__(*args, **kwargs, self_bot=True)
        self.token = token
        self.active_loops = {}
        self.msg_delay = 0.8
        self.nc_delay = 2.5
        self.heart_index = {}
        self.bypass_mode = True
        self.pending_tasks = {}

    async def run_attack(self, cid, cmd, args, target_msg_id=None):
        is_nc = cmd in ["nc", "ncc", "rexnc", "enc", "longnc", "baapnc", "timenc", "spmnc"]
        is_swipe = cmd in ["rexswipe", "eswipe", "cswipe", "target", "targetslide"]
        loop_type = "nc" if is_nc else "spam"

        if cid in self.active_loops and self.active_loops[cid].get(loop_type, False):
            return

        if cid not in self.active_loops:
            self.active_loops[cid] = {"spam": False, "nc": False}
            self.heart_index[cid] = 0
        self.active_loops[cid][loop_type] = True

        self.pending_tasks[cid] = (cmd, args)
        channel = self.get_channel(cid)
        if not channel: return

        if is_swipe and target_msg_id:
            swipe_targets[cid] = target_msg_id
        elif is_swipe:
            swipe_targets.pop(cid, None)

        burst_count = 0
        if self.bypass_mode and is_nc:
            burst_size = random.randint(12, 15)
            burst_pause = random.randint(3, 5)
        else:
            burst_size = 999999
            burst_pause = 0

        while self.active_loops.get(cid, {}).get(loop_type, False):
            try:
                if self.bypass_mode and is_nc:
                    burst_count += 1
                    if burst_count >= burst_size:
                        await asyncio.sleep(burst_pause)
                        burst_count = 0
                        burst_size = random.randint(12, 15)
                        burst_pause = random.randint(3, 5)

                if is_swipe:
                    target_id = swipe_targets.get(cid)
                    if target_id:
                        try:
                            target_msg = await channel.fetch_message(target_id)
                        except:
                            target_msg = None
                    else:
                        target_msg = None
                    if not target_msg:
                        async for m in channel.history(limit=1):
                            target_msg = m
                    if not target_msg:
                        await asyncio.sleep(self.msg_delay)
                        continue

                    if cmd == "eswipe":
                        line = f"{args} {random.choice(ENG_LIST)}"
                    elif cmd == "cswipe":
                        line = args
                    elif cmd == "target":
                        line = f"{args} {random.choice(REX_LIST)}"
                    elif cmd == "targetslide":
                        line = f"{args} {random.choice(REX_SWIPE_LIST)}"
                    else:
                        line = f"{args} {random.choice(REX_SWIPE_LIST)}"
                    await target_msg.reply(line, mention_author=False)
                    await asyncio.sleep(self.msg_delay)
                    continue

                elif cmd == "espam":
                    line = f"{args} {random.choice(ENG_LIST)}"
                elif cmd == "rexspam":
                    line = f"{args} {random.choice(REX_SPAM_LIST)}"
                elif cmd == "cspam":
                    line = args
                elif cmd in ["spam", "chudai"]:
                    line = f"{args} {random.choice(REX_LIST)}"
                elif is_nc:
                    if cmd == "ncc":
                        new_name = f"{random.choice(EMO_LIST_2)} {args} {random.choice(EMO_LIST_1)}"
                    elif cmd == "enc":
                        new_name = f"{args} {random.choice(ENG_LIST)}"[:100]
                    elif cmd == "longnc":
                        new_name = f"{args} {random.choice(LONGNC_PATTERNS)}"
                    elif cmd == "baapnc":
                        new_name = f"{args} {random.choice(LONGNC_PATTERNS)} 𝙏𝙀𝙍𝘼 𝘽𝘼𝘼𝙋 𝙍𝙀𝙓"
                    elif cmd == "spmnc":
                        heart = HEART_CYCLE[self.heart_index[cid] % len(HEART_CYCLE)]
                        self.heart_index[cid] += 1
                        new_name = f"{args} {SPAMNC_PATTERN} {heart}"
                    elif cmd == "timenc":
                        now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
                        time_str = now.strftime("%H:%M:%S")
                        clock_emoji = get_clock_emoji(now.hour, now.minute)
                        new_name = f"{args} 𝐃ᴇ𝐊ʜ 𝐓ᴇʀɪ 𝐌ᴀ 𝐊ɪ 𝐂ᴜᴅᴀɪ 𝐊ᴀ 𝐓ɪᴍᴇ 𝐇ᴏɢʏᴀ {time_str} {clock_emoji}"
                    else:
                        new_name = random.choice(NAME_LIST).format(name=args)
                    await channel.edit(name=new_name[:100])
                    await asyncio.sleep(self.nc_delay)
                    continue

                await channel.send(line)
                await asyncio.sleep(self.msg_delay)
            except:
                await asyncio.sleep(2)

        self.pending_tasks.pop(cid, None)
        swipe_targets.pop(cid, None)

    async def on_message(self, message):
        global SELF_REACT_EMOJI, global_react_target

        is_sudo = message.author.id in SUDO_USERS
        is_self = message.author.id == self.user.id

        if message.content.startswith(PREFIX):
            if not is_sudo and not is_self:
                await message.reply("𝙍𝙀𝙓 𝘽𝘼𝘼𝙋 𝙎𝙀 𝙎𝙐𝘿𝙊 𝙇𝙀𝙆𝙀 𝘼𝘼 𝘽𝙃𝙄𝙆𝘼𝙍𝙄")
                return

            parts = message.content[len(PREFIX):].split()
            cmd = parts[0].lower()
            args = " ".join(parts[1:]) if len(parts) > 1 else ""
            cid = message.channel.id

            if cmd in ["help", "menu"]:
                menu_text = (
                    "```yaml\n"
                    "╔══════════════════════════════════════╗\n"
                    "║    ⛩️  ECHO QTY MASTER MENU  ⛩️    ║\n"
                    "║     「 GAWD EDITION 」               ║\n"
                    "╚══════════════════════════════════════╝\n"
                    "```\n"
                    "**▸ SYSTEM**\n"
                    "`!status` `!ping` `!refresh` `!spamdelay` `!ncdelay` `!uptime`\n\n"
                    "**▸ NC ENGINE**\n"
                    "`!nc` `!ncc` `!enc` `!rexnc` `!longnc` `!baapnc` `!timenc` `!spmnc`\n"
                    "`!dnc` `!dlongnc` `!dbaapnc` `!dtimenc` `!dspmnc`\n\n"
                    "**▸ SPAM ENGINE**\n"
                    "`!spam` `!espam` `!rexspam` `!cspam` `!chudai`\n"
                    "`!rexswipe` `!eswipe` `!cswipe` `!target` `!targetslide` `!picspm`\n"
                    "`!dspam` `!dswipe` `!dtarget`\n\n"
                    "**▸ TARGET MODULES**\n"
                    "`!target` `!targetslide`\n\n"
                    "**▸ SUDO CONTROL**\n"
                    "`!addsudo` `!delsudo`\n\n"
                    "**▸ BOT MANAGEMENT**\n"
                    "`!minereact` `!dminereact` `!react` `!dreact`\n"
                    "`!lock @user` `!clock @user <msg>` `!dlock`\n"
                    "`!tts` (echo) `!dtts` `!activebots` `!leave`\n"
                    "`!gcpfp` (reply) `!dgcpfp` `!lockgcpfp` `!dlockgcpfp`\n"
                    "`!addbottoken` `!removebottoken`\n"
                    "`!purge <num>` `!purgefrom` `!purgehere` `!joingc` `!invgc`\n"
                    "`!bypassflood`\n\n"
                    "**▸ KILL SWITCHES**\n"
                    "`!stop`\n\n"
                    "```fix\n"
                    "⚡ ECHO QTY CORE ACTIVE ⚡\n"
                    "```"
                )
                await message.channel.send(menu_text)
                return

            elif cmd == "stop":
                if cid in self.active_loops:
                    self.active_loops[cid]["spam"] = False
                    self.active_loops[cid]["nc"] = False
                lock_targets.pop(cid, None)
                lock_messages.pop(cid, None)
                copycat_mode.discard(cid)
                global_react_target = None
                swipe_targets.pop(cid, None)
                self.pending_tasks.pop(cid, None)
                await message.channel.send("🛑 **ALL LOOPS & FEATURES KILLED**")
                return

            elif cmd == "dnc":
                if cid in self.active_loops: self.active_loops[cid]["nc"] = False
                self.pending_tasks.pop(cid, None)
                await message.channel.send("🛑 **NC LOOP STOPPED**")
                return
            elif cmd == "dspam":
                if cid in self.active_loops: self.active_loops[cid]["spam"] = False
                self.pending_tasks.pop(cid, None)
                await message.channel.send("🛑 **SPAM LOOP STOPPED**")
                return
            elif cmd in ["dswipe", "dtarget"]:
                if cid in self.active_loops: self.active_loops[cid]["spam"] = False
                swipe_targets.pop(cid, None)
                self.pending_tasks.pop(cid, None)
                await message.channel.send("🛑 **SWIPE/TARGET LOOP STOPPED**")
                return
            elif cmd == "dtts":
                copycat_mode.discard(cid)
                await message.channel.send("🔁 Echo mode OFF")
                return

            elif cmd == "status":
                latency_ms = round(self.latency * 1000)
                active_nc = sum(1 for v in self.active_loops.values() if v.get("nc"))
                active_spam = sum(1 for v in self.active_loops.values() if v.get("spam"))
                memory = psutil.Process(os.getpid()).memory_info().rss // 1024 // 1024
                guilds = len(self.guilds)
                status_text = (
                    f"**Bot Health Status**\n"
                    f"• Latency: `{latency_ms}ms`\n"
                    f"• Active NC loops: `{active_nc} channels`\n"
                    f"• Active spam loops: `{active_spam} channels`\n"
                    f"• Memory usage: `{memory} MB`\n"
                    f"• Servers: `{guilds}`"
                )
                await message.channel.send(status_text)
                return
            elif cmd == "uptime":
                if not start_time:
                    await message.channel.send("Uptime not available yet.")
                else:
                    delta = datetime.utcnow() - start_time
                    hours, remainder = divmod(int(delta.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    await message.channel.send(f"⏱️ Uptime: `{hours}h {minutes}m {seconds}s`")
                return
            elif cmd == "ping":
                latency = round(self.latency * 1000)
                await message.channel.send(f"🏓 **Pong!** `{latency}ms`")
                return
            elif cmd == "refresh":
                if cid in self.active_loops:
                    self.active_loops[cid]["spam"] = False
                    self.active_loops[cid]["nc"] = False
                gc.collect()
                await message.channel.send("🔄 **Bot refreshed & optimised. Speed tuned.**")
                return

            elif cmd == "spamdelay":
                ms = float(args) if args else 800
                self.msg_delay = ms / 1000
                await message.channel.send(f"spam delay set {int(ms)}ms")
                return
            elif cmd == "ncdelay":
                ms = float(args) if args else 2500
                self.nc_delay = ms / 1000
                await message.channel.send(f"NC delay set {int(ms)}ms")
                return

            elif cmd in ["dlongnc", "dbaapnc", "dtimenc", "dspmnc"]:
                if cid in self.active_loops: self.active_loops[cid]["nc"] = False
                self.pending_tasks.pop(cid, None)
                await message.channel.send(f"🛑 **{cmd.upper()} STOPPED**")
                return

            elif cmd == "addsudo" and is_self:
                for u in message.mentions:
                    if u.id not in SUDO_USERS: SUDO_USERS.append(u.id)
                await message.channel.send("👑 **SUDO USERS ADDED**")
                return
            elif cmd == "delsudo" and is_self:
                for u in message.mentions:
                    if u.id in SUDO_USERS: SUDO_USERS.remove(u.id)
                await message.channel.send("👑 **SUDO USERS REMOVED**")
                return

            elif cmd == "dreact":
                global_react_target = None
                await message.channel.send("🔴 **Global react removed**")
                return
            elif cmd == "dminereact":
                SELF_REACT_EMOJI = None
                await message.channel.send("🔕 **Self-react emoji disabled.**")
                return
            elif cmd == "react":
                if not message.mentions or not args:
                    await message.channel.send("Usage: `!react :emoji: @user`")
                    return
                user = message.mentions[0]
                emoji = args.split(" ")[0]
                global_react_target = (user.id, emoji)
                await message.channel.send(f"🎯 Global react to **{user.display_name}** with {emoji}")
                return
            elif cmd == "minereact":
                if not args:
                    await message.channel.send("Usage: `!minereact :emoji:`")
                    return
                SELF_REACT_EMOJI = args.strip()
                await message.channel.send(f"✅ Self-react emoji set to {SELF_REACT_EMOJI}")
                return

            elif cmd in ["lock", "clock"]:
                target_user = None
                custom_msg = None

                if message.reference:
                    try:
                        ref_msg = await message.channel.fetch_message(message.reference.message_id)
                        target_user = ref_msg.author
                    except:
                        pass

                if message.mentions:
                    target_user = message.mentions[0]

                if not target_user:
                    if cid in lock_targets:
                        del lock_targets[cid]
                        lock_messages.pop(cid, None)
                        await message.channel.send("🔓 **Lock removed.**")
                    else:
                        await message.channel.send("Usage: Reply to a user's message or mention them.\n`!lock` (to remove) or `!clock <custom message>`")
                    return

                if cmd == "clock":
                    args_without_mentions = args
                    for user in message.mentions:
                        args_without_mentions = args_without_mentions.replace(f"<@{user.id}>", "").replace(f"<@!{user.id}>", "").strip()
                    custom_msg = args_without_mentions if args_without_mentions else random.choice(REX_LIST)
                else:
                    custom_msg = random.choice(REX_LIST)

                lock_targets[cid] = target_user.id
                lock_messages[cid] = custom_msg
                await message.channel.send(f"🔒 **{target_user.display_name}** locked. Custom reply set: {custom_msg[:50]}...")
                return

            elif cmd == "dlock":
                if cid in lock_targets:
                    del lock_targets[cid]
                    lock_messages.pop(cid, None)
                    await message.channel.send("🔓 **Lock removed.**")
                else:
                    await message.channel.send("No lock active in this channel.")
                return

            elif cmd == "tts":
                if not args:
                    if cid in copycat_mode:
                        copycat_mode.discard(cid)
                        await message.channel.send("🔁 Copycat mode OFF")
                    else:
                        copycat_mode.add(cid)
                        await message.channel.send("🔁 Copycat mode ON – I'll mirror your messages instantly.")
                    return
                await message.channel.send(f"[TTS DISABLED] {args}")
                return

            elif cmd == "activebots":
                # Show status for each token in the TOKENS list
                lines = []
                for t in TOKENS:
                    if len(t) > 20:  # likely a real token
                        user_id = token_to_user.get(t)
                        if user_id and user_id in active_bots:
                            status = active_bots[user_id]["status"]
                            name = active_bots[user_id]["name"]
                            lines.append(f"• `{t[:10]}...` ({name}) – {status}")
                        else:
                            lines.append(f"• `{t[:10]}...` (Not connected) – offline")
                if not lines:
                    await message.channel.send("No tokens found or none connected yet.")
                else:
                    await message.channel.send("**Active Bots:**\n" + "\n".join(lines))
                return

            elif cmd == "leave":
                if message.guild:
                    await message.channel.send("👋 Leaving server...")
                    await message.guild.leave()
                elif isinstance(message.channel, discord.GroupChannel):
                    await message.channel.send("👋 Leaving group...")
                    await message.channel.leave()
                else:
                    await message.channel.send("This command can only be used in a server or group DM.")
                return

            elif cmd == "gcpfp":
                if not message.reference:
                    await message.channel.send("Reply to an image with `!gcpfp` to set & lock the server/group icon.")
                    return
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    if ref_msg.attachments:
                        img_url = ref_msg.attachments[0].url
                        async with aiohttp.ClientSession() as session:
                            async with session.get(img_url) as resp: img_bytes = await resp.read()
                        if message.guild:
                            await message.guild.edit(icon=img_bytes)
                            locked_pfp[message.guild.id] = img_bytes
                            await message.channel.send("✅ Server icon updated & locked.")
                        elif isinstance(message.channel, discord.GroupChannel):
                            await message.channel.edit(icon=img_bytes)
                            locked_pfp[message.channel.id] = img_bytes
                            await message.channel.send("✅ Group icon updated & locked.")
                        else:
                            await message.channel.send("This command can only be used in a server or group DM.")
                    else:
                        await message.channel.send("No image found in the replied message.")
                except Exception as e:
                    await message.channel.send(f"Failed to change icon: {e}")
                return
            elif cmd == "dgcpfp":
                if not message.guild: return await message.channel.send("This command only works in a server.")
                try: await message.guild.edit(icon=None); await message.channel.send("🗑️ **Server icon removed.**")
                except Exception as e: await message.channel.send(f"Failed to remove icon: {e}")
                return
            elif cmd == "lockgcpfp":
                if not message.guild: return await message.channel.send("This command only works in a server.")
                try:
                    if message.guild.icon:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(message.guild.icon.url) as resp: img_bytes = await resp.read()
                        locked_pfp[message.guild.id] = img_bytes
                        await message.channel.send("🔒 **Server icon locked.** Any changes will be reverted.")
                    else: await message.channel.send("Server has no icon to lock.")
                except Exception as e: await message.channel.send(f"Failed to lock icon: {e}")
                return
            elif cmd == "dlockgcpfp":
                if message.guild and message.guild.id in locked_pfp:
                    del locked_pfp[message.guild.id]; await message.channel.send("🔓 **Server icon lock removed.**")
                else: await message.channel.send("No icon lock active or not in server.")
                return

            elif cmd == "addbottoken" and is_self:
                if not args: await message.channel.send("Usage: `!addbottoken <token>`"); return
                token = args.strip()
                if token not in TOKENS:
                    TOKENS.append(token)
                    Thread(target=start_bot, args=(token,), daemon=True).start()
                    await message.channel.send("✅ Token added and bot starting...")
                else: await message.channel.send("Token already exists.")
                return
            elif cmd == "removebottoken" and is_self:
                if not args: await message.channel.send("Usage: `!removebottoken <token>`"); return
                token = args.strip()
                if token in TOKENS:
                    TOKENS.remove(token)
                    await message.channel.send("✅ Token removed (bot may still run until restart).")
                else: await message.channel.send("Token not found.")
                return

            elif cmd == "purge":
                if not args.isdigit():
                    await message.channel.send("Usage: `!purge <amount>`")
                    return
                amount = int(args)
                if amount < 1:
                    await message.channel.send("Amount must be at least 1.")
                    return
                try:
                    deleted = await message.channel.purge(limit=amount, bulk=True)
                    await message.channel.send(f"🧹 Deleted {len(deleted)} messages.", delete_after=3)
                except discord.Forbidden:
                    await message.channel.send("I don't have permission to delete messages.")
                except Exception as e:
                    await message.channel.send(f"Bulk delete failed: {e}. Falling back to slow delete...")
                    async for msg in message.channel.history(limit=amount+1):
                        try: await msg.delete()
                        except: pass
                        await asyncio.sleep(0.5)
                return

            elif cmd == "purgefrom":
                if not message.reference:
                    await message.channel.send("Reply to the **start** message with `!purgefrom`")
                    return
                purge_from_ids[cid] = message.reference.message_id
                await message.channel.send("✅ Start message saved. Now reply to the **end** message with `!purgehere`")
                return
            elif cmd == "purgehere":
                if not message.reference or cid not in purge_from_ids:
                    await message.channel.send("You must first set a start message with `!purgefrom` (reply to it), then reply to the end message with `!purgehere`")
                    return
                from_id = purge_from_ids.pop(cid)
                to_id = message.reference.message_id
                try:
                    after = await message.channel.fetch_message(from_id)
                    before = await message.channel.fetch_message(to_id)
                    async for msg in message.channel.history(limit=100, before=before, after=after):
                        try: await msg.delete()
                        except: pass
                        await asyncio.sleep(0.3)
                    try: await after.delete()
                    except: pass
                    try: await before.delete()
                    except: pass
                    await message.channel.send("🧹 Purge complete.", delete_after=3)
                except Exception as e:
                    await message.channel.send(f"Failed: {e}")
                return

            elif cmd == "picspm":
                if not message.reference:
                    await message.channel.send("Reply to an image with `!picspm` to spam it.")
                    return
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    if not ref_msg.attachments:
                        await message.channel.send("No image in the replied message.")
                        return
                    img_url = ref_msg.attachments[0].url
                    async with aiohttp.ClientSession() as session:
                        async with session.get(img_url) as resp:
                            img_bytes = await resp.read()
                    file = discord.File(BytesIO(img_bytes), filename="spam.png")
                    if cid not in self.active_loops:
                        self.active_loops[cid] = {"spam": False, "nc": False}
                    self.active_loops[cid]["spam"] = True
                    self.pending_tasks[cid] = ("picspm", args)
                    channel = self.get_channel(cid)
                    if not channel: return
                    while self.active_loops[cid]["spam"]:
                        try:
                            await channel.send(file=file)
                            file = discord.File(BytesIO(img_bytes), filename="spam.png")
                            await asyncio.sleep(self.msg_delay)
                        except:
                            await asyncio.sleep(2)
                except Exception as e:
                    await message.channel.send(f"Failed: {e}")
                return

            elif cmd == "joingc":
                invite_link = args
                if not invite_link:
                    await message.channel.send("Provide an invite link: `!joingc https://discord.gg/...`")
                    return
                try:
                    invite = await self.fetch_invite(invite_link)
                    await invite.accept()
                    await message.channel.send("✅ Joined the group/channel.")
                except Exception as e:
                    await message.channel.send(f"Failed to join: {e}")
                return
            elif cmd == "invgc":
                if not message.mentions:
                    await message.channel.send("Mention users to create a group with them.")
                    return
                try:
                    group = await self.create_group(message.mentions)
                    await message.channel.send(f"✅ Group created: {group.name} (ID: {group.id})")
                except Exception as e:
                    await message.channel.send(f"Failed to create group: {e}")
                return

            elif cmd == "bypassflood":
                self.bypass_mode = not self.bypass_mode
                state = "ON (burst mode – faster NC)" if self.bypass_mode else "OFF (old‑school safe continuous)"
                await message.channel.send(f"🔥 Bypass mode: {state}")
                return

            elif cmd in ["spam", "espam", "rexspam", "cspam", "rexswipe", "eswipe", "cswipe", "chudai", "target", "targetslide",
                         "nc", "ncc", "rexnc", "enc", "longnc", "baapnc", "timenc", "spmnc"]:
                target_msg_id = None
                if cmd in ["rexswipe", "eswipe", "cswipe", "target", "targetslide"] and message.reference:
                    target_msg_id = message.reference.message_id
                asyncio.create_task(self.run_attack(cid, cmd, args, target_msg_id))
                return

        # Non-command messages
        if is_self:
            return

        cid = message.channel.id
        if is_sudo:
            if cid in lock_targets and message.author.id == lock_targets[cid]:
                reply_text = lock_messages.get(cid, random.choice(REX_LIST))
                try: await message.reply(reply_text, mention_author=False)
                except: pass
            if global_react_target and message.author.id == global_react_target[0]:
                try: await message.add_reaction(global_react_target[1])
                except: pass
            if cid in copycat_mode:
                if message.reference:
                    try:
                        ref_msg = await message.channel.fetch_message(message.reference.message_id)
                        if ref_msg:
                            await ref_msg.reply(message.content, mention_author=False)
                    except: pass
                else:
                    await message.channel.send(message.content)

    async def on_connect(self):
        global start_time
        start_time = datetime.utcnow()
        # We don't have user yet, so we skip storing in on_connect

    async def on_disconnect(self):
        if self.user.id in active_bots:
            active_bots[self.user.id]["status"] = "offline"

    async def on_ready(self):
        global start_time
        start_time = datetime.utcnow()
        print(f"⛩️ CORE ONLINE: {self.user.name}")
        token_to_user[self.token] = self.user.id
        active_bots[self.user.id] = {"name": str(self.user), "status": "online"}
        # Auto-resume tasks
        for cid, (cmd, args) in list(self.pending_tasks.items()):
            asyncio.create_task(self.run_attack(cid, cmd, args))

    async def on_guild_update(self, before, after):
        if after.id in locked_pfp and before.icon != after.icon:
            try: await after.edit(icon=locked_pfp[after.id])
            except: pass

def start_bot(token):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            bot = RexMasterBot(token=token)
            bot.run(token)
        except Exception as e:
            print(f"Bot with token {token[:10]}... crashed: {e}")
            time_module.sleep(5)

if __name__ == "__main__":
    Thread(target=run_web).start()
    # Start bots from the TOKENS list (populated from env)
    for t in TOKENS:
        if len(t) > 20 and "TOKEN" not in t:
            Thread(target=start_bot, args=(t,), daemon=True).start()
            time_module.sleep(2)
    while True:
        time_module.sleep(1)
