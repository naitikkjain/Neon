import discord , os
from discord.ext import commands
def owner():
    async def predicate(ctx: commands.Context):
        c = await ctx.bot.db.cursor()
        await c.execute("SELECT user_id FROM Owner")
        ids_ = await c.fetchall()
        if ids_ is None:
            return

        ids = [int(i[0]) for i in ids_]
        if ctx.author.id in ids:
            return True
        else:
            return False
    return commands.check(predicate)
color = 0x2b2d31

#EMOJIS

Tick="<:raze_tick:1137769484397051926>"
Cross="<:raze_cross:1137769307632308285>"

StageChannel = "<:raze_stage:1137769083421610094>"
TextChannel = "<:raze_hashtag:1137768591945642015>"
VoiceChannel = "<:raze_voice:1137768063547216022>"

Support = "https://discord.gg/n24FvHEugA"
Invite = "https://discord.com/api/oauth2/authorize?client_id=1137764189021155388&permissions=8&scope=bot"