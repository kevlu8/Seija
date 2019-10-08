import discord
from discord.ext import commands
from modules import db


class Docs(commands.Cog, name="Pretty Bot Documentation"):
    def __init__(self, bot):
        self.bot = bot
        self.help_thumbnail = "https://i.imgur.com/JhL9PV8.png"
        self.author_icon = "https://i.imgur.com/1icHC5a.png"
        self.author_text = "Seija"
        self.footer_icon = 'https://avatars0.githubusercontent.com/u/5400432'
        self.footer_text = "Made by Kyuunex"
        self.veto_channel_id_list = db.query(["SELECT value FROM config WHERE setting = ?", ["guild_veto_channel"]])

    @commands.command(name="docs", brief="Pretty help command", description="", pass_context=True)
    async def docs(self, ctx, sub_help = None):
        if sub_help == "veto":
            if (str(ctx.channel.id),) in self.veto_channel_id_list:
                await ctx.send(embed=await self.veto())
        elif sub_help == "mapchannel":
            await ctx.send(embed=await self.mapset_channel())
        elif sub_help == "queue":
            await ctx.send(embed=await self.queue(ctx.author))
        elif sub_help == "mapchannelmanagement":
            await ctx.send(embed=await self.mapset_channel_management())
        elif sub_help == "queuemanagement":
            await ctx.send(embed=await self.queue_management())
        else:
            await ctx.send(embed=await self.main())

    async def main(self):
        embed = discord.Embed(title="Seija teaches you how to be a bot master.", description="Any abuse will be dealt with punishment.", color=0xbd3661)
        embed.add_field(name="'docs mapchannel", value="To bring up a help menu for requesting a mapset channel.", inline=True)
        embed.add_field(name="'docs queue", value="To bring up a help menu for requesting a queue channel.", inline=True)
        embed.add_field(name="'docs mapchannelmanagement", value="To bring mapset channel management commands.", inline=True)
        embed.add_field(name="'docs queuemanagement", value="To bring up queue channel management commands.", inline=True)
        embed.add_field(name="'from (country_name)", value="Retrive a list of server members that are in the specified country. Takes Alpha-2, Alpha-3 codes and full country names.", inline=True)
        embed.add_field(name="'ts (mod)", value="Send an osu editor clickable timestamp. Must start with a timestamp.", inline=True)
        #embed.add_field(name="'docs veto", value="Commands for tracking in veto mode.", inline=True)
        embed.set_thumbnail(url=self.help_thumbnail)
        embed.set_author(name=self.author_text, icon_url=self.author_icon)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon)
        return embed
        
    async def veto(self):
        embed = discord.Embed(title="~~BNS PLEZ MUTUAL ME~~", description="**Here are veto tracking commands:**", color=0xbd3661)
        embed.add_field(name="'veto <mapset_id>", value="Track a mapset in this channel in veto mode.", inline=True)
        embed.add_field(name="'unveto <mapset_id>", value="Untrack a mapset in this channel in veto mode.", inline=True)
        embed.set_thumbnail(url=self.help_thumbnail)
        embed.set_author(name=self.author_text, icon_url=self.author_icon)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon)
        return embed

    async def queue(self, author):
        qname = author.display_name.replace(" ", "_").lower()
        text = "**__Queue creation command:__**"
        text += "\n`'request_queue (queue type)` - Create a queue. By default, the queue will be closed."
        text += "\n`(queue type)` is an optional argument that specifies what goes between your username and the word `queue` in the title of the channel. If no argument is supplied, `std` will be automatically filled. Please follow our naming standards."
        text += "\n"
        text += "\n**__Examples:__**"
        text += "\n`'request_queue mania` - This example will create `#%s-mania-queue`" % (qname)
        text += "\n`'request_queue taiko-bn` - This example will create `#%s-taiko-bn-queue`" % (qname)
        text += "\n"
        text += "\nFor queue management commands, type `'docs queuemanagement`"
        text += "\n"
        text += "\n**Remember:**"
        text += "\n**__DO NOT__ create a queue __only__ for GD requests.**"
        text += "\n**__IT SHOULD__ be a queue, not diary, not image dump. You can be creative and do other things but it's primary purpose must be a queue.**"
        embed = discord.Embed(title="With this command, you can create a queue channel.", description=text, color=0xbd3661)
        embed.set_author(name=self.author_text, icon_url=self.author_icon)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon)
        return embed

    async def mapset_channel(self):
        text = "**__Mapset channel creation command:__**: "
        text += "\n`'request_mapset_channel (mapset id) (song name)` - This is the general command to create a channel."
        text += "\n`(song name)` is an optional argument that is not required. But it must be written in quotes if supplied."
        text += "\nIf the mapset is not yet uploaded, `(mapset id)` can be set to `0` but in that case, `(song name)` argument is required."
        text += "\n"
        text += "\n**__Examples:__**"
        text += "\n`'request_mapset_channel 817793` - Example usage with mapset id."
        text += "\n`'request_mapset_channel 0 \"Futanari Nari ni\"` - Example usage with just song name."
        text += "\n"
        text += "\nFor mapset channel management commands, type `'docs mapchannelmanagement`"
        text += "\n"
        text += "\n**Remember:**"
        text += "\n**__DO NOT__ create a mapset channel for single person sets. Only do it if you have guest difficulties or if this is a collab.**"
        text += "\n**__DO NOT__ create a channel if you __already__ don't have a collaborator.**"
        embed = discord.Embed(title="With this command, you can create a mapset channel for collaborators.", description=text, color=0xbd3661)
        embed.set_author(name=self.author_text, icon_url=self.author_icon)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon)
        return embed

    async def queue_management(self):
        embed = discord.Embed(title="Queue management commands", description="""**Please avoid manually editing channel permissions unless you wanna ban a specific person or a role from your queue or unless the bot is down.**""", color=0xbd3661)
        embed.add_field(name="'open", value="Open the queue, everyone can see and post in it.", inline=False)
        embed.add_field(name="'close", value="Close the queue, everyone can see but can't post in it. You can also use this command to unhide the queue, but again, nobody will be able to post in it.", inline=False)
        embed.add_field(name="'hide", value="Hide the queue, only admins can see the queue. Nobody else can see and post in it.", inline=False)
        embed.set_author(name=self.author_text, icon_url=self.author_icon)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon)
        return embed

    async def mapset_channel_management(self):
        embed = discord.Embed(title="Mapset channel management commands", description="""`(user)` can be ether a name of the user or a discord account user id. To get user id, you need developer mode enabled in your discord client settings, right click on the user and click \"Copy ID\". Using IDs are recommended rather than names.""", color=0xbd3661)
        embed.add_field(name="'add (user)", value="Add a user in the mapset channel.", inline=False)
        embed.add_field(name="'remove (user)", value="Remove a user from the mapset channel.", inline=False)
        embed.add_field(name="'abandon", value="If you abandoning the set, whether temporarily or permanently, this will stop all tracking and move the channel to archive category.", inline=False)
        embed.add_field(name="'setid (mapset_id)", value="Set a mapset id for this channel. Useful if you created this channel without setting an id.", inline=False)
        embed.add_field(name="'setowner (user_id)", value="Transfer set ownership to another discord account. user_id can only be that discord account's id.", inline=False)
        #embed.add_field(name="'track (tracking_mode)", value="Track the mapset in this channel. For tracking_mode, specify 'classic' for discussion/timeline type, specify 'notification' for notification type.", inline=False)
        embed.add_field(name="'track", value="Track the mapset in this channel", inline=False)
        embed.add_field(name="'untrack", value="Untrack everything in this channel.", inline=False)
        embed.set_author(name=self.author_text, icon_url=self.author_icon)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon)
        return embed

def setup(bot):
    bot.add_cog(Docs(bot))