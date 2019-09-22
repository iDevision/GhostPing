import traceback
import typing

import discord
from discord.ext import commands

class Customiser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.identifiers = ["message.author", "message.content", "message.guild", "me"]
        self.customisers = ["dm_message", "guild_message"]
    
    async def get_customiser(self, member: typing.Union[discord.Member, discord.User]):
        """Get a customiser"""
        query = "SELECT * FROM storage WHERE id = $1;"

        return await self.bot.db.fetch(query, member.id)

    async def make_customiser(self, member: typing.Union[discord.Member, discord.User]):
        """Make a customiser"""
        query = "INSERT INTO storage (id, guild_message, dm_message) VALUES ($1,$2,$3);"

        return await self.bot.db.execute(query, member.id, "{{me}}, you were ghost pinged in {{message.guild}} inside a message from {{message.author}}.", "You were ghost pinged in a message from {{message.author}}.")

    async def update_customiser(self, member: typing.Union[discord.Member, discord.User], setting, content):
        """Update a customiser"""
        query = f"UPDATE storage SET {setting.lower()} = $1 WHERE id = $2;"

        return await self.bot.db.execute(query, content, member.id)

    @commands.group(name="customiser", invoke_without_command=True)
    async def customiser_(self, ctx):
        """Group parent, show your current settings."""
        storage = await self.get_customiser(ctx.author)

        if not storage:
            await self.make_customiser(ctx.author)

            storage = await self.get_customiser(ctx.author)

        embed = discord.Embed(title="Your customiser", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)
        embed.add_field(name="DM Message", value=storage[0]["dm_message"], inline=False)
        embed.add_field(name="Guild Message", value=storage[0]["guild_message"], inline=False)

        embed.set_footer(text="Note these are global.")

        return await ctx.send(embed=embed)
    
    @customiser_.command(name="set")
    async def set_(self, ctx, setting, *, content):
        """Set a customiser value. You can set dm_message and guild_message. Please note that when using markdown, add a space. i.e: `** {{message.content}} **`"""
        if setting.lower() not in self.customisers:
            raise commands.BadArgument("Identifier %s not valid. Choose from `dm_message` or `guild_message`" % setting.lower())
        
        customiser = await self.get_customiser(ctx.author)

        if not customiser:
            await self.make_customiser(ctx.author)

        await self.update_customiser(ctx.author, setting, content)

        return await ctx.send(f"Your customiser for {setting.lower()} has been updated to {content}.")
    
    @customiser_.command(name="reset")
    async def reset_(self, ctx, setting):
        """Reset a setting to default"""
        if setting.lower() not in self.customisers:
            raise commands.BadArgument("Identifier %s not valid. Choose from `dm_message` or `guild_message`" % setting.lower())
        
        customiser = await self.get_customiser(ctx.author)
        
        if not customiser:
            await self.make_customiser(ctx.author)

        if setting.lower() == "dm_message":
            content = "You were ghost pinged in {{message.guild}} inside a message from {{message.author}}."
        else:
            content = "{{me}}, you were ghost pinged in a message from {{message.author}}."

        await self.update_customiser(ctx.author, setting, content)

        return await ctx.send(f"Your customiser for {setting.lower()} has been updated to {content}.")

def setup(bot):
    bot.add_cog(Customiser(bot))