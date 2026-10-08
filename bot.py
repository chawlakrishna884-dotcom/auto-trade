import os
import random
import logging
from datetime import datetime, timezone

import discord
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("trade-selfbot")

USER_TOKEN = os.getenv("USER_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0") or 0)
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "300"))
MESSAGE = os.getenv("MESSAGE", "WTS royal package, dm me")

if not USER_TOKEN:
    raise SystemExit("missing USER_TOKEN in env")
if not CHANNEL_ID:
    raise SystemExit("missing CHANNEL_ID in env")

MESSAGES_RAW = os.getenv("MESSAGES", "")
MESSAGES = [m.strip() for m in MESSAGES_RAW.split("||") if m.strip()] or [MESSAGE]


class TradeSelfbot(discord.Client):
    def __init__(self):
        super().__init__()
        self.channel_id = CHANNEL_ID
        self.interval_seconds = INTERVAL_SECONDS

    async def on_ready(self):
        log.info("logged in as %s (%s)", self.user, self.user.id)
        if not self.trade_loop.is_running():
            self.trade_loop.change_interval(seconds=self.interval_seconds)
            self.trade_loop.start()
            log.info("trade loop started, every %ss", self.interval_seconds)

    @tasks.loop(seconds=INTERVAL_SECONDS)
    async def trade_loop(self):
        channel = self.get_channel(self.channel_id)
        if channel is None:
            try:
                channel = await self.fetch_channel(self.channel_id)
            except discord.HTTPException as e:
                log.warning("channel fetch failed: %s", e)
                return
        if not isinstance(channel, discord.TextChannel):
            log.warning("target is not a text channel")
            return

        msg = random.choice(MESSAGES)
        try:
            await channel.send(msg)
            log.info("sent: %s", msg)
        except discord.HTTPException as e:
            log.error("send failed: %s", e)

    @trade_loop.before_loop
    async def before_loop(self):
        await self.wait_until_ready()


if __name__ == "__main__":
    bot = TradeSelfbot()
    bot.run(USER_TOKEN)
