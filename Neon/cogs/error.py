from typing import Optional
from discord.ext import commands
import discord
import datetime


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        if isinstance(error, commands.MissingRequiredArgument):
            help_embed = discord.Embed(description=f"You are missing a required argument for the command `{ctx.command}`.", color=0x2b2d31)
            help_embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
          
            help_embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=help_embed)

        if isinstance(error, commands.BotMissingPermissions):
            permissions = ', '.join(perm for perm in error.missing_permissions)
            error_embed = discord.Embed(description=f"The bot needs {permissions} to execute this command.", color=0x2b2d31)
            error_embed.timestamp = datetime.datetime.utcnow()
            error_embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            return await ctx.send(embed=error_embed)

        if isinstance(error, commands.CommandOnCooldown):
            bucket = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)
            retry_after = bucket.get_bucket(ctx.message).update_rate_limit()

            if retry_after:
                return

            cooldown_embed = discord.Embed(description=f"You're on cooldown. Try again in {round(error.retry_after, 2)} seconds.", color=0x2b2d31)
            cooldown_embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            cooldown_embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=cooldown_embed)

        if isinstance(error, commands.UserNotFound):
            user_not_found_embed = discord.Embed(description="The specified user was not found.", color=0x2b2d31)
            user_not_found_embed.timestamp = datetime.datetime.utcnow()
            user_not_found_embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            return await ctx.send(embed=user_not_found_embed)

        if isinstance(error, commands.MemberNotFound):
            member_not_found_embed = discord.Embed(description="The specified member was not found.", color=0x2b2d31)
            member_not_found_embed.timestamp = datetime.datetime.utcnow()
            member_not_found_embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            return await ctx.send(embed=member_not_found_embed)

        if isinstance(error, commands.RoleNotFound):
            role = error.argument
            role_not_found_embed = discord.Embed(description=f"The role `{role}` was not found.", color=0x2b2d31)
            role_not_found_embed.timestamp = datetime.datetime.utcnow()
            role_not_found_embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            return await ctx.send(embed=role_not_found_embed)

        if isinstance(error, commands.ChannelNotFound):
            channel = error.argument
            channel_not_found_embed = discord.Embed(description=f"The channel '{channel}' was not found.", color=0x2b2d31)
            channel_not_found_embed.timestamp = datetime.datetime.utcnow()
            channel_not_found_embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            return await ctx.send(embed=channel_not_found_embed)

        if isinstance(error, commands.MaxConcurrencyReached):
            max_concurrency_embed = discord.Embed(description=f"{ctx.author} {error}", color=0x2b2d31)
            max_concurrency_embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=max_concurrency_embed)

        if isinstance(error, commands.CheckAnyFailure):
            for err in error.errors:
                if isinstance(err, commands.MissingPermissions):
                    permissions_embed = discord.Embed(description=f"You don't have enough permissions to run the command `{ctx.command.qualified_name}`", color=0x2b2d31)
                    permissions_embed.timestamp = datetime.datetime.utcnow()
                    permissions_embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
                    return await ctx.send(embed=permissions_embed, delete_after=5)

        if isinstance(error, commands.CheckFailure):
            return


async def setup(bot):
    await bot.add_cog(Errors(bot))
