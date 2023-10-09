import discord
from discord.ext import commands
import asyncio
import aiosqlite
import datetime
from cogs.ticket import ButtonView , TicketView
from Extra import config
import json
import wavelink
from wavelink.ext import spotify

from core.context import Context

proxy_url = "http://103.155.217.156:41469"

async def get_prefix(client, message):
    if str(message.channel.type) == 'private':
        await message.channel.send("Currently Raze is not available in DMs.")
        return

    
    cursor = await client.db.execute(f"SELECT users FROM Np")
    NP = await cursor.fetchall()

    if message.author.id in ([int(i[0]) for i in NP]):
        a = commands.when_mentioned_or('', '&')(client, message)
        return sorted(a, reverse=True)
    else:
        return commands.when_mentioned_or('&')(client, message)



class Neon(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                        intents=discord.Intents.all(),
                        shards=10,
                        case_insensitive=True,
                        strip_after_prefix=True,
                        status=discord.Status.online,
                        activity=discord.Activity(type=discord.ActivityType.listening, name="&help"),
                        proxy_url=proxy_url
                        )

    async def setup_hook(self):
        self.invoker = {}
        self.invoked_commands = 0

        self.db = await aiosqlite.connect("Main.db")
        self.cd = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)
        cur = await self.db.cursor()
        
        await cur.execute("CREATE TABLE IF NOT EXISTS G_bl(guild_id TEXT NOT NULL, time TEXT, reason TEXT, author_id TEXT)")
        await cur.execute("CREATE TABLE IF NOT EXISTS wlc_ch (guild_id VARCHAR(20),channel_id VARCHAR(20));")
        await cur.execute("CREATE TABLE IF NOT EXISTS Welcome (guild_id INTEGER, msg TEXT,delete_after INTEGER);")
        await cur.execute("CREATE TABLE IF NOT EXISTS Embed (embed TEXT,state TEXT,ping INTEGER,guild_id INTEGER);")
        await cur.execute("CREATE TABLE IF NOT EXISTS Autorole (guild_id INTEGER,role_id INTEGER);")
        await cur.execute("CREATE TABLE IF NOT EXISTS AutoroleHuman (guild_id INTEGER,role_id INTEGER);")
        await cur.execute("CREATE TABLE IF NOT EXISTS Giveaway (guild_id INTEGER,host_id INTEGER,start_time TEXT,ends_at TEXT,prize TEXT,winners INTEGER,message_id INTEGER,channel_id INTEGER);")
        await cur.execute("CREATE TABLE IF NOT EXISTS MediaWhitelist (guild_id INTEGER,channel_id INTEGER,role_id INTEGER);")
        await cur.execute("CREATE TABLE IF NOT EXISTS Media (guild_id INTEGER, channel_id INTEGER);")
        await cur.execute("CREATE TABLE IF NOT EXISTS Ticket (guild_id INTEGER,support_roleid INTEGER,channel_id INTEGER, category_id INTEGER, message_id INTEGER);")
        await cur.execute("CREATE TABLE IF NOT EXISTS TicketUser(user_id TEXT NOT NULL, channel_id TEXT NOT NULL, guild_id TEXT NOT NULL, state TEXT);")
        await cur.execute("CREATE TABLE IF NOT EXISTS AFK (user_id INT,guild_id INT,reason VARCHAR(255));")
        await cur.execute("CREATE TABLE IF NOT EXISTS Np(users)")
        await cur.execute("CREATE TABLE IF NOT EXISTS Blacklisted (user_id TEXT NOT NULL,author_id TEXT NOT NULL,time	TEXT NOT NULL,reason TEXT);")
        await cur.execute("CREATE TABLE IF NOT EXISTS auto_res (id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER,name TEXT,content TEXT,time INTEGER);")
        print("Databasing Done")

         
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

        self.launch_time = datetime.datetime.utcnow()

        await self.load_extension("cogs.events")
        await self.load_extension("cogs.giveaway")
        await self.load_extension("cogs.help")
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.utility")
        await self.load_extension("cogs.autoresponder")
        await self.load_extension("cogs.info")
        await self.load_extension("cogs.voice")
        await self.load_extension("cogs.owner")
        await self.load_extension("cogs.ticket")
        await self.load_extension("cogs.media")
        await self.load_extension("cogs.welcome")
        await self.load_extension("cogs.error")
        await self.db.commit()
        asyncio.create_task(DBRefresher())
        button_view = ButtonView(client)
        ticket_view = TicketView(client)
        client.add_view(button_view)
        client.add_view(ticket_view)

    async def get_context(self, message, *, cls=None):
      return await super().get_context(message, cls=cls or Context)

client = Neon()


async def DBRefresher():
    await client.wait_until_ready()
    
    c = await client.db.cursor()
    await c.execute("SELECT channel_id FROM wlc_ch")
    channels__1 = await c.fetchall()

    if channels__1 != []:
        channels1 = [int(i[0]) for i in channels__1]

        for channel in channels1:
            got = client.get_channel(channel)
            if got is None:
                await c.execute("DELETE FROM wlc_ch WHERE channel_id = ?", (channel,))

    #----------------------------#

    await c.execute("SELECT channel_id FROM TicketUser")
    re = await c.fetchall()

    if re != []:
        channels1 = [int(i[0]) for i in re]

        for channel in channels1:
            ch = client.get_channel(channel)
            if ch is None:
                await c.execute("DELETE FROM TicketUser WHERE channel_id = ?", (channel,))
    
    #----------------------------#

    await c.execute("SELECT channel_id FROM Media")
    channels__2 = await c.fetchall()

    if channels__2 != []:
        channels2 = [int(i[0]) for i in channels__2]

        for channel in channels2:
            cj = client.get_channel(channel)
            if cj is None:
                await c.execute("DELETE FROM Media WHERE channel_id = ?", (channel,))

    await c.execute("SELECT role_id, guild_id FROM MediaWhitelist")
    roles__1 = await c.fetchall()

    if roles__1 != []:
        roles2 = [int(i[0]) for i in roles__1]
        guilds2 = [int(i[1]) for i in roles__1]

        for r1_, guild_1 in zip(roles2, guilds2):
                guild = client.get_guild(guild_1)
                r = guild.get_role(r1_)
                if r is None:
                    await c.execute("DELETE FROM MediaWhitelist WHERE role_id = ?", (r1_,))
        
    #--------------------------

    

                

    #--------------------------
    
    

    await client.db.commit()
    print("Successfully refreshed the database.")

@client.check
@commands.cooldown(1, 60.0, commands.BucketType.user)
async def bl(ctx):
    cur = await client.db.cursor()
    await cur.execute("SELECT user_id FROM Blacklisted")
    user = await cur.fetchall()
    if ctx.author.id in [int(i[0]) for i in user] and ctx.author.id not in client.owner_ids:
        bucket = client.cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()

        if retry_after: return
        
        embed = discord.Embed(description=f"You cannot use my commands as you're banned from using me.\n\nReach [Support Server]() to appeal.")
        embed.color = config.color
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=client.user.name, icon_url=client.user.display_avatar.url)
        await ctx.channel.send(embed=embed)
        return False
    elif ctx.author.id not in [int(i[0]) for i in user]:
        return True

@client.check
async def LockdownCheck(ctx):
    if ctx.author.id in client.owner_ids:
        return True

    with open('DB/lockdown.json', 'r') as f:
        data = json.load(f)

    if not data['state']:
        bucket = client.cd.get_bucket(ctx.message)
        retry = bucket.update_rate_limit()
        if retry: return False

        embed = discord.Embed(
            description=f"Hey, **Raze** is currently unavailable. The bot will be back soon. Please check [Status On Our Support Server]()",
            color=config.color
        )
        embed.set_author(name=client.user.name, icon_url=client.user.display_avatar.url)
        await ctx.send(embed=embed, delete_after=10)
        return False
    else: return True

@client.event
async def on_message_edit(before, after):
    ctx: Context = await client.get_context(after, cls=Context)
    
    if not ctx.valid: return
    if before.content != after.content:
        if after.guild is None or after.author.bot:
            return
        if ctx.command is None:
            return
        if str(ctx.channel.type) == "public_thread":
            return
        
        if after.id in client.invoker:
            await client.process_commands(after)
        else:
            await client.invoke(ctx)

    else:
        return




        



client.run("")
asyncio.run(client.db.close())