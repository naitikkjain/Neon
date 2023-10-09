from typing import Optional
import discord
from discord.ext import commands, tasks
import pytz, typing, datetime, asyncio

from Extra import config, converters

from paginations.paginator import PaginatorView










class RoleConverter(commands.RoleConverter):
    async def convert(self, ctx: commands.Context, argument: str) -> discord.Role:
        try:
            return await super().convert(ctx, argument)
        except commands.RoleNotFound:
            for role in ctx.guild.roles:
                if argument.lower() in role.name.lower():
                    return role
            raise commands.RoleNotFound(argument)














class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(description="Locks a specfic channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def lock(self, ctx, channel: discord.TextChannel=None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"Successfully locked {channel.mention}.")

    @commands.hybrid_command(description="Unlocks a specfic channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def unlock(self, ctx, channel: discord.TextChannel=None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send(f"Successfully unlocked {channel.mention}.")

    @commands.hybrid_command(description="Locks all the channels of the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    @commands.bot_has_permissions(administrator=True)
    async def lockall(self, ctx, role: discord.Role = None):
        m = await ctx.channel.send(f"Processing the command.")
        channels = [i for i in ctx.guild.channels]
        unlocked_channels = [i for i in channels if i.permissions_for(ctx.guild.default_role).send_messages]

        role = role or ctx.guild.default_role

        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to lock {len(unlocked_channels)} channels for {role.mention}?**", author=ctx.author)

        if con:
            em = discord.Embed(description=f"Locking {len(unlocked_channels)} for {role.mention}.", color=config.color)
            await ctx.send(embed=em)
            notch = 0
            for ch in unlocked_channels:
                await ch.set_permissions(role, send_messages=False)
                notch += 1
            await ctx.send(f"Successfully locked {notch} channels.")
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")

    @commands.hybrid_command(description="Unlocks all the channels of the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    @commands.bot_has_permissions(administrator=True)
    async def unlockall(self, ctx, role: discord.Role = None):
        m = await ctx.channel.send(f"Processing the command.")
        channels = [i for i in ctx.guild.channels]
        locked_channels = [i for i in channels if not i.permissions_for(ctx.guild.default_role).send_messages]

        role = role or ctx.guild.default_role

        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to unlock {len(locked_channels)} channels for {role.mention}?**", author=ctx.author)

        if con:
            em = discord.Embed(description=f"Unlocking {len(locked_channels)} for {role.mention}.", color=config.color)
            await ctx.send(embed=em)
            notch = 0
            for ch in locked_channels:
                await ch.set_permissions(role, send_messages=True)
                notch += 1
            await ctx.send(f"Successfully unlocked {notch} channels.")
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")





    @commands.hybrid_command(description="Hides a specfic channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def hide(self, ctx, channel: discord.TextChannel=None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ctx.send(f"Successfully hidden {channel.mention}.")

    @commands.hybrid_command(description="Unhides a specfic channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def unhide(self, ctx, channel: discord.TextChannel=None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, view_channel=None)
        await ctx.send(f"Successfully unhidden {channel.mention}.")


    @commands.hybrid_command(description="Hides all the channels of the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    @commands.bot_has_permissions(administrator=True)
    async def hideall(self, ctx: commands.Context, role: discord.Role=None):
        m = await ctx.channel.send(f"Processing the command.")
        channels = [i for i in ctx.guild.channels]
        unhidden_channels = [i for i in channels if i.permissions_for(ctx.guild.default_role).view_channel]

        role = role or ctx.guild.default_role

        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to hide {len(unhidden_channels)} channels for {role.mention}?**", author=ctx.author)

        if con:
            em = discord.Embed(description=f"Hiding {len(unhidden_channels)} for {role.mention}.", color=config.color)
            await ctx.send(embed=em)
            notch = 0
            for ch in unhidden_channels:
                await ch.set_permissions(role, view_channel=False)
                notch += 1
            await ctx.send(f"Successfully hidden {notch} channels.")
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")

    @commands.hybrid_command(description="Hides all the channels of the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def unhideall(self, ctx, role: discord.Role = None):
        m = await ctx.channel.send(f"Processing the command.")
        channels = [i for i in ctx.guild.channels]
        hidden_channels = [i for i in channels if not i.permissions_for(ctx.guild.default_role).view_channel]

        role = role or ctx.guild.default_role

        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to unhide {len(hidden_channels)} channels for {role.mention}?**", author=ctx.author)

        if con:
            em = discord.Embed(description=f"Unhiding {len(hidden_channels)} for {role.mention}.", color=config.color)
            await ctx.send(embed=em)
            notch = 0
            for ch in hidden_channels:
                await ch.set_permissions(role, view_channel=True)
                notch += 1
            await ctx.send(f"Successfully unhidden {notch} channels.")
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")










    @commands.hybrid_group(invoke_without_command=True, description="Adds role to a user.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    async def role(self, ctx, user: discord.Member, role: RoleConverter):
        if ctx.author != ctx.guild.owner:
            if ctx.author.top_role <= user.top_role:
                await ctx.send(f"Your highest role must be above user's role.")
                return
        if ctx.guild.me.top_role <= user.top_role:
            await ctx.send(f"My highest role is below their top role.")
            return
        if ctx.guild.me.top_role <= role:
            await ctx.send(f"My highest role is below the role.")
            return
        
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send(f"Successfully removed **{role}** from {user}.")
        elif role not in user.roles:
            await user.add_roles(role)
            await ctx.send(f"Successfully added **{role}** to {user}.")
        

    @role.command(name="bots", description="Adds role to only bots.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.bot_has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def bots1(self, ctx, role: RoleConverter):
        m = await ctx.channel.send(f"Processing the command.")
        bots = [member for member in ctx.guild.members if member.bot and role not in member.roles]

        if ctx.guild.me.top_role <= role:
           try: await m.delete()
           except: pass
           return await ctx.send(f"My highest role is below the role.")
        
        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to add {role.mention} to {len(bots)} bots?**", author=ctx.author)

        if con:
            embed = discord.Embed(description=f"Adding the role to {len(bots)} bots.", color=config.color)
            await ctx.send(embed=embed)

            notrole = 0
            forbidden_users = 0
            for bot in bots:
                try:
                   await bot.add_roles(role)
                   notrole += 1
                except discord.Forbidden:
                    forbidden_users += 1
            await ctx.send(f"Successfully added the role to {notrole} bots.\n\n" + "".join(f"Unfotunately, I was unable to add the role to {forbidden_users} bots." if forbidden_users != 0 else ''))
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")

    @role.command(description="Adds role to all the users in the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def all(self, ctx, role: RoleConverter):
        m = await ctx.channel.send(f"Processing the command.")
        users = [i for i in ctx.guild.members if not role in i.roles]

        if ctx.guild.me.top_role <= role:
           try: await m.delete()
           except: pass
           return await ctx.send(f"My highest role is below the role.")
        
        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to add {role.mention} to {len(users)} members?**", author=ctx.author)

        if con:
            embed = discord.Embed(description=f"Adding the role to {len(users)} members.", color=config.color)
            await ctx.send(embed=embed)

            notrole = 0
            forbidden_users = 0
            for user in users:
                try:
                   await user.add_roles(role)
                   notrole += 1
                except discord.Forbidden:
                    forbidden_users += 1
            await ctx.send(f"Successfully added the role to {notrole} members.\n\n" + "".join(f"Unfotunately, I was unable to add the role to {forbidden_users} members." if forbidden_users != 0 else ''))
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")

    @role.command(name="humans", description="Adds role to only humans.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def humans1(self, ctx, role: RoleConverter):
        m = await ctx.channel.send(f"Processing the command.")
        humans = [member for member in ctx.guild.members if not member.bot and role not in member.roles]

        if ctx.guild.me.top_role <= role:
           try: await m.delete()
           except: pass
           return await ctx.send(f"My highest role is below the role.")
    
        
        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to add {role.mention} to {len(humans)} humans?**")

        if con:
            embed = discord.Embed(description=f"Adding the role to {len(humans)} humans.", color=config.color)
            await ctx.send(embed=embed)

            notrole = 0
            forbidden_users = 0
            for user in humans:
                try:
                   await user.add_roles(role)
                   notrole += 1
                except discord.Forbidden:
                    forbidden_users += 1
            await ctx.send(f"Successfully added the role to {notrole} humans.\n\n" + "".join(f"Unfotunately, I was unable to add the role to {forbidden_users} humans." if forbidden_users != 0 else ''))
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")






    

    @commands.hybrid_group(description="Remove role commands.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def rrole(self, ctx, role: RoleConverter):
        m = await ctx.channel.send(f"Processing the command.")
        users = [i for i in ctx.guild.members if not role in i.roles]

        if ctx.guild.me.top_role <= role:
           try: await m.delete()
           except: pass
           return await ctx.send(f"My highest role is below the role.")
    
        
        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to remove {role.mention} from {len(users)} members?**")

        if con:
            embed = discord.Embed(description=f"Removing the role from {len(users)} members.", color=config.color)
            await ctx.send(embed=embed)

            notrole = 0
            forbidden_users = 0
            for user in users:
                try:
                   await user.remove_roles(role)
                   notrole += 1
                except discord.Forbidden:
                    forbidden_users += 1
            await ctx.send(f"Successfully removed the role from {notrole} members.\n\n" + "".join(f"Unfotunately, I was unable to remove the role from {forbidden_users} members." if forbidden_users != 0 else ''))
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")


    @rrole.command(name="humans", description="Removes role from humans.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def humans2(self, ctx, role: RoleConverter):
        m = await ctx.channel.send(f"Processing the command.")
        humans = [i for i in ctx.guild.members if not i.bot and role not in i.roles]

        if ctx.guild.me.top_role <= role:
           try: await m.delete()
           except: pass
           return await ctx.send(f"My highest role is below the role.")
    
        
        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to remove {role.mention} from {len(humans)} humans?**")

        if con:
            embed = discord.Embed(description=f"Removing the role from {len(humans)} humans.", color=config.color)
            await ctx.send(embed=embed)

            notrole = 0
            forbidden_users = 0
            for user in humans:
                try:
                   await user.remove_roles(role)
                   notrole += 1
                except discord.Forbidden:
                    forbidden_users += 1
            await ctx.send(f"Successfully removed the role from {notrole} humans.\n\n" + "".join(f"Unfotunately, I was unable to remove the role from {forbidden_users} members." if forbidden_users != 0 else ''))
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")
 
    @rrole.command(name="bots", description="Removes role from humans.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def bots2(self, ctx, role: RoleConverter):
        m = await ctx.channel.send(f"Processing the command.")
        bots = [i for i in ctx.guild.members if i.bot and role not in i.roles]

        if ctx.guild.me.top_role <= role:
           try: await m.delete()
           except: pass
           return await ctx.send(f"My highest role is below the role.")
    
        
        try: await m.delete()
        except: pass
        con = await ctx.confirm(message=f"**Are you sure you want to remove {role.mention} from {len(bots)} bots?**")

        if con:
            embed = discord.Embed(description=f"Removing the role from {len(bots)} bots.", color=config.color)
            await ctx.send(embed=embed)

            notrole = 0
            forbidden_users = 0
            for user in bots:
                try:
                   await user.add_roles(role)
                   notrole += 1
                except discord.Forbidden:
                    forbidden_users += 1
            await ctx.send(f"Successfully remove the role from {notrole} bots.\n\n" + "".join(f"Unfotunately, I was unable to remove the role from {forbidden_users} bots." if forbidden_users != 0 else ''))
        else:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")













    @commands.hybrid_command(description="Changes nickname of users")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_nicknames=True))
    async def nick(self, ctx, member: discord.Member, *, nick: str = None):
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"My highest role is below their top role.")
        
        nick = nick or None
        await member.edit(nick=nick)
        await ctx.send(f"Successfully changed their nick.")

    @commands.command(description=f"Kick a member if they are breaking rules.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(kick_members=True))
    async def kick(self, ctx, user : discord.Member, *, reason=None):
        reason = reason or "No reason provided."
        if ctx.author.top_role <= user.top_role or not user.guild.owner:
            return await ctx.send(f"You cannot kick them.")
        if ctx.guild.me.top_role.position <= user.top_role.position:
            return await ctx.send(f"My highest role is below their role.")
        if user == ctx.author:
            return await ctx.send(f"You cannot kick yourself.")
        
        else:
            try:
                await user.send(f"You have been **Kicked** from {ctx.guild.name}\n**__Reason__**: `{reason}`")
            except:
                pass
            await ctx.guild.kick(user=user, reason=f"By {ctx.author}: {reason}")
            await ctx.message.add_reaction(config.Tick)
            await ctx.send(f"Successfully kicked **{user}** `{reason}`")

    @commands.hybrid_command(aliases=['fuckban', 'hackban', 'fuckyou'], description=f"Ban a user if they are breaking rules again and again.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=None):
        reason = reason or "[No reason]"

        if user in ctx.guild.members:
            user = ctx.guild.get_member(user.id)

            if ctx.author is not ctx.guild.owner:
                if ctx.author.top_role > user.top_role:
                    if user.top_role < ctx.guild.me.top_role:
                        await ctx.message.add_reaction(config.Tick)
                        try:
                            await user.send(f"You have been **Banned** from {ctx.guild.name}\n**__Reason__**: `{reason}`")
                        except:
                            pass
                        await ctx.guild.ban(user=user, reason=f"By {ctx.author}: {reason}", delete_message_seconds=0)
                        await ctx.send(f"Successfully banned **{user}** `{reason}`")
                    else:
                        return await ctx.send(f"My highest role is below their top role.")
                else:
                    return await ctx.send(f"You don't have permission to do it.")
            else:
                if user.top_role < ctx.guild.me.top_role:
                    await ctx.message.add_reaction(config.Tick)
                    try:
                        await user.send(f"You have been **Banned** from {ctx.guild.name}\n**__Reason__**: `{reason}`")
                    except:
                        pass
                    await ctx.guild.ban(user=user, reason=f"By {ctx.author}: {reason}", delete_message_seconds=0)
                    await ctx.send(f"Successfully banned **{user}** `{reason}`")
                else:
                    return await ctx.send(f"My highest role is below their top role.")

        else:
            try:
                await user.send(f"You have been **Banned** from {ctx.guild.name}\n**__Reason__**: `{reason}`")
            except:
                pass
            await ctx.guild.ban(user=user, reason=f"By {ctx.author}: {reason}", delete_message_seconds=0)
            await ctx.message.add_reaction(config.Tick)
            await ctx.send(f"Successfully banned **{user}** `{reason}`")

    @commands.command(description="Unban a user using this command.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason=None):
        reason = reason or "[No reason]"
        try:
           await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            return await ctx.send(f"That user is not banned.")
        
        await ctx.guild.unban(user=user, reason=f"By {ctx.author}: {reason}")
        await ctx.message.add_reaction(config.Tick)
        await ctx.send(f"Successfully unbanned **{user}** `{reason}`")

    @commands.hybrid_command(description="Warn a user if they are breaking rules. | Warnings aren't stored")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    async def warn(self, ctx, member: discord.Member, *, reason):
        if ctx.author.top_role <= member.top_role or not member.guild.owner:
            return await ctx.channel.send(f"You cannot warn them.")
        elif member.id == ctx.author.id:
            return await ctx.channel.send(f"You cannot warn yourself.")
        elif member.bot:
            return await ctx.channel.send(f"I cannot warn my fellow mates.")
        try:
            await member.send(f"You have been **Warned** in **{ctx.guild.name}**\n**__Reason__**: `{reason}`.")
            await ctx.send(f"Successfully warned **{member}** `{reason}`")
        except:
            await ctx.send(f"Their DM is closed.")
        

    async def timeout(self, ctx: commands.Context, member: discord.Member, delta, reason):
        if member.is_timed_out():
          return await ctx.send(f"The user is already timed out.")

        if ctx.author is not ctx.guild.owner:
            if ctx.author.top_role > member.top_role:
                await member.timeout(delta, reason=f"By {ctx.author}: {reason}")
                await ctx.send(f"Successfully muted **{member}** `{reason}`.")
                return
            else:
                return await ctx.send(f"You don't have permission to do it.", delete_after=5)
                
        await member.timeout(delta, reason=f"By {ctx.author}: {reason}")
        await ctx.send(f"Successfully muted **{member}** `{reason}`.")

    @commands.command(description="Stops a user from writing in channels.", aliases=['stfu', 'timeout', 'tempmute'])
    @commands.check_any(commands.is_owner(),commands.has_permissions(moderate_members=True))
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration, *, reason: str = None):
        reason = reason or 'No reason provided.'

        if ctx.author is member:
            return await ctx.send(f"You cannot mute yourself.")
        
        time_ = converters.TimeConvert(duration)
        delta = datetime.timedelta(seconds=time_)

        if delta == -1:
            return await ctx.send(f"{config.Warn} | **{ctx.author}** Invalid unit. `?mute <member> 30m spamming`.")
        
        await self.timeout(ctx, member, delta, reason)


    async def remove_timeout(self, ctx: commands.Context, member: discord.Member, reason):
        if ctx.author is not ctx.guild.owner:
            if ctx.author.top_role > member.top_role:
                await member.timeout(None, reason=reason)
                await ctx.send(f"Successfully unmuted {member} `{reason}`.")
            else:
                await ctx.send(f"You don't have permission to do it.", delete_after=5)
        else:
            await member.timeout(None, reason=reason)
            await ctx.send(f"Successfully unmuted {member} `{reason}`.")

    @commands.hybrid_command(description="Unmutes a user so that they can write in the channels.", aliases=['unshut'])
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        reason = reason or 'No reason provided.'

        if ctx.author is member:
            return await ctx.send(f"You cannot unmute yourself.")
        
        if not member.is_timed_out():
          return await ctx.send(f"The user is not timed out.")
        
        await self.remove_timeout(ctx, member, reason)

    
    @commands.command(description="Deletes a channel")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def delchannel(self, ctx: commands.Context, channel: typing.Optional[discord.CategoryChannel]):
        channel = channel or ctx.channel

        confirm = await ctx.confirm(message=f"**Are you sure you want to delete {channel.mention}?**", author=ctx.author)

        if confirm:
            await ctx.channel.delete()
        elif not confirm:
            await ctx.send(f"{ctx.author.mention} command execution cancelled.")
        else:
            await ctx.send(f"{ctx.author.mention} Okay, This channel will not be deleted.")

    @commands.hybrid_command(description="Gives a role to all the provided users.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def giverole(self, ctx, role: RoleConverter, users: commands.Greedy[discord.Member]):

        if ctx.guild.me.top_role < role:
            return await ctx.send(f"Your top role must be above the role.", delete_after=5)

        if ctx.author != ctx.guild.owner:
            if ctx.author.top_role > role:
                for user in users:
                    if user.top_role < ctx.author.top_role:
                        for user in users:
                            await user.add_roles(role)
                        await ctx.send(f"Successfully added the role to all the listed users.")
                    else:
                        await ctx.send(f"Your top role must be above all the user's top role.", delete_after=5)
            else:
                await ctx.send(f"Your top role must be above the role.")
        else:
            for user in users:
                if user.top_role < ctx.author.top_role:
                    for user in users:
                        await user.add_roles(role)
                    await ctx.send(f"Successfully added the role to all the listed users.")


    @commands.hybrid_command(description="Shows logs of audit log.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.is_owner(), commands.has_permissions(view_audit_log=True))
    @commands.bot_has_permissions(view_audit_log=True)
    async def audit(self, ctx, limit):
        try:
            int(limit)
        except TypeError:
            return await ctx.send(f"Invalid limit.")
        
        await ctx.typing()
        embeds = []

        entry = [entry async for entry in ctx.guild.audit_logs(limit=int(limit))]


        for chunk in discord.utils.as_chunks(entry, 5):
            embed = discord.Embed(color=config.color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url, url=f'https://discord.com/users/{ctx.author.id}')
            embed.description = ''

            for entry in chunk:
                user = entry.user
                target = entry.target
                action = str(entry.action.name).replace('_', ' ').title()
                time = f'<t:{round(entry.created_at.timestamp())}:R>'
                entry_id = entry.id


                embed.description += f'\n**Action By:** {user} ({user.mention})\n**Target:** {target}\n**Action:** {action}\n**Time:** {time}\n**ID:** {entry_id}\n\n'
            embeds.append(embed)

        view = PaginatorView(embeds, self.bot, ctx.author)
        if len(embeds) > 1:
            view.message = await ctx.send(embed=view.initial, view=view)
        else:
            view.message = await ctx.send(embed=view.initial)
        




































































async def setup(bot):
    await bot.add_cog(Moderation(bot))