import discord
from discord.ext import commands
import datetime




from Extra import config

class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Shows bot's uptime.")
    async def uptime(self, ctx):
        delta_uptime = datetime.datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        
        await ctx.send(
        f"Uptime: {days} days, {hours} hours, {minutes} minutes and {seconds} seconds."
        )

    @commands.hybrid_command(aliases=['bi', 'stats'], description="Shows Bot's information")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botinfo(self, ctx):
        
       

        delta_uptime = datetime.datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        c = []
        for guild in self.bot.guilds:
            for ch in guild.voice_channels:
                c.append(ch)

        c2 = []
        for guild in self.bot.guilds:
            for ch2 in guild.text_channels:
                c2.append(ch2)

        c3 = []
        for guild in self.bot.guilds:
            for ch3 in guild.stage_channels:
                c3.append(ch3)

        total_users = sum([i.member_count for i in self.bot.guilds])
        cached_users = len(self.bot.users)


        embed = discord.Embed(title="")
        embed.add_field(inline=False, name=f"__{self.bot.user.name} Information__",
        value=f"**Online Since:** {days} day(s), {hours} hour(s), {minutes} minute(s) and {seconds} second(s)\n**Servers:** {len(self.bot.guilds)}\n**Shards:** {len(self.bot.shards)}\n**Users** {total_users} Total | {cached_users} Cached\n**Commands:** Total {len(self.bot.commands)} \n**Total Channels** {len(list(self.bot.get_all_channels()))}\n**Version:** 2.0.0")

        
    
      



        embed.color = config.color
        embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=self.bot.user.display_avatar.url)
        
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Shows bot's ping.")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)

        text =f":ping_pong: My Ping Is {latency}\n I'm Alive"

        await ctx.send(text)


async def setup(bot):
    await bot.add_cog(info(bot)) 