import typing

from datetime import datetime

import discord
from discord.ext import commands

class Pings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def make_toggle(self, member: typing.Union[discord.Member, discord.User], toggle: bool):
        """Creates a toggle in the db"""
        query = "INSERT INTO toggles (id, toggle) VALUES ($1,$2);"

        return await self.bot.db.execute(query, member.id, toggle)

    async def get_toggle(self, member: typing.Union[discord.Member, discord.User]):
        """Get a toggle"""
        query = "SELECT * FROM toggles WHERE id = $1;"

        return await self.bot.db.fetch(query, member.id)
    
    async def update_toggle(self, member: typing.Union[discord.Member, discord.User], toggle: bool):
        """Update a toggle"""
        query = "UPDATE toggles SET toggle = $1 WHERE id = $2;"

        return await self.bot.db.execute(query, toggle, member.id)

    async def check_block(self, object):
        """Check a block"""
        fetch = await self.bot.cogs["Blocks"].get_block(object)

        return False if not fetch else fetch["id"]

    @commands.command(name="toggle")
    async def toggle_(self, ctx):
        """Toggle ping detection off/on"""
        fetch = await self.get_toggle(ctx.author)

        if not fetch:
            toggle = True
            await self.make_toggle(ctx.author, toggle)
        else:
            toggle = not fetch[0]["toggle"]

        await self.update_toggle(ctx.author, toggle)

        return await ctx.send("Opted in to ghost ping detector." if toggle else "Opted out to ghost ping detector.")

    @commands.command(name="tracking")
    async def tracking_(self, ctx):
        """See what messages with your mention i am tracking"""
        tracking = [m[0] for m in self.bot._ping_cache.values() if ctx.author.id in [u.id for u in m[1]]]
        toggle = await self.get_toggle(ctx.author)

        if not toggle or toggle[0]["toggle"] is False:
            return await ctx.send("You are not opted in. To begin tracking use `ghost toggle`.")

        embed = discord.Embed(title="Currently Tracking", colour=discord.Colour.blue(), timestamp=ctx.message.created_at)

        if tracking:
            for message in tracking:
                embed.add_field(name=f"From {message.author}", value=message.content, inline=False)
        else:
            embed.description = "Not tracking anything with your mention."
        
        return await ctx.send(embed=embed)

    async def clean_mentions(self, author: typing.Union[discord.Member, discord.User], mentions: list, edit: bool, new=None):
        """Clean up the message mention list"""
        cleaned = []

        if not edit:
            for mention in mentions:
                if mention.id == author.id:
                    continue
                
                toggle = await self.get_toggle(mention)

                if not toggle or toggle[0]["toggle"] is False:
                    continue

                cleaned.append(mention)
        else:
            for mention in mentions:
                if mention.id in [m["id"] for m in new] or mention.id == author.id:
                    continue

                else:
                    toggle = await self.get_toggle(mention)
                    
                    if not toggle or toggle[0]["toggle"] is False:
                        continue
                    
                    cleaned.append(mention)
        
        return cleaned

    async def format_msg(self, ctx, user, message, actual: discord.Message):
        """Format a custom message"""
        valid_options = ["message.author", "message.content", "message.guild", "message.timestamp", "me"]
        
        formatted = []

        for word in message.split(" "):
            if word.strip().startswith("{{") and word.strip().endswith("}}") or word[:-1].endswith("}}"):
                if word[:-1].endswith("}}"):
                    word = word[2:-3]
                else:
                    word = word[2:-2]

                if word not in valid_options:
                    word = word
                else:
                    if word == "message.content":
                        word = await commands.clean_content().convert(ctx, str(getattr(actual, word.split(".")[1])))
                    elif word == "me":
                        word = user.mention
                    elif word == "message.timestamp":
                        word = actual.created_at.ctime()
                    else:
                        word = str(getattr(actual, word.split(".")[1]))
            
            formatted.append(word)
        
        return ' '.join(formatted)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Ping detector"""
        if not message.mentions or message.author == self.bot.user:
            return
        
        self.bot._ping_cache[message.id] = (message, message.mentions)
    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """Detect if a message with pings was deleted"""
        if payload.message_id not in self.bot._ping_cache.keys():
            return
        
        message = self.bot._ping_cache[payload.message_id]
        ctx = await self.bot.get_context(message[0])

        clean_mentions = await self.clean_mentions(message[0].author, message[1], False)

        for user in clean_mentions:
            user_blocks = await self.bot.cogs["Blocks"].get_blocks(user)
            user_blocks = [item["id"] for item in user_blocks]

            if payload.channel_id in user_blocks:
                return
            
            if message[0].author.id in user_blocks:
                return
            
            print(f"Messaging {user}")

            storage = await self.bot.db.fetch("SELECT * FROM storage WHERE id = $1;", user.id)
            guild = self.bot.get_guild(payload.guild_id)

            try:
                if not storage:
                    await user.send(f"You were ghost pinged in {guild} inside a message from {message[0].author}")
                else:
                    formatted = await self.format_msg(ctx, user, storage[0]["dm_message"], message[0])
                    await user.send(formatted)
                
                del self.bot._ping_cache[message[0].id]

                return

            except discord.Forbidden:
                if not storage:
                    await message[0].channel.send(f"{user.mention}, you were ghost pinged by {message[0].author}")
                else:
                    formatted = await self.format_msg(ctx, user, storage[0]["guild_message"], message[0])
                    await message[0].channel.send(formatted)
        
        del self.bot._ping_cache[message[0].id]
        
    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        """Detect if a message with pings was deleted"""
        if not payload.message_id in self.bot._ping_cache.keys():
            return
        
        message = self.bot._ping_cache[payload.message_id]
        ctx = await self.bot.get_context(message[0])

        clean_mentions = await self.clean_mentions(message[0].author, message[1], True, payload.data["mentions"])

        for user in clean_mentions:
            print(f"Messaging {user}")

            storage = await self.bot.db.fetch("SELECT * FROM storage WHERE id = $1;", user.id)
            channel = self.bot.get_channel(payload.channel_id)

            try:
                if not storage:
                    await user.send(f"You were ghost pinged in {channel.guild} inside a message from {message[0].author}")
                else:
                    formatted = await self.format_msg(ctx, user, storage[0]["dm_message"], message[0])
                    await user.send(formatted)
                
                del self.bot._ping_cache[message[0].id]

                return
            except discord.Forbidden:
                if not storage:
                    await message[0].channel.send(f"{user.mention}, you were ghost pinged by {message[0].author}")
                else:
                    formatted = await self.format_msg(ctx, user, storage[0]["guild_message"], message[0])
                    await message[0].channel.send(formatted)
        
        del self.bot._ping_cache[message[0].id]

def setup(bot):
    bot.add_cog(Pings(bot))