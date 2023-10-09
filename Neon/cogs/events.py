import discord
from discord.ext import commands,tasks
import datetime
import jishaku
from Extra import config
import aiohttp

class events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embeds = []
    def cog_load(self):
        self.cd = commands.CooldownMapping.from_cooldown(2, 3, commands.BucketType.user)
        self.command_logger.start()
        self.GuildLeave.start()

    @commands.Cog.listener()
    async def on_ready(self):
      await self.bot.load_extension("jishaku")
      self.bot.owner_ids = [1137444075151311028]
      print(f"Connected as {self.bot.user}")
    
    @commands.Cog.listener("on_command")
    async def command_logger_embed(self, ctx):
        self.bot.invoked_commands += 1

        if self.bot.user.id != 1137764189021155388: return

        if ctx.interaction:
            ctx.message.content = '*Interaction Command*'

        embed = discord.Embed(
            description=f"**__Command:__** {ctx.command}\n\n**__Author:__** {ctx.message.author}\n**__Author ID:__** {ctx.message.author.id}\n\n**__Guild:__** {ctx.message.guild.name}\n**__Guild ID:__** {ctx.message.guild.id}\n\n**__Channel:__** {ctx.channel.mention}\n**__Channel ID:__** {ctx.channel.id}\n\n**__Message__**\n```\n{ctx.message.content}```\n\n**__Time:__** <t:{round(datetime.datetime.now().timestamp())}:R>\n**__Date__** {datetime.date.today()}",
            color=config.color
        )
        self.embeds.append(embed)


    @tasks.loop(seconds=10)
    async def command_logger(self):
        if self.bot.user.id != 1137764189021155388: return
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url="https://discord.com/api/webhooks/1138140612600799245/kmAtcx2DSfRuNxmBdr4O-8P3oUT-dNeX6TqYtW8l6RG9OjIO0m6knK5qSYmGHTXSfG8Z", session=session)
            if len(self.embeds) == 0:
               return
            
            await webhook.send(embeds=self.embeds)

            self.embeds = []

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        bucket = self.cd.get_bucket(message)
        ratelimit = bucket.update_rate_limit()

        if ratelimit: return

        if message.content != self.bot.user.mention or message.author.bot: return
        
        
        embed = discord.Embed(description=f"Hey {message.author.mention}\nMy prefix here is `&` \nServer Id: `{ctx.guild.id}`\n\nType `&`help To Get The Command List")

        button = discord.ui.Button(label="Invite Me", url=config.Invite)
        button2 = discord.ui.Button(label="Support ", url=config.Support)

        
        embed.color = config.color
        view = discord.ui.View().add_item(button).add_item(button2)
        embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon)
        embed.set_thumbnail(url=self.bot.user.avatar)
        embed.set_footer(text="Developed With ❤️ By Sky..!!" , icon_url=self.bot.user.avatar)
        await message.reply(embed=embed, view=view, mention_author=False)


    #@commands.Cog.listener()
    #async def on_message_edit(self, before, after):
    #    ctx = await self.bot.get_context(after)
      #  if before.content != after.content:
    #        if after.guild is None or after.author.bot:
      #          return
           # if ctx.command is None:
           #      return
           # if str(ctx.channel.type) == "public_thread":
           #     return
            #bot_message = None
           # async for message in ctx.channel.history(limit=10):
           #  if message.author == self.bot.user:
            #     bot_message = message
            #     break
              
          #  if bot_message is not None:
          #   await bot_message.delete()
              
           #  await self.bot.invoke(ctx)
        #else:
          #  return

    @commands.Cog.listener("on_message")
    async def MediaChannelMessageDelete(self, message: discord.Message):

        if str(message.channel.type) != 'text':
            return
        if type(message.author) == discord.User:
            return
        if message.author.bot:
            return
        
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT channel_id FROM Media WHERE guild_id = ?", (message.guild.id,))
        channel_ids_raw = await cur.fetchall()

        await cur.execute("SELECT role_id FROM MediaWhitelist WHERE guild_id = ?", (message.guild.id,))
        role_ids_raw = await cur.fetchall()

        role_ids = [int(i[0]) for i in role_ids_raw]
        
        channel_ids = [int(i[0]) for i in channel_ids_raw]

        IDS = [int(i.id) for i in message.author.roles]
        
        for roleids in role_ids:
            if roleids in IDS:
                return
            
        if message.channel.id not in channel_ids:
            return
        if not message.attachments:
            bucket = self.cd.get_bucket(message)
            retry = bucket.update_rate_limit()

            if retry: return
            await message.delete()  

    @commands.Cog.listener("on_message")
    async def AFKMessage(self, message: discord.Message):

        if message.author.bot or str(message.channel.type) == 'private':
            return
        
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT user_id, guild_id, reason FROM AFK")
        re = await cur.fetchall()

        if re == []:
            return
        
        for i in re:
            user = self.bot.get_user(int(i[0]))
            if user is None:
                await cur.execute("DELETE FROM AFK WHERE user_id = ? AND guild_id = ?", (i[0], i[1]))
                continue

            if message.guild.id == int(i[1]):
                if message.author.id == user.id:
                    bucket = self.cd.get_bucket(message)
                    retry = bucket.update_rate_limit()

                    if retry: return

                    await cur.execute("DELETE FROM AFK WHERE guild_id = ? AND user_id = ?", (message.guild.id, user.id))
                    await message.channel.send(f"**{message.author}** Welcome back, Your AFK has been removed.", delete_after=5)
                    print(f'AFK Removed - {user} ({user.id})')

                if user.mention in message.content or str(user.name).lower() in (message.content).lower():
                    bucket = self.cd.get_bucket(message)
                    retry = bucket.update_rate_limit()

                    if retry: return

                    await message.channel.send(f"**{user}** is AFK - {i[2]}", allowed_mentions=discord.AllowedMentions.none())

                if message.reference:
                    if message.reference.resolved:
                        bucket = self.cd.get_bucket(message)
                        retry = bucket.update_rate_limit()

                        if retry: return

                        if message.reference.resolved.author.id == user.id:
                            await message.channel.send(f"**{user}** is AFK - {i[2]}", allowed_mentions=discord.AllowedMentions.none())
                    
            
        await self.bot.db.commit() 

    @commands.Cog.listener('on_message')
    async def AutoResponder(self, message: discord.Message):

        if message.author.bot or str(message.channel.type) == 'private': return

        c = await self.bot.db.cursor()
        await c.execute("SELECT name, content FROM auto_res WHERE guild_id = ?", (message.guild.id,))
        re = await c.fetchall()
        if re == []: return

        for m in re:
            if m[0].lower() == message.content.lower():

                bucket = self.cd.get_bucket(message)
                retry = bucket.update_rate_limit()

                if retry: return

                await message.channel.send(m[1])

        await self.bot.db.commit()
    
    
    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild :discord.Guild):
        if self.bot.user.id != 1137764189021155388: return
        c = await self.bot.db.cursor()
        await c.execute("SELECT guild_id FROM G_bl")
        re = await c.fetchall()

        guild_list = [int(i[0]) for i in re]

        if guild.id in guild_list:
            await guild.leave()

        
        



         
        embed = discord.Embed(title="Joined A Guild", description=f"**ID:** {guild.id}\n**Name:** {guild.name}\n**MemberCount:** {len(guild.members)}\n**Created:** <t:{int(guild.created_at.timestamp())}:R>")
        embed.add_field(name="Owner Information",
        value=f"**Name:** {guild.owner} ({guild.owner_id})\n**Created:** <t:{int(guild.owner.created_at.timestamp())}:R>", inline=False)
        embed.add_field(name=f"{self.bot.user.name} GuildCount",
        value=f"```fix\n{len(self.bot.guilds)}```", inline=False)
        embed.add_field(name=f"{self.bot.user.name} UserCount",
        value=f"```fix\n{len(self.bot.users)}```", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        embed.color = config.color
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner is not None:
            embed.set_image(url=guild.banner.url)
        channel = self.bot.get_channel(1138140072831627425)
        await channel.send(embed=embed)
    
    @commands.Cog.listener("on_guild_remove")
    async def on_guild_remove(self, guild: discord.Guild):
        if self.bot.user.id != 1137764189021155388: return
        
        cur = await self.bot.db.cursor()
        await cur.execute(f"DELETE FROM Autorole WHERE guild_id = ?", (guild.id,))
        await cur.execute(f"DELETE FROM AutoroleHuman WHERE guild_id = ?", (guild.id,))
        await cur.execute(f"DELETE FROM Welcome WHERE guild_id = ?", (guild.id,))
        await cur.execute(f"DELETE FROM TicketUser WHERE guild_id = ?", (guild.id,))
        await cur.execute(f"DELETE FROM Ticket WHERE guild_id = ?", (guild.id,))
        await cur.execute(f"DELETE FROM Media WHERE guild_id = ?", (guild.id,))
        await cur.execute(f"DELETE FROM MediaWhitelist WHERE guild_id = ?", (guild.id,))
        await cur.execute(f"DELETE FROM Giveaway WHERE guild_id = ?", (guild.id,))
        await cur.execute(f"DELETE FROM AFK WHERE guild_id = ?", (guild.id,))
        await cur.execute(f"DELETE FROM wlc_ch WHERE guild_id = ?", (guild.id,))
        


        await self.bot.db.commit()

        owner = guild.owner
        embed = discord.Embed(title="Left A Guild", description=f"**ID:** {guild.id}\n**Name:** {guild.name}\n**MemberCount:** {len(guild.members)}\n**Created:** <t:{int(guild.created_at.timestamp())}:R>")
        embed.add_field(name="Owner Information",
        value=f"**Name:** {guild.owner} ({guild.owner_id})\n**Created:** <t:{int(owner.created_at.timestamp())}:R>", inline=False)
        embed.add_field(name=f"{self.bot.user.name} GuildCount",
        value=f"```fix\n{len(self.bot.guilds)}```", inline=False)
        embed.add_field(name=f"{self.bot.user.name} UserCount",
        value=f"```fix\n{len(self.bot.users)}```", inline=False)
        embed.add_field(name=f"Shard ID",
        value=f"```fix\n{guild.shard_id}```")
        embed.timestamp = datetime.datetime.utcnow()
        embed.color = config.color
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner is not None:
            embed.set_image(url=guild.banner.url)
            
        channel = self.bot.get_channel(1138140088954519562)
        await channel.send(embed=embed)
        print(f"Left: {guild.name} ({guild.id})")

    
    @tasks.loop(seconds=10)
    async def GuildLeave(self):
        await self.bot.wait_until_ready()
        
        c = await self.bot.db.cursor()
        await c.execute("SELECT guild_id FROM G_bl")
        re = await c.fetchall()

        for guild_id in re:
            if int(guild_id[0]) in [int(i.id) for i in self.bot.guilds]:
                guild = self.bot.get_guild(int(guild_id[0]))
                await guild.leave()
          
    



async def setup(bot: commands.Bot):
    await bot.add_cog(events(bot))