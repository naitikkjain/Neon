from typing import Optional
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Button, View
from contextlib import redirect_stdout
from prettytable import PrettyTable

import asyncio, os, random, sys, io, textwrap, traceback, discord, datetime, aiohttp, psutil, json

from paginations.paginator import PaginatorView
from Extra import config


class PanelView(View):
    def __init__(self, bot, author):
        self.bot = bot
        self.author = author

        super().__init__(timeout=180)

    @discord.ui.button(label="Bot Info")
    async def callback1(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interation.", ephemeral=True)

        mem = psutil.virtual_memory()
        total_mem = round(mem.total / (1024 ** 3), 1)
        used_mem = round(mem.used / (1024 ** 3), 1)
        available_mem = round(mem.available / (1024 ** 3), 1)

        dis = psutil.disk_usage('/')
        total_dis = round(dis.total / (1024 ** 3), 1)
        used_dis = round(dis.used / (1024 ** 3), 1)
        avail_dis = round(dis.free / (1024 ** 3), 1)
        per_dis = dis.percent

        embed = discord.Embed(
            color=config.color
        )
        embed.add_field(
            name="Core Statics",
            value=f"```ahk\nCores: {psutil.cpu_count()}\nCPU Usage: {psutil.cpu_percent()}%\nMemory: {used_mem}/{total_mem} GB\nMemory Available: {available_mem} GB\nDisk: {used_dis}/{total_dis} GB ({per_dis} %)\nDisk Available: {avail_dis} GB```",
            inline=False
        )
        embed.add_field(
            name="Bot Cache Info",
            value=f"```ahk\nGuilds: {len(self.bot.guilds)}\nUsers: {len(self.bot.users)}\nLatency: {round(self.bot.latency * 1000)} MS\nChannels: {len(list(self.bot.get_all_channels()))}```",
            inline=False
        )
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.display_avatar.url
        )
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Get User")
    async def UserPanel(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interation.", ephemeral=True)

        await interaction.response.send_modal(
            UserInfoModal(message=self.message, author=self.author)
        )

    async def on_timeout(self):
        if self.message is None: return
        for i in self.children:
            i.disabled = True
        await self.message.edit(view=self)


class UserInfoPanel(discord.ui.View):
    def __init__(self, author, msg):
        self.author = author
        self.msg = msg
        super().__init__(timeout=180)

    @discord.ui.button(label="Main Menu", style=discord.ButtonStyle.primary)
    async def MainMenuCall(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interation.", ephemeral=True)

        await interaction.response.edit_message(embed=self.msg.embeds[0],
                                                view=PanelView(bot=interaction.client, author=self.author))

    @discord.ui.button(label="Add No Prefix", style=discord.ButtonStyle.green)
    async def NpAdd(self, interaction: discord.Interaction, btn: discord.ui.Button):
        ...

    @discord.ui.button(label="Remove No Prefix", style=discord.ButtonStyle.red)
    async def NpRemove(self, interaction: discord.Interaction, btn: discord.ui.Button):
        ...

class UserInfoModal(discord.ui.Modal):
    def __init__(self, message, author):
        self.message = message
        self.author = author
        super().__init__(title="User")

        self.name = discord.ui.TextInput(label="Please Enter ID")
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interation.", ephemeral=True)
        try:
            user = await interaction.client.fetch_user(int(self.name.value))
        except discord.NotFound:
            return await interaction.response.send_message("Not Found", ephemeral=True)

        cached = interaction.client.get_user(int(self.name.value))

        c = await interaction.client.db.cursor()
        await c.execute("SELECT user_id FROM Blacklisted WHERE user_id = ?", (user.id,))
        bl = await c.fetchone()
        await c.execute("SELECT users FROM Np WHERE users = ?", (user.id,))
        np = await c.fetchone()

        embed = discord.Embed(
            color=config.color
        )
        embed.add_field(
            name="User Info",
            value=f">>> Mention: <@{user.id}>\nName: {user}\nID: {user.id}\nCached?: {config.Tick if cached is not None else config.Cross}\nAccount Created: <t:{round(user.created_at.timestamp())}:R>\n\n",
            inline=True
        )
        embed.add_field(
            name="Statics",
            value=f">>> Blacklisted: {config.Tick if bl is not None else config.Cross}\nNo Prefix: {config.Tick if np is not None else config.Cross}\n",
            inline=False
        )
        embed.set_thumbnail(
            url=user.display_avatar.url
        )
        if user.banner:
            embed.set_image(
                url=user.banner.url
            )
        view = UserInfoPanel(author=self.author, msg=self.message)
        await interaction.response.edit_message(embed=embed, view=view)


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def panel(self, ctx):
        embed = discord.Embed(
            description="NeoN Control Panel",
            color=config.color
        )

        view = PanelView(bot=self.bot, author=ctx.author)
        view.message = await ctx.send(embed=embed, view=view)

    @commands.command(description="Restarts the bot.", aliases=['rs'], hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        button = Button(style=discord.ButtonStyle.green, label="Yes")
        button2 = Button(style=discord.ButtonStyle.red, label="No")

        async def callback(int: discord.Interaction):
            if int.user != ctx.author:
                await int.response.send_message(f"It's not your interaction.")
                return
            await int.response.edit_message(content="Restarting.", view=None)
            await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Loading."))

            await asyncio.sleep(1)
            os.execv(sys.executable, ['python'] + sys.argv)

        async def callback2(int: discord.Interaction):
            if int.user != ctx.author:
                await int.response.send_message(f"It's not your interaction.", ephemeral=True)
                return
            await int.response.edit_message(content="Cancelled.", view=None)

        button.callback = callback
        button2.callback = callback2
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)
        await ctx.send("Are you sure?", view=view)

    @commands.group(hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def owner(self, ctx):
        await ctx.send_help(ctx.command)

    @owner.command(hidden=True, name="add")
    @commands.is_owner()
    async def add3(self, ctx, user: discord.User):
        await ctx.typing()
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Owner")
        re = await c.fetchall()

        if re != []:
            ids = [int(i[0]) for i in re]
            if user.id in ids:
                await ctx.send("That user is already owner.")
                return

        await c.execute("INSERT INTO Owner(user_id) VALUES(?)", (user.id,))
        await ctx.send(f"Added **{user} ({user.id})** to owners.")
        await self.bot.db.commit()

    @owner.command(hidden=True, name="remove", aliases=['rmv'])
    @commands.is_owner()
    async def remove3(self, ctx, user: discord.User):
        await ctx.typing()
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Owner")
        re = await c.fetchall()

        if re == []:
            await ctx.send("There are no owners.")
            return
        ids = [int(i[0]) for i in re]
        if user.id not in ids:
            await ctx.send("That user is not owner.")
            return

        await c.execute("DELETE FROM Owner WHERE user_id = ?", (user.id,))
        await ctx.send(f"Removed **{user} ({user.id})** from owners.")
        await self.bot.db.commit()

    @owner.command(hidden=True, name="list", aliases=['show'])
    @commands.is_owner()
    async def list3(self, ctx):
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Owner")
        re = await c.fetchall()

        if re == []:
            await ctx.send("There are no owners.")
            return

        ids_ = [int(i[0]) for i in re]

        ids = []
        for i in ids_:
            z = await self.bot.fetch_user(i)
            ids.append(z)
        enumerate(ids, start=1)

        embeds = []
        embed = discord.Embed(description="```\n", color=config.color)
        embed.set_author(
            name=ctx.author,
            icon_url=ctx.author.display_avatar.url
        )
        chunk = discord.utils.as_chunks(ids, 20)
        for n, user in chunk:
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
            embed.description += "".join(f'[{n}] {i}\t({i.id})\n\n' for i in user)

            embed.description += '```'
            embeds.append(embed)

        view = PaginatorView(embeds, bot=self.bot, author=ctx.author)
        if len(embeds) > 1:
            return view.message == await ctx.send(embed=view.initial, view=view)

        view.message = await ctx.send(embed=view.initial)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sql(self, ctx, *, query: str):
        if not query.strip().lower().startswith("select"):
            try:
                await self.bot.db.execute(query)
                await self.bot.db.commit()
                await ctx.send("Database updated successfully.")
            except Exception as e:
                await ctx.send(f"An error occurred while updating the database: \n```sql\n{e}```")
            return

        try:
            cursor = await self.bot.db.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = await cursor.fetchall()
        except Exception as e:
            await ctx.send(f"An error occurred while executing the query: \n```sql\n{e}```")
            return

        if not rows:
            await ctx.send('No results found.')
            return

        table = PrettyTable()
        table.field_names = columns
        table.align = "l"

        for row in rows:
            table.add_row(row)

        await ctx.send(f"```sql\n{table}\n```")

    @commands.group(aliases=['nopre', 'np'], description="No prefix commands.", invoke_without_command=True)
    @commands.check_any(config.owner(), commands.is_owner())
    async def noprefix(self, ctx):
        await ctx.send_help(ctx.command)

    @noprefix.command(description="Adds user to no prefix.")
    @commands.check_any(config.owner(), commands.is_owner())
    async def add(self, ctx, user: discord.User):
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT users FROM Np")
        result = await cursor.fetchall()

        if user.id not in [int(i[0]) for i in result]:
            await ctx.typing()
            await cursor.execute(f"INSERT INTO Np(users) VALUES(?)", (user.id,))
            await ctx.send(f"Successfully added {user} to no prefix.")
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(
                    url="https://discord.com/api/webhooks/1138140437882880160/75vOXl7v6TYluC91DmK-zmBzDFF5NSzNNv0T4k_hbW-Fhx3e4aTOCFPYquIPXgYMSut3",
                    session=session)

                embed = discord.Embed(title="No Prefix Added",
                                      description=f"**Author:** {ctx.author}\n**Author ID:** {ctx.author.id}\n**Added To:** {user} ({user.id})\n\n**Guild** {ctx.guild.name}\n**Guild ID:** {ctx.guild.id}\n\n**Message:**\n```\n{ctx.message.content}```",
                                      color=config.color)
                embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                await webhook.send(embed=embed)
        else:
            await ctx.send(f"That user is already in no prefix.")

        await self.bot.db.commit()

    @noprefix.command(description="Removes no prefix from a user.", aliases=['rmv'])
    @commands.check_any(config.owner(), commands.is_owner())
    async def remove(self, ctx, user: discord.User):
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT users FROM Np")
        result = await cursor.fetchall()

        if user.id in [int(i[0]) for i in result]:
            await ctx.typing()
            await cursor.execute(f"DELETE FROM Np WHERE users = ?", (user.id,))
            await ctx.send(f"Successfully removed {user} from no prefix.")
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(
                    url="https://discord.com/api/webhooks/1138140437882880160/75vOXl7v6TYluC91DmK-zmBzDFF5NSzNNv0T4k_hbW-Fhx3e4aTOCFPYquIPXgYMSut3",
                    session=session)

                embed = discord.Embed(title="No Prefix Removed",
                                      description=f"**Author:** {ctx.author}\n**Author ID:** {ctx.author.id}\n**Removed From:** {user} ({user.id})\n\n**Guild** {ctx.guild.name}\n**Guild ID:** {ctx.guild.id}\n\n**Message:**\n```\n{ctx.message.content}```",
                                      color=config.color)
                embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                await webhook.send(embed=embed)
        else:
            await ctx.send(f"That user isn't in no prefix.")

        await self.bot.db.commit()

    @noprefix.command(description="Shows the list of no prefix users.", aliases=['show'])
    @commands.check_any(config.owner(), commands.is_owner())
    async def list(self, ctx):
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT users FROM Np")
        result = await cursor.fetchall()

        embeds = []
        users_ = [int(i[0]) for i in result]

        users = []
        for i in users_:
            u = await self.bot.fetch_user(i)
            users.append(u)

        chunked = discord.utils.as_chunks(enumerate(users, start=1), 20)

        for chunk in chunked:
            embed = discord.Embed(description="```\n", color=config.color)
            embed.set_author(name=ctx.author,
                             icon_url=ctx.author.display_avatar.url)

            for i, user in chunk:
                if user is None: await cursor.execute("DELETE FROM Np WHERE users = ?", (int(user),))
                embed.description += "".join([f"[{i}]  {user}\t({user.id})\n"])
            embed.description += '```'
            embeds.append(embed)

        if len(embeds) > 1:
            view = PaginatorView(embeds, bot=self.bot, author=ctx.author)
            view.message = await ctx.send(embed=view.initial, view=view)
        else:
            view2 = PaginatorView(embeds, bot=self.bot, author=ctx.author)
            view2.message = await ctx.send(embed=view2.initial)
        await self.bot.db.commit()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def gleave(self, ctx, guild: discord.Guild):
        button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        button2 = discord.ui.Button(label="No", style=discord.ButtonStyle.danger)

        async def callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(f"It's not your interaction.", ephemeral=True)
                return
            try:
                await guild.leave()
                await interaction.response.edit_message(content=f"Successfully left {guild.name}", view=None)
            except Exception as e:
                await ctx.send(f"Error:```\n{e}```")

        async def callback2(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(f"It's not your interaction.", ephemeral=True)
                return
            await interaction.response.edit_message(content="Cancelled", view=None)

        button.callback = callback
        button2.callback = callback2
        view = discord.ui.View(timeout=None)
        view.add_item(button)
        view.add_item(button2)
        await ctx.send("Are you sure?", view=view)

    @commands.group(aliases=['bl'], hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def blacklist(self, ctx):
        await ctx.send_help(ctx.command)

    @blacklist.group(hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def guild(self, ctx):
        await ctx.send_help(ctx.command)

    @blacklist.group(hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def user(self, ctx):
        await ctx.send_help(ctx.command)

    @user.command(name="add", hidden=True)
    @commands.check_any(config.owner(), commands.is_owner())
    async def add2(self, ctx, user: discord.User, *, reason=None):
        reason = reason or 'None'
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Blacklisted")
        ids_raw = await c.fetchall()

        if ids_raw != []:
            ids = [int(i[0]) for i in ids_raw]
            if user.id in ids:
                await ctx.send("That user is already blacklisted.")
                return

        time = round(datetime.datetime.now().timestamp())

        await c.execute("INSERT INTO Blacklisted(user_id, author_id, reason, time) VALUES(?, ?, ?, ?)",
                        (user.id, ctx.author.id, reason, time))
        await ctx.send(f"Blacklisted **{user} ({user.id})**")

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                url="https://discord.com/api/webhooks/1138140545294798848/HBLp_pcnlSncvj52AhMaocRo1FRt9LVUfXW1b28SR_0cHYc9t_UkyAqyJqgxZaFMgYQE",
                session=session)
            embed = discord.Embed(
                title="Blacklist Added",
                description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**User:** {user} ({user.id})\n**Time:** <t:{time}:R> (<t:{time}:D>)\n**Reason:**\n```\n{reason}```",
                color=config.color
            )
            await webhook.send(embed=embed)

        await self.bot.db.commit()

    @user.command(name="remove", aliases=['rmv'], hidden=True)
    @commands.check_any(config.owner(), commands.is_owner())
    async def remove2(self, ctx, user: discord.User, *, reason=None):
        reason = reason or 'None'
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Blacklisted")
        ids_raw = await c.fetchall()

        if ids_raw != []:
            ids = [int(i[0]) for i in ids_raw]
            if user.id not in ids:
                await ctx.send("That user is not blacklisted.")
                return

        time = round(datetime.datetime.now().timestamp())

        await c.execute("DELETE FROM Blacklisted WHERE user_id = ?", (user.id,))
        await ctx.send(f"Unblacklisted **{user} ({user.id})**")

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                url="https://discord.com/api/webhooks/1138140545294798848/HBLp_pcnlSncvj52AhMaocRo1FRt9LVUfXW1b28SR_0cHYc9t_UkyAqyJqgxZaFMgYQE",
                session=session)
            embed = discord.Embed(
                title="Blacklist Removed",
                description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**User:** {user} ({user.id})\n**Time:** <t:{time}:R> (<t:{time}:D>)\n**Reason:**\n```\n{reason}```",
                color=config.color
            )
            await webhook.send(embed=embed)
        await self.bot.db.commit()

    @guild.command(name="add", hidden=True)
    @commands.check_any(commands.is_owner())
    async def bl_add(self, ctx, guild: discord.Guild, *, reason=None):
        reason = reason or 'None'

        c = await self.bot.db.cursor()
        await c.execute("SELECT guild_id FROM G_bl")
        ids_raw = await c.fetchall()

        if ids_raw != []:
            ids = [int(i[0]) for i in ids_raw]
            if guild.id in ids:
                await ctx.send("That guild is already blacklisted.")
                return

        time = round(datetime.datetime.now().timestamp())

        await c.execute("INSERT INTO G_bl(guild_id, author_id, reason, time) VALUES(?, ?, ?, ?)",
                        (guild.id, ctx.author.id, reason, time))
        await ctx.send(f"Blacklisted **{guild} ({guild.id})**")

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                url="https://discord.com/api/webhooks/1138140545294798848/HBLp_pcnlSncvj52AhMaocRo1FRt9LVUfXW1b28SR_0cHYc9t_UkyAqyJqgxZaFMgYQE",
                session=session)
            embed = discord.Embed(
                title="Blacklist Added",
                description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**Guild:** {guild} ({guild.id})\n**Time:** <t:{time}:R> (<t:{time}:D>)\n**Reason:**\n```\n{reason}```",
                color=config.color
            )
            await webhook.send(embed=embed)

        await self.bot.db.commit()

    @guild.command(name="remove", aliases=['rmv'], hidden=True)
    @commands.check_any(commands.is_owner())
    async def bl_remove(self, ctx, guild: discord.Guild, *, reason=None):
        reason = reason or 'None'
        c = await self.bot.db.cursor()
        await c.execute("SELECT guild_id FROM G_bl")
        ids_raw = await c.fetchall()

        if ids_raw != []:
            ids = [int(i[0]) for i in ids_raw]
            if guild.id not in ids:
                await ctx.send("That guild is not blacklisted.")
                return

        time = round(datetime.datetime.now().timestamp())

        await c.execute("DELETE FROM G_bl WHERE guild_id = ?", (guild.id,))
        await ctx.send(f"Unblacklisted **{guild} ({guild.id})**")

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                url="https://discord.com/api/webhooks/1138140545294798848/HBLp_pcnlSncvj52AhMaocRo1FRt9LVUfXW1b28SR_0cHYc9t_UkyAqyJqgxZaFMgYQE",
                session=session)

            embed = discord.Embed(
                title="Blacklist Removed",
                description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**User:** {guild} ({guild.id})\n**Time:** <t:{time}:R> (<t:{time}:D>)\n**Reason:**\n```\n{reason}```",
                color=config.color
            )
            await webhook.send(embed=embed)
        await self.bot.db.commit()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def lockdown(self, ctx):
        with open('DB/lockdown.json', 'r') as f:
            data = json.load(f)

        if data['state']:
            data['state'] = False
        else:
            data['state'] = True

        with open('DB/lockdown.json', 'w') as f:
            json.dump(data, f, indent=4)

        if data['state']:
            await ctx.send(f"Unlocked the bot.")
        else:
            await ctx.send("Locked the bot.")


async def setup(bot):
    await bot.add_cog(Owner(bot))