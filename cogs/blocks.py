import typing

import discord
from discord.ext import commands

class Blocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def make_block(self, type, object, user):
        """Make a block"""
        query = "INSERT INTO blocks (owner_id, id, type) VALUES ($1,$2,$3);"

        return await self.bot.db.execute(query, user.id, object.id, type)

    async def get_block(self, object):
        """Get a block"""
        query = "SELECT * FROM blocks WHERE id = $1;"

        return await self.bot.db.fetch(query, object.id)

    async def get_blocks(self, user):
        """Get a user's blocks"""
        query = "SELECT * FROM blocks WHERE owner_id = $1;"

        return await self.bot.db.fetch(query, user.id)

    async def remove_block(self, object, user):
        """Remove a block"""
        query = "DELETE FROM blocks WHERE owner_id = $1 AND id = $2;"

        return await self.bot.db.execute(query, user.id, object.id)

    @commands.command(name="block")
    async def block_(self, ctx, content: commands.Greedy[typing.Union[discord.Member, discord.TextChannel]]):
        """Block as many channels or users as you wish"""
        for object in content:
            if object == ctx.author:
                return await ctx.send("You can't block yourself.")

            block = await self.get_block(object)

            if block:
                return await ctx.send("You already have this user / channel blocked.")

            if isinstance(object, discord.Member):
                # The block is a user
                await self.make_block("user", object, ctx.author)

            elif isinstance(object, discord.TextChannel):
                # The block is a channel
                await self.make_block("channel", object, ctx.author)

            await ctx.send(await commands.clean_content().convert(ctx, f"Successfully blocked {object.mention}"))
        
        return
    
    @commands.command(name="unblock")
    async def unblock_(self, ctx, content: commands.Greedy[typing.Union[discord.Member, discord.TextChannel]]):
        """Unblock as many channels or users as you wish"""
        for object in content:
            block = await self.get_block(object)

            if not block:
                return await ctx.send("You already have this user / channel blocked.")

            if isinstance(object, discord.Member):
                # The block is a user
                await self.remove_block(object, ctx.author)

            elif isinstance(object, discord.TextChannel):
                # The block is a channel
                await self.remove_block(object, ctx.author)

            await ctx.send(await commands.clean_content().convert(ctx, f"Successfully unblocked {object.mention}"))
        
        return
    
    @commands.command(name="blocks")
    async def blocks_(self, ctx):
        """Get a list of blocks"""
        blocks = await self.get_blocks(ctx.author)
        desc = ""

        for block in blocks:
            if block["type"] == "channel":
                obj = self.bot.get_channel(block["id"])
                desc += f"Channel, {obj.mention}\n"
            else:
                obj = self.bot.get_user(block["id"])
                desc += f"User, {obj.mention}\n"

        return await ctx.send(embed=discord.Embed(title="Your blocks", description=desc, colour=discord.Colour.blue(), timestamp=ctx.message.created_at))

def setup(bot):
    bot.add_cog(Blocks(bot))