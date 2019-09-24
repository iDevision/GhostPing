import discord
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_toggles(self):
        """Get the amount of toggles"""
        query = "SELECT COUNT(*) FROM toggles;"
        fetch = await self.bot.db.fetch(query)

        return fetch[0]["count"]

    async def get_paramaters(self, paramaters):
        """Returns a commands peramaters in the format of <> or []"""
        final_string = []

        for paramater in paramaters:
            if "=" in str(paramaters[paramater]):
                final_string.append(f"[{paramater}]")
            else:
                final_string.append(f"<{paramater}>")
        
        return " ".join(final_string)

    @commands.command(name="info", aliases=["about"])
    async def info_(self, ctx):
        """Info on the bot"""
        toggles = await self.get_toggles()

        fields = [f"Looking at {len(self.bot.guilds)} guilds, with {len(self.bot.users)} users in total.\n\n" \
                  f"{toggles} opted-in users.\n" \
                  f"Currently Tracking {len(self.bot._ping_cache.keys())} ping(s)\n\n" \
                  f"Made by Lgan#4676\n\n",
                  "[Invite](https://discordapp.com/api/oauth2/authorize?client_id=606167630214201344&permissions=66560&scope=bot) | [Support](https://discord.gg/kayUTZm)"]
        desc = ""

        for field in fields:
            desc += field

        embed = discord.Embed(title="Info", description=desc, timestamp=ctx.message.created_at, colour=discord.Colour.blue())

        return await ctx.send(embed=embed)
    
    @commands.command(name="invite", aliases=["inv", "invites"])
    async def invite_(self, ctx):
        """Get bot invites"""
        return await ctx.send(embed=discord.Embed(description="[Invite](https://discordapp.com/api/oauth2/authorize?client_id=606167630214201344&permissions=66560&scope=bot) | [Support](https://discord.gg/kayUTZm)", colour=discord.Colour.blue(), timestamp=ctx.message.created_at))

    @commands.command(name="help")
    async def help_(self, ctx, *, category=None):
        """Get help on a command"""
        embed = discord.Embed(title="Help", colour=discord.Colour.blue())

        if not category:
            # Overview
            fields = {
                "Pings": "GhostPing's main commands.",
                "Customiser": "Customiser commands, set custom messages.",
                "Misc": "Miscellaneous commands."
            }

            for cat, desc in fields.items():
                embed.add_field(name=cat, value=desc, inline=False)
        else:
            categories = {**dict.fromkeys(["customiser","customizer"], self.bot.get_cog("Customiser")), "misc": self.bot.get_cog("Misc"), "pings": self.bot.get_cog("Pings"), "blocks": self.bot.get_cog("Blocks")}

            if category.lower() not in categories.keys():
                return await ctx.send("That category does not exist.")
            
            for command in categories[category.lower()].walk_commands():
                if len(command.aliases) > 0:
                    fmt = f"{command.name} | {' | '.join(command.aliases)}"
                else:
                    fmt = command.name
                
                params = await self.get_paramaters(command.clean_params)

                fmt += f" {params}"

                if command.parent:
                    fmt = f"{command.parent} {fmt}"
                    
                embed.add_field(name=fmt, value=command.help, inline=False)

            return await ctx.send(embed=embed)

        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Misc(bot))