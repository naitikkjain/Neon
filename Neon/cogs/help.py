from typing import Any, Optional
import discord
from discord.ext import commands
import datetime, pytz
from discord.interactions import Interaction
from discord.ui import Button, Select, View
import aiosqlite, sqlite3
from difflib import get_close_matches



from paginations.paginator import PaginatorView
from Extra import config






class SearchModal(discord.ui.Modal):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__(title="User")

        self.name = discord.ui.TextInput(label="Please Enter Command Name")
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        command = self.bot.get_command(self.name.value)
        if command is None:
            matches = get_close_matches(self.name.value, [i.qualified_name for i in self.bot.commands if not i.hidden])

            if matches == []:
                return await interaction.response.send_message(f"Command `{self.name.value}` not found.", ephemeral=True)
            else:
                match_list = '\n'.join(f"`[{i}]` {z}" for i, z in enumerate(matches, 1))
                return await interaction.response.send_message(f"Command `{self.name.value}` not found.\n\nDid you mean:\n{match_list}", ephemeral=True)

        blue_block = "```css\n<> - Required Argument | () - Optional Argument\n```"
        embed = discord.Embed(
            title=f"Information of {command.name}",
            description=blue_block,
            color=config.color
        )
        embed.add_field(name="Command Name", value=f"```{command.name}```", inline=False)
        
        if isinstance(command, commands.Group):
            embed.add_field(name="Command Aliases", value="```None```", inline=False)
        else:
            embed.add_field(name="Command Aliases", value=f"```{', '.join(command.aliases)}```", inline=False)
        
        embed.add_field(name="Command Category", value=f"```{command.cog_name}```", inline=False)
        embed.set_footer(text="Developed with ❤️ by Sky..!!")

        await interaction.response.send_message(embed=embed, ephemeral=True)



class SearchButton(discord.ui.Button):
    def __init__(self, author: discord.Member, bot):
        self.author = author
        self.bot = bot
        super().__init__(label="Command Search", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author: 
            return await interaction.response.send_message(f"This cannot be controlled by you.", ephemeral=True)
        
        await interaction.response.send_modal(SearchModal(self.bot))





















class HelpCommand(commands.HelpCommand):

  async def send_bot_help(self, mapping):
    
    

    self.embed = discord.Embed(description=f"""Hey!! {self.context.author.mention} 
• My prefix for this server is `&`
• Total Commands {len(self.context.bot.commands)}
• [Get Raze]({config.Invite}) | [Support Server]({config.Support})
• Type `&help <command | module>` for more info.

""", color=config.color)
    
    self.embed.add_field(
        name="__Main__",
        value=f"**<:raze_moderation:1138137003901329508> : Moderation\n<:raze_giveaway:1138137232885166161> : Giveaway\n<:raze_ticket:1138137446832418856> : Ticket\n<:raze_utility:1138137827910107259> : Utility\n<:raze_welcome:1138138018918703246> : Welcome**"
    )
    self.embed.add_field(
        name="__Extra__",
        value=f"**<:raze_ar:1138138209537249370> : Auto Responder\n<:raze_image:1138138386725601341> : Media\n<:raze_voice:1138138687826313278> : Voice Command\n<:raze:1138139190106796114> : Information**"
    )
    
    class HelpPanel(discord.ui.View):
        def __init__(self, author, embed):
            self.author = author
            self.embed = embed
            super().__init__(timeout=120)

        @discord.ui.select(placeholder="Choose a menu for commands.",
                        options=[
            discord.SelectOption(label="Home", emoji="<:raze_home:1138139791108620320>"),
            discord.SelectOption(label="Moderation", emoji="<:raze_moderation:1138137003901329508>"),
            discord.SelectOption(label="Giveaway", emoji="<:raze_giveaway:1138137232885166161>"),
            discord.SelectOption(label="Ticket", emoji="<:raze_ticket:1138137446832418856>"),
            discord.SelectOption(label="Utility", emoji="<:raze_utility:1138137827910107259>"),
            discord.SelectOption(label="Welcome", emoji="<:raze_welcome:1138138018918703246>"),

            discord.SelectOption(label="Auto Responder", emoji="<:raze_ar:1138138209537249370>"),
            discord.SelectOption(label="Media", emoji="<:raze_image:1138138386725601341>"),
            discord.SelectOption(label="Voice Command", emoji="<:raze_voice:1138138687826313278>"),
            discord.SelectOption(label="Bot", emoji="<:raze:1138139190106796114>")
            ])
        async def callback(self, interaction: discord.Interaction, select: Select):
            if interaction.user != self.author:
                await interaction.response.send_message(content=f"This interaction cannot be controlled by you.", ephemeral=True)
                return
            if select.values[0] == "Home":
                await interaction.response.edit_message(embed=self.embed, view=view)

            


            if select.values[0] == "Moderation":
                cog = interaction.client.get_cog("Moderation")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed, view=view)

            if select.values[0] == "Giveaway":
                cog = interaction.client.get_cog("Giveaway")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed, view=view)

            if select.values[0] == "Ticket":
                cog = interaction.client.get_cog("Ticket")
                embed = discord.Embed(title="Ticket", description=", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed, view=view)

            if select.values[0] == "Utility":
                cog = interaction.client.get_cog("Utility")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            if select.values[0] == "Welcome":
                cog = interaction.client.get_cog("Welcome")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed, view=view)



            if select.values[0] == "Auto Responder":
                cog = interaction.client.get_cog("AutoResponder")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            

            if select.values[0] == "Media":
                cog = interaction.client.get_cog("Media")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            if select.values[0] == "Voice Command":
                cog = interaction.client.get_cog("Voice")
                embed = discord.Embed(title=cog.qualified_name + " Command", description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            

            if select.values[0] == "Bot":
                cog = interaction.client.get_cog("info")
                embed = discord.Embed(title="Bot", description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Developed with ❤️ by Sky..!!", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)


        async def on_timeout(self):
            if len(self.children) == 0: return
            
            for i in self.children:
                i.disabled = True
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    inv = discord.ui.Button(label="Invite Raze", url=config.Invite)
    support = discord.ui.Button(label="Support Server", url=config.Support)
    view = HelpPanel(author=self.context.author, embed=self.embed).add_item(inv).add_item(support).add_item(SearchButton(self.context.author, self.context.bot))

    self.embed.set_author(name=self.context.author, icon_url=self.context.author.display_avatar.url)
    self.embed.set_footer(text=f"Developed with ❤️ by Sky..!!", icon_url=self.context.bot.user.display_avatar.url)

    if self.context.guild.icon:
        self.embed.set_thumbnail(url=self.context.guild.icon.url)
    else:
        self.embed.set_thumbnail(url=self.context.bot.user.display_avatar.url)

    view.message = await self.context.send(embed=self.embed, view=view)







  async def send_command_help(self, command):
    if command.hidden:
        return await self.command_not_found(command.name)

    if len(command.description) == 0:
      command.description = "No description provided."

    embed = discord.Embed(description=f"```diff\n- [] = optional argument\n- <> = required argument\n- Do NOT type these when using commands.```\n>>> {command.description}", color=config.color)
    alias = command.aliases
    if alias:
        embed.add_field(name="Aliases", value=", ".join(f"`{x}`" for x in alias))
    embed.add_field(name="Usage", value=f"`&{(command)}`", inline=False)
    embed.set_author(name=self.context.bot.user.name, icon_url=self.context.bot.user.display_avatar.url)
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text=self.context.bot.user.name, icon_url=self.context.bot.user.display_avatar.url)

    await self.context.send(embed=embed)
    


  async def send_group_help(self, group: commands.Group):

    embeds = []
    str1 = [self.get_command_signature(i) for i in group.commands if not i.hidden]
    str2 = [i.description if len(i.description) != 0 else 'No description provided.' for i in group.commands]


    for chunk in discord.utils.as_chunks(zip(str1, str2), 10):
        embed = discord.Embed(title=f"`&{(group)}`", color=config.color)
        embed.description = ''
        embed.set_author(name=self.context.bot.user.name, icon_url=self.context.bot.user.display_avatar.url)
        embed.set_footer(text=f"{self.context.author}", icon_url=self.context.author.display_avatar.url)
        for i, z in chunk:
            embed.description += f"".join(f"`{i}`\n{z}\n\n");
        embeds.append(embed)
    
    if len(embeds) == 0:
        return await self.command_not_found(group.name)
    
    if len(embeds) > 1:
        view = PaginatorView(embeds, bot=self.context.bot, author=self.context.author)
        view.message = await self.context.send(embed=view.initial, view=view)
    else:
        view2 = PaginatorView(embeds, bot=self.context.bot, author=self.context.author)
        view2.message = await self.context.send(embed=view2.initial)
  


  async def send_cog_help(self, cog):
    embed = discord.Embed(description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)

    embed.set_author(name=self.context.bot.user.name, icon_url=self.context.bot.user.display_avatar.url)
    embed.timestamp = datetime.datetime.now()
    embed.set_footer(text=f"Requested By {self.context.author}", icon_url=self.context.author.display_avatar.url)

    await self.context.send(embed=embed)





  async def command_not_found(self, string):
      cmds_list = [cmd.name for cmd in self.context.bot.commands if not cmd.hidden]
      matches = get_close_matches(string, cmds_list)

      if len(matches) > 0: 
          match_list = enumerate([f"{match}" for match in matches], start=1)

          embed = discord.Embed(description=f"Could not find `{string}` command.\n\nDid you mean:\n"+ "".join(f'`[{i}]` {z}\n' for i, z in match_list), color=config.color)
          embed.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url)
          embed.timestamp = datetime.datetime.utcnow()
          await self.context.send(embed=embed)

      else:
          embed2 = discord.Embed(description=f"Could not find `{string}` command.", color=config.color)
          embed2.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url)
          embed2.timestamp = datetime.datetime.utcnow()
          await self.context.send(embed=embed2)


  async def subcommand_not_found(self, command, string):
      cmds_list = [cmd.name for cmd in self.context.bot.commands if not cmd.hidden]
      matches = get_close_matches(string, cmds_list)

      if len(matches) > 0:
          match_list = enumerate([f"{match}" for match in matches], start=1)
          embed = discord.Embed(description=f"Could not find `{string}` command.\n\nDid you mean:\n"+ "".join(f'`[{i}]` {z}\n' for i, z in match_list), color=config.color)
          embed.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url)
          embed.timestamp = datetime.datetime.utcnow()
          await self.context.send(embed=embed)

      else:
          embed2 = discord.Embed(description=f"Could not find `{string}` subcommand for `{command}` command.", color=config.color)
          embed2.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url)
          embed2.timestamp = datetime.datetime.utcnow()
          await self.context.send(embed=embed2)


  async def send_error_message(self, error):
      if isinstance(error, commands.BadArgument):
        embed = discord.Embed(description=str(error))
        embed.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url, color=config.color)
        embed.timestamp = datetime.datetime.utcnow()
        await self.context.send(embed=embed)

     



        

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        for i in self.bot.commands:
           if len(i.description) == 0:
              i.description = "No description provided."
        attributes = {
        'aliases': ["h"],
        'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.user),
      } 
              
        Help = HelpCommand(command_attrs=attributes)
        bot.help_command = Help
        bot.help_command.cog = self
        "bot._BotBase__cogs = commands.core._CaseInsensitiveDict()"
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command






async def setup(bot):
  await bot.add_cog(Help(bot))