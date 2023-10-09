from typing import Optional
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Select
import re, typing, aiosqlite, pytz, datetime, discord, requests, os, asyncio, time
import aiohttp


from Extra import config, converters
from paginations.paginator import PaginatorView




def get_message_emojis(m: discord.Message) -> typing.List[discord.PartialEmoji]:
    """ Returns a list of custom emojis in a message. """
    emojis = re.findall('<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>', m.content)
    return [discord.PartialEmoji(animated=bool(animated), name=name, id=id) for animated, name, id in emojis]





snipe_message_author = {}
snipe_message_content = {}
snipe_message_time = {}
snipe_message_attachments = {}
snipe_message_replied = {}







class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Shows all information of the server.", aliases=['si'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        bans = '**Banned:** ' + str(len([entry async for entry in guild.bans()])) if ctx.guild.me.guild_permissions.ban_members else ''
        desc = ''.join(f"{guild.description}\n" if guild.description is not None else '')
        upload_limit = float(round(guild.filesize_limit / 1024 / 1034))
        Features = ''.join([f"{config.Tick}:{i.lower().title().replace('_', ' ')}\n" for i in guild.features])
        rules = ''.join(f"**Rules Channel:** {guild.rules_channel.mention}" if guild.rules_channel is not None else '')

        vc = len(guild.voice_channels) if guild.voice_channels is not None else None
        txt = len(guild.text_channels) if guild.text_channels is not None else None
        stage = len(guild.stage_channels) if guild.stage_channels is not None else None

        output = ""
        if vc: output += config.VoiceChannel + str(vc)
        if txt:
            if output: output += " | "
            output += config.TextChannel + str(txt)
        if stage:
            if output: output += " | "
            output += config.StageChannel + str(stage)

        noti = {
            "NotificationLevel.all_messages": "All Messages",
            "NotificationLevel.only_mentions": "Only @mentions"
        }
        c = str(noti[str(guild.default_notifications)])

        inactive_ch = f'**Inactive Channel:** {guild.afk_channel.mention}\n' if guild.afk_channel is not None else ''
        systm_msg_ch = f'**System Message Channel:** {guild.system_channel.mention}\n' if guild.system_channel is not None else ''
        verify_lvl = f'**Verification Level:** {str(guild.verification_level).title()}\n' if str(guild.verification_level) != 'none' else ''

        embed = discord.Embed(
            description=f"{desc}",
            color=config.color,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="__About__",
            value=f"**Name:** {guild.name}\n**ID:** {guild.id}\n**Owner:** <:owner:1116042446296588295> {guild.owner} ({guild.owner.mention})\n**Server Created:** <t:{round(guild.created_at.timestamp())}:R>\n**Members:** {len(list(guild.members))}\n{bans}",
            inline=False
        )

        embed.add_field(
            name="__Extra__",
            value=f"{verify_lvl}**Upload Limit:** {upload_limit} MB\n{inactive_ch}**Inactive Timeout:** {round(guild.afk_timeout / 60)} minutes\n{systm_msg_ch}**System Welcome Messages:** {config.Tick if guild.system_channel_flags.join_notifications else config.Cross}\n**System Boost Messages:** {config.Tick if guild.system_channel_flags.premium_subscriptions else config.Cross}\n**Default Notifications:** {c}\n**Explicit Media Content Filter:** {config.Tick if guild.explicit_content_filter else config.Cross}\n**2FA Requirements:** {config.Tick if guild.mfa_level else config.Cross}",
            inline=False
        )

        if len(Features) != 0:
            embed.add_field(
                name="__Features__",
                value=Features,
                inline=False
            )

        embed.add_field(
            name="__Channels__",
            value=f"**Total:** {len(guild.channels)}\n**Channels:** {output}\n{rules}",
            inline=False
        )

        an_emojis = len([i for i in guild.emojis if i.animated])
        n_emojis = len([i for i in guild.emojis if not i.animated])

        embed.add_field(
            name="__Emoji Info__",
            value=f"**Regular:** {n_emojis}/{guild.emoji_limit}\n**Animated:** {an_emojis}/{guild.emoji_limit}\n**Total:** {len(guild.emojis)}/{guild.emoji_limit}"
        )

        embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)

        if guild.icon is not None:
            embed.set_thumbnail(
                url=guild.icon.url
            )
            embed.set_author(
                name=guild.name,
                icon_url=guild.icon.url
            )
        else:
            embed.set_author(
                name=guild.name
            )

        await ctx.send(embed=embed)

            

    @commands.hybrid_command(aliases=['av'], description="Shows user's avatar")
    async def avatar(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        if user.avatar is not None:
            embed = discord.Embed(color=config.color)
            embed.set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.set_image(url=user.avatar.url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_author(name=user, icon_url=user.avatar.url)

            button = discord.ui.Button(label="Download", url=user.avatar.url)
            view = discord.ui.View().add_item(button)

            await ctx.send(embed=embed, view=view)

        else:
            await ctx.send(f"This user doesn't have any avatar.")

    @commands.hybrid_command(aliases=['mc','members'], description="Shows membercount server.")
    async def membercount(self, ctx):
        embed = discord.Embed(title="Member Count", description=f"{ctx.guild.member_count} Members", color=config.color)
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_group(invoke_without_command=True, description="Banner command for user and server.")
    async def banner(self, ctx):
        await ctx.send_help(ctx.command)

    @banner.command(description="Shows banner of a user.")
    async def user(self, ctx, user: discord.Member=None):
        if user is None:
            user = ctx.author
        user_info = await self.bot.fetch_user(user.id)
        if user_info.banner is None:
            await ctx.send(f"This user doesn't have any banner.")
            return

        embed = discord.Embed(color=config.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_image(url=user_info.banner.url)
        button = discord.ui.Button(label="Download", url=user_info.banner.url)
        view = discord.ui.View(timeout=None).add_item(button)
        await ctx.send(embed=embed, view=view)

    @banner.command(description="Shows banner of the server")
    async def server(self, ctx):
        if ctx.guild.banner is None:
            await ctx.send(f"This server doesn't have any banner.")
            return

        embed = discord.Embed(color=config.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_image(url=ctx.guild.banner.url)
        button = discord.ui.Button(label="Download", url=ctx.guild.banner.url)
        view = discord.ui.View(timeout=None).add_item(button)
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_group(description="Cleans the given amount of messages.", invoke_without_command=True, usage='<Choice>')
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def purge(self, ctx, user: typing.Optional[discord.Member], limit):
        if ctx.interaction: await ctx.defer()
        if not ctx.interaction: await ctx.message.delete()

        try: int(limit)
        except ValueError:
            return await ctx.send(f"Invalid input.")
        
        if user:
            def check(m):
                if m.author.bot: return True

            d = await ctx.channel.purge(limit=int(limit), check=check)
            await ctx.send(f"Successfully cleaned {len(d)} messages.", delete_after=3, ephemeral=True)
        else:

            d = await ctx.channel.purge(limit=int(limit))
            await ctx.send(f"Successfully cleaned {len(d)} messages.", delete_after=3, ephemeral=True)

    @purge.command(description="Deletes only the messages of bot users.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.bot_has_permissions(manage_messages=True)
    async def bots(self, ctx, limit = 100):
        if ctx.interaction: await ctx.defer()
        if not ctx.interaction: await ctx.message.delete()

        def check(m):
            if m.author.bot:
                return True
        deleted = await ctx.channel.purge(limit=limit, check=check, before=ctx.message, bulk=True)

        await ctx.send(f"Successfully cleaned {len(deleted)} messages.", delete_after=3, ephemeral=True)

    @purge.command(description="Deletes only the messages of humans.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def humans(self, ctx, limit= 100):
        if ctx.interaction: await ctx.defer()
        if not ctx.interaction: await ctx.message.delete()

        def check(m):
            if not m.author.bot:
                return True

        deleted = await ctx.channel.purge(limit=limit, check=check, before=ctx.message, bulk=True)

        await ctx.send(f"Successfully cleaned {len(deleted)} messages.", delete_after=3, ephemeral=True)

    @purge.command(description="Deletes the messages containing the substring.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def contains(self, ctx, *, substr: str):
        if ctx.interaction: await ctx.defer()
        if not substr:
            await ctx.send(f"Please provide a substring to search for.")
            return
        if not ctx.interaction: await ctx.message.delete()

        def check(m):
            if substr.lower() in m.content.lower():
                return True

        deleted = await ctx.channel.purge(limit=100, check=check, before=ctx.message, bulk=True)

        await ctx.send(f"Successfully cleaned {len(deleted)} messages", delete_after=3, ephemeral=True)

    @commands.hybrid_command(aliases=['nuke'], description="Clones a text channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def clone(self, ctx):
        
        class ButtonView(View):
            def __init__(self, bot):
                self.bot = bot
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.followup.send(f"Its not your interaction dumbo.", ephemeral=True)
                    return
                try:
                   c =  await interaction.channel.clone(reason=f"By {ctx.author}")
                except:
                    await ctx.message.delete()
                    return await ctx.send(f"This channel cannot be cloned.")

                await c.move(before=interaction.channel)
                await ctx.channel.delete()
                self.stop()
            
            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Integration, button: Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.followup.send(f"Its not your interaction dumbo.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled")
                self.stop()

            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    self.stop()
                    return
                await self.message.delete()
                await ctx.send(content=f"{ctx.author.mention} Okay, this channel will not be cloned.")
            
        embed = discord.Embed(description="**Are you sure you want to clone this channel?**", color=config.color)
        view = ButtonView(bot=self.bot)
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()
                
    @commands.hybrid_command(description="Makes you afk. If someone pings they are notified with the reason.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def afk(self, ctx, *, reason: typing.Optional[str]):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT * FROM AFK WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id))
        re = await cur.fetchone()
        if re is not None:
            await ctx.send(f"**{ctx.author}**, You're too quick please slow down.")
            return
        
        reason = f'**{reason}**' or 'No reason'

        await cur.execute("INSERT INTO AFK(user_id, guild_id, reason) VALUES(?, ?, ?)", (ctx.author.id, ctx.guild.id, reason))

        await ctx.send(f"**{ctx.author}**, You have been set to AFK - {reason}", allowed_mentions=discord.AllowedMentions.none())
        await self.bot.db.commit()



    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        
        snipe_message_author[message.channel.id] = message.author
        snipe_message_content[message.channel.id] = message.content
        if message.attachments:
            snipe_message_attachments[message.channel.id] = message.attachments
        else:
            try:
               del snipe_message_attachments[message.channel.id]
            except KeyError:pass
            
        if message.reference:
            snipe_message_replied[message.channel.id] = message.reference.resolved
        else:
            try:
               del snipe_message_replied[message.channel.id]
            except KeyError:pass

        snipe_message_time[message.channel.id] = datetime.datetime.now()



    @commands.hybrid_command(description="Shows the latest deleted message.")
    async def snipe(self, ctx):
        try:
            embed = discord.Embed(
                description=f"Message sent by {snipe_message_author.get(ctx.channel.id)} deleted in {ctx.channel.mention}.",
                color=config.color
            )
            embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)

            content = snipe_message_content[ctx.channel.id] if len(snipe_message_content[ctx.channel.id]) != 0 else '*Not Available*'
            replied = snipe_message_replied.get(ctx.channel.id, None)

            if snipe_message_attachments.get(ctx.channel.id):
                attachment = enumerate(
                    [i.url for i in snipe_message_attachments.get(ctx.channel.id) if i is not None], start=1
                )
                attachment_text = "".join(f"\n`[{id}]` [Attachment]({url})" for id, url in attachment)
            else:
                attachment_text = ""

            embed.add_field(name="Content", value=f"{content}\n{attachment_text}", inline=False)

            if replied:
                embed.add_field(name="Replied To", value=f"[{replied.author}]({replied.jump_url})", inline=False)

            time_diff = datetime.datetime.now() - snipe_message_time.get(ctx.channel.id, datetime.datetime.min)
            k = int(time_diff.total_seconds())
            deleted = converters.time(k)

            embed.set_footer(text=f"Deleted {deleted} ago.", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except KeyError:
            await ctx.send(f"There are no messages to snipe.", ephemeral=True)

    
    @commands.hybrid_command(name="firstmessage", aliases=['firstmsg'],
                             description="Shows the first message of the channel.")
    async def first_message(self, ctx, channel: typing.Optional[discord.TextChannel]):
        channel = ctx.channel or channel

        async for message in channel.history(limit=1, oldest_first=True):
            await ctx.send(f"First message sent in {channel.mention} is {message.jump_url}")
            break
        
    




    @commands.hybrid_command(aliases=['jumbo'])
    async def enlarge(self, ctx, emojis: commands.Greedy[discord.Emoji]):
        if emojis == []:
            for e in emojis:
                emojis = get_message_emojis(e)
            return await ctx.send(f"Emoji was not found.")
        

        embeds = []
        for chunk in discord.utils.as_chunks(emojis, 1):
            embed = discord.Embed(color=config.color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Powered By Neon HQ", icon_url=self.bot.user.display_avatar.url)

            for emoji in chunk:
                embed.set_image(url=emoji.url)
            embeds.append(embed)

        view = PaginatorView(embeds, ctx.bot, ctx.author)
        if len(embeds) > 1:
            view.message = await ctx.send(embed=view.initial, view=view)
        else:
            view.message = await ctx.send(embed=view.initial)

   
    @commands.hybrid_command(usage="<emoji> [name]", description="Steals emoji from other servers.")
    async def steal(self, ctx: commands.Context, emojis, name=None):
        regex = r'\b((?:https?|ftp)://[^\s/$.?#].[^\s]*)\b'
        matches = re.findall(regex, emojis)
        name = name or 'stolen_emoji_raze'

        if matches:
            async with aiohttp.ClientSession() as ses:
                async with ses.get(emojis) as r:
                    try:
                        bValue = await r.read()
                        if r.status in range(200, 299):
                            emoji = await ctx.guild.create_custom_emoji(name=name, image=bValue)
                            await ctx.send(f"Successfully stolen {emoji}.")
                        else:
                            await ctx.send(f"**{ctx.author}** An error occurred while making this request.")
                    except discord.HTTPException:
                        await ctx.send(f"This file is too big.")
            await ses.close()
        else:
            emojis = get_message_emojis(ctx.message)
            if emojis == []:
                return await ctx.send(f"Unable to add the emoji.")
            async with aiohttp.ClientSession() as ses:
                async with ses.get(emojis[0].url) as r:
                    try:
                        bValue = await r.read()
                        if r.status in range(200, 299):
                            emoji = await ctx.guild.create_custom_emoji(name=name, image=bValue)
                            await ctx.send(f"Successfully stolen {emoji}.")
                        else:
                            await ctx.send(f"**{ctx.author}** An error occurred while making this request.")
                    except discord.HTTPException:
                        await ctx.send(f"This file is too big.")
            await ses.close()

















    




async def setup(bot):
    await bot.add_cog(Utility(bot))