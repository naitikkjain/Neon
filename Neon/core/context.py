from discord.ext import commands, tasks
import discord
from discord.ui import Button, View



import random, sys , typing, asyncio, aiosqlite, jishaku, os

from Extra import config





class Context(commands.Context):
    async def send(self, content: str = None, *args, **kwargs) -> discord.Message:
        premsg = self.bot.invoker.get(self.message.id, None)
        if premsg is not None:
            
            attachments = kwargs.pop("files", [])
            if file := kwargs.get("file"):
                attachments.append(file)

            embeds = kwargs.pop("embeds", [])
            if embed := kwargs.get("embed"):
                embeds.append(embed)

            fields = {
                "content": content,
                "attachments": attachments,
                "view": kwargs.pop("view", None),
                "embeds": embeds,
            }
            try:
                return await premsg.edit(**fields)
            except: pass
    

        if random.randint(0, 8) == 4:

           if content:
                content += ""
           else:
                content = ""
        
        msg = await super().send(content, *args, **kwargs)
        self.bot.invoker[self.message.id] = msg
        return msg
    

    async def confirm(self, message: str, author: discord.Member = None, timeout = 30):
        author = author or self.author
        class ConfirmationView(discord.ui.View):
            def __init__(self):
                self.value: typing.Optional[bool] = None
                super().__init__(timeout=timeout)


            @discord.ui.button(label="Confirm", emoji=config.Tick, style=discord.ButtonStyle.green)
            async def ConfirmCallback(self, interaction: discord.Interaction, btn: discord.ui.Button):
                if interaction.user != author:
                    return await interaction.response.send_message(f"This panel cannot be controlled by you.")
                await interaction.response.defer()
                await interaction.delete_original_response()
                self.value = True
                self.stop()
                

            @discord.ui.button(label="Cancel", emoji=config.Cross, style=discord.ButtonStyle.red)
            async def CancelCallback(self, interaction: discord.Interaction, btn: discord.ui.Button):
                if interaction.user != author:
                    return await interaction.response.send_message(f"This panel cannot be controlled by you.")
                await interaction.response.defer()
                await interaction.delete_original_response()
                self.value = False
                self.stop()
            
            
            async def on_timeout(self):
                if self.message is None and self.message.channel is None: 
                    return self.stop() 
                try:
                   await self.message.delete()
                except:
                    pass
                self.stop()
    
        view = ConfirmationView()
        embed = discord.Embed(
            description=message,
            color=config.color
        )
        view.message = await self.send(embed=embed, view=view)
        await view.wait()
        return view.value

