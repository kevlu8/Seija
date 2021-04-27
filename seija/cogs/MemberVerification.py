import random

import sqlite3
from discord.ext import commands
from discord.utils import escape_markdown
from seija.modules import permissions
from seija.reusables import exceptions
from seija.reusables import verification as verification_reusables
from seija.embeds import newembeds as osuwebembed
import datetime
import dateutil


class MemberVerification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect(self.bot.database_file)
        c = conn.cursor()
        self.verify_channel_list = tuple(c.execute("SELECT channel_id, guild_id FROM channels WHERE setting = ?",
                                                   ["verify"]))
        conn.close()
        self.post_verification_emotes = [
            ["FR", "🥖"],
        ]

    @commands.command(name="verify", brief="Manually verify a member")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def verify(self, ctx, user_id, osu_id):
        """
        Manually verify a member

        user_id: Discord account ID
        osu_id: osu! account ID
        """

        if not user_id.isdigit():
            await ctx.send("discord account user_id must be all digits")
            return

        member = ctx.guild.get_member(int(user_id))
        if not member:
            await ctx.send("no member found with that user_id")
            return

        try:
            fresh_osu_data = await self.bot.osuweb.get_user_array(osu_id)
        except Exception as e:
            await ctx.send("i have connection issues with osu servers. so i can't do that right now",
                           embed=await exceptions.embed_exception(e))
            return

        if not fresh_osu_data:
            await ctx.send("no osu account found with that osu_id or username")
            return

        ranked_amount = fresh_osu_data["ranked_and_approved_beatmapset_count"]

        try:
            role = await verification_reusables.get_role_based_on_reputation(self, member.guild, ranked_amount)
        except:
            role = None

        if not role:
            await ctx.send("i can't find a role to give. something is misconfigured")
            return

        try:
            await member.add_roles(role)
        except Exception as e:
            await ctx.send("i can't give the role", embed=await exceptions.embed_exception(e))

        try:
            await member.edit(nick=fresh_osu_data["username"])
        except Exception as e:
            await ctx.send("i can't update the nickname of this user", embed=await exceptions.embed_exception(e))

        embed = await osuwebembed.user_array(fresh_osu_data)

        join_date = dateutil.parser.parse(fresh_osu_data['join_date'])
        join_date_int = int(join_date.timestamp())

        await self.bot.db.execute("DELETE FROM users WHERE user_id = ?", [int(member.id)])
        await self.bot.db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)",
                                  [int(member.id), int(fresh_osu_data["id"]), str(fresh_osu_data["username"]),
                                   int(join_date_int), int(fresh_osu_data["statistics"]["pp"]),
                                   str(fresh_osu_data["country_code"]), int(ranked_amount),
                                   int(fresh_osu_data["kudosu"]["total"]), 0])
        await self.bot.db.commit()

        await self.check_group_roles(ctx.channel, member, ctx.guild, fresh_osu_data)
        await ctx.send(content=f"Manually Verified: {member.name}", embed=embed)

    @commands.command(name="verify_restricted", brief="Manually verify a restricted member")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def verify_restricted(self, ctx, user_id, osu_id, username=""):
        """
        Insert a restricted user info into the database. This command does not give any roles.

        user_id: Discord account ID
        osu_id: osu! account ID
        username: osu! account username
        """

        if not user_id.isdigit():
            await ctx.send("discord account user_id must be all digits")
            return

        if not osu_id.isdigit():
            await ctx.send("osu account id must be all digits")
            return

        await self.bot.db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)",
                                  [int(user_id), int(osu_id), str(username), 0, 0, None, 0, 0, 0])
        await self.bot.db.commit()

        await ctx.send("lol ok")

    @commands.command(name="update_user_discord_account", brief="When user switched accounts, apply this")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def update_user_discord_account(self, ctx, old_id, new_id, osu_id=""):
        """
        A command to migrate stuff from old discord account to a new one.

        old_id: an ID of the old Discord account
        new_id: an ID of the new Discord account
        osu_id: an ID of the osu account
        """

        if not old_id.isdigit():
            await ctx.send("old_id must be all digits")
            return

        if not new_id.isdigit():
            await ctx.send("new_id must be all digits")
            return

        try:
            old_account = ctx.guild.get_member(int(old_id))
            if old_account:
                await ctx.send("kicking old account")
                await old_account.kick()
        except Exception as e:
            await ctx.send(embed=await exceptions.embed_exception(e))

        await self.bot.db.execute("UPDATE users SET user_id = ? WHERE user_id = ?", [int(new_id), int(old_id)])
        await self.bot.db.execute("UPDATE difficulty_claims SET user_id = ? WHERE user_id = ?",
                                  [int(new_id), int(old_id)])
        await self.bot.db.execute("UPDATE queues SET user_id = ? WHERE user_id = ?", [int(new_id), int(old_id)])
        await self.bot.db.execute("UPDATE mapset_channels SET user_id = ? WHERE user_id = ?",
                                  [int(new_id), int(old_id)])
        await self.bot.db.commit()

        if osu_id:
            await ctx.send("verifying the new account now")
            await self.verify(ctx, new_id, osu_id)

        await ctx.send("okay, done")

    @commands.command(name="unverify", brief="Unverify a member and delete it from db")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def unverify(self, ctx, user_id):
        """
        Unverify a member and delete it from the database
        
        user_id: Discord account ID
        """

        await self.bot.db.execute("DELETE FROM users WHERE user_id = ?", [int(user_id)])
        await self.bot.db.commit()
        await ctx.send("deleted from database")

        member = ctx.guild.get_member(int(user_id))
        if not member:
            return

        try:
            await member.edit(roles=[])
            await member.edit(nick=None)
            await ctx.send("removed nickname and roles")
        except Exception as e:
            await ctx.send("no perms to change nickname and/or remove roles", embed=await exceptions.embed_exception(e))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for verify_channel_id in self.verify_channel_list:
            if member.guild.id != int(verify_channel_id[1]):
                continue

            channel = self.bot.get_channel(int(verify_channel_id[0]))
            if not channel:
                # something is misconfigured
                continue

            if member.guild.member_count == 1000:
                await channel.send(f"owo, our 1000-th member is here!")

            if member.bot:
                await channel.send(f"beep boop boop beep, {member.mention} has joined our army of bots")
                return

            await self.ask_just_joined_member_to_verify(channel, member)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        for verify_channel_id in self.verify_channel_list:
            if message.channel.id != int(verify_channel_id[0]):
                continue

            if "https://osu.ppy.sh/u" in message.content:
                profile_id = self.grab_osu_profile_id_from_text(message.content)
                await self.profile_id_verification(message.channel, message.author, profile_id)
                return

            if message.content.lower() == "yes" and self.is_new_user(message.author) is False:
                profile_id = message.author.name
                await self.profile_id_verification(message.channel, message.author, profile_id)
                return

            return

    def grab_osu_profile_id_from_text(self, text):
        split_message = text.split("/")
        return split_message[4].split("#")[0].split(" ")[0]

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        for verify_channel_id in self.verify_channel_list:
            if member.guild.id != int(verify_channel_id[1]):
                continue

            channel = self.bot.get_channel(int(verify_channel_id[0]))
            if not channel:
                # something is misconfigured
                continue

            if member.bot:
                await channel.send(f"beep boop boop beep, {member.mention} has left our army of bots")
                return

            async with self.bot.db.execute("SELECT osu_id, osu_username FROM users WHERE user_id = ?",
                                           [int(member.id)]) as cursor:
                osu_id = await cursor.fetchone()

            if osu_id:
                try:
                    fresh_osu_data = await self.bot.osuweb.get_user_array(osu_id[0])
                    embed = await osuwebembed.small_user_array(fresh_osu_data, 0xffffff, "User left")
                    member_name = fresh_osu_data["username"]
                except:
                    print("Connection issues?")
                    embed = None
                    member_name = member.name
            else:
                embed = None
                member_name = member.name

            escaped_member_name = escape_markdown(member_name)

            async with self.bot.db.execute("SELECT message FROM member_goodbye_messages") as cursor:
                member_goodbye_messages = await cursor.fetchall()

            goodbye_message = random.choice(member_goodbye_messages)

            await channel.send(goodbye_message[0] % f"**{escaped_member_name}**", embed=embed)

    async def profile_id_verification(self, channel, member, osu_id, confirmed=False):

        try:
            fresh_osu_data = await self.bot.osuweb.get_user_array(osu_id)
        except Exception as e:
            await channel.send("i am having issues connecting to osu servers to verify you. "
                               "try again later or wait for a manager to help",
                               embed=await exceptions.embed_exception(e))
            return

        if not fresh_osu_data:
            if osu_id.isdigit():
                await channel.send("verification failure, "
                                   "i can't find any profile from that link or you are restricted. "
                                   "if you are restricted, link any of your recently uploaded maps (new site only)")
            else:
                await channel.send("verification failure, "
                                   "either your discord username does not match a username of any osu account "
                                   "at the time you typed 'yes', "
                                   "or you linked an incorrect profile. "
                                   "this error also pops up if you are restricted, in that case, "
                                   "link any of your recently uploaded maps (ranked with the latest name preferred)")
            return

        ranked_amount = fresh_osu_data["ranked_and_approved_beatmapset_count"]
        role = await verification_reusables.get_role_based_on_reputation(self, member.guild, ranked_amount)

        try:
            if fresh_osu_data['discord']:
                if str(member) == str(fresh_osu_data['discord']):
                    confirmed = True
        except KeyError:
            pass

        async with self.bot.db.execute("SELECT osu_id FROM users WHERE user_id = ?", [int(member.id)]) as cursor:
            already_linked_to = await cursor.fetchone()
        if already_linked_to:
            if int(fresh_osu_data["id"]) != int(already_linked_to[0]):
                await channel.send(f"{member.mention} it seems like your discord account is already in my database and "
                                   f"is linked to <https://osu.ppy.sh/users/{already_linked_to[0]}>."
                                   f"this check exists to prevent impersonation to an extent. "
                                   f"ping kyuunex if there is a problem, "
                                   f"for example if you multiaccounted on osu in past or something.")
                return
            else:
                try:
                    await member.add_roles(role)
                    await member.edit(nick=fresh_osu_data["username"])
                except:
                    pass
                await channel.send(content=f"{member.mention} i already know lol. here, have some roles")
                return

        if not confirmed:
            async with self.bot.db.execute("SELECT user_id FROM users WHERE osu_id = ?",
                                           [int(fresh_osu_data["id"])]) as cursor:
                check_if_new_discord_account = await cursor.fetchone()
            if check_if_new_discord_account:
                if int(check_if_new_discord_account[0]) != int(member.id):
                    old_user_id = check_if_new_discord_account[0]
                    await channel.send(f"this osu account is already linked to <@{old_user_id}> in my database. "
                                       f"this check exists to prevent impersonation to an extent. "
                                       "if there's a problem, for example, you got a new discord account, "
                                       "or somebody impersonated you, ping kyuunex.")
                    return

        if self.last_visit_check(fresh_osu_data, day_amount=60):
            await channel.send(f"i can't verify you right now. circumstances are too suspicious")
            return

        try:
            await member.add_roles(role)
            await member.edit(nick=fresh_osu_data["username"])
        except:
            pass

        embed_color = self.get_correct_embed_trust_color(member, fresh_osu_data)
        embed = await osuwebembed.user_array(fresh_osu_data, color=embed_color)

        join_date = dateutil.parser.parse(fresh_osu_data['join_date'])
        join_date_int = int(join_date.timestamp())

        await self.bot.db.execute("DELETE FROM users WHERE user_id = ?", [int(member.id)])
        await self.bot.db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)",
                                  [int(member.id), int(fresh_osu_data["id"]), str(fresh_osu_data["username"]),
                                   int(join_date_int), int(fresh_osu_data["statistics"]["pp"]),
                                   str(fresh_osu_data["country_code"]), int(ranked_amount),
                                   int(fresh_osu_data["kudosu"]["total"]), 0])
        await self.bot.db.commit()
        verified_message = await channel.send(content="Verified!", embed=embed)

        await self.add_obligatory_reaction(verified_message, fresh_osu_data["country_code"])
        await self.check_group_roles(channel, member, member.guild, fresh_osu_data)

        await self.send_post_verification_message(channel, member, member.guild)

    async def send_post_verification_message(self, channel, member, guild):
        async with self.bot.db.execute("SELECT message FROM post_verification_messages WHERE guild_id = ?",
                                       [int(guild.id)]) as cursor:
            post_verification_message = await cursor.fetchone()
        if post_verification_message:
            await channel.send((post_verification_message[0]).replace("(mention)", member.mention))

    async def member_is_already_verified_and_just_needs_roles(self, channel, member, user_db_lookup):
        try:
            fresh_osu_data = await self.bot.osuweb.get_user_array(user_db_lookup[0])
        except Exception as e:
            await channel.send("okay, i also can't check your osu profile. "
                               "although i do have your osu profile info in my database. "
                               "I'll just use the cached info then",
                               embed=await exceptions.embed_exception(e))
            fresh_osu_data = None

        if fresh_osu_data:
            name = fresh_osu_data["username"]
            ranked_amount = fresh_osu_data["ranked_and_approved_beatmapset_count"]
            embed = await osuwebembed.user_array(fresh_osu_data)
        else:
            name = user_db_lookup[1]
            ranked_amount = user_db_lookup[2]
            embed = None

        role = await verification_reusables.get_role_based_on_reputation(self, member.guild, ranked_amount)
        await member.add_roles(role)

        await member.edit(nick=name)
        verified_message = await channel.send(f"Welcome aboard {member.mention}! Since we know who you are, "
                                              "I have automatically given you appropriate roles. "
                                              "Enjoy your stay!",
                                              embed=embed)

        await self.add_obligatory_reaction(verified_message, fresh_osu_data["country_code"])
        await self.check_group_roles(channel, member, member.guild, fresh_osu_data)

    async def ask_just_joined_member_to_verify(self, channel, member):
        async with self.bot.db.execute("SELECT osu_id, osu_username, ranked_maps_amount FROM users WHERE user_id = ?",
                                       [int(member.id)]) as cursor:
            user_db_lookup = await cursor.fetchone()
        if user_db_lookup:
            await self.member_is_already_verified_and_just_needs_roles(channel, member, user_db_lookup)
            return

        try:
            fresh_osu_data = await self.bot.osuweb.get_user_array(member.name)
        except Exception as e:
            # connection issues
            await channel.send(f"Welcome {member.mention}! in this server, we have a verification system "
                               "for purposes of giving correct roles and dealing with raids. "
                               "Usually I would ask you to link your osu profile, "
                               "but i seem to be having trouble connecting to osu servers. "
                               "so, now I ask you link your profile and if it does not work, "
                               "wait patiently a little bit and then link your profile again. "
                               "worse case, managers will have to manually let you in. "
                               "it will just take time. ignore the error bellow, this is for the managers. ",
                               embed=await exceptions.embed_exception(e))
            return

        if self.autodetect_profile_proven(member, fresh_osu_data):
            profile_id = member.name
            await channel.send(f"Welcome {member.mention}! We have a verification system in this server "
                               "so we can give you appropriate roles and keep raids/spam out. \n"
                               "To make verification faster, I have looked up your discord username on osu "
                               "and found this profile. \n"
                               "Since you have specified your Discord account on osu and the 4 digits also match, "
                               "I'll link you to that profile. "
                               "If something is incorrect, let us know.")
            await self.profile_id_verification(channel, member, profile_id, True)
            return

        if self.autodetect_profile_inquiry_conditions(fresh_osu_data, member):
            await channel.send(content=f"Welcome {member.mention}! We have a verification system in this server "
                                       "so we can give you appropriate roles and keep raids/spam out. \n"
                                       "Is this your osu! profile? "
                                       "If yes, type `yes`, if not, post a link to your profile.",
                               embed=await osuwebembed.small_user_array(fresh_osu_data))
        else:
            await channel.send(f"Welcome {member.mention}! We have a verification system in this server "
                               "so we can give you appropriate roles and keep raids/spam out. \n"
                               "Please post a link to your osu! profile and I will verify you instantly.")

    def autodetect_profile_proven(self, member, fresh_osu_data):
        try:
            if fresh_osu_data['discord']:
                if str(member) == str(fresh_osu_data['discord']):
                    return True
        except KeyError:
            pass
        return False

    def autodetect_profile_inquiry_conditions(self, fresh_osu_data, member):
        try:
            if self.is_new_user(member):
                return False

            if not fresh_osu_data:
                return False

            if fresh_osu_data['last_visit']:
                last_visit = dateutil.parser.parse(fresh_osu_data['last_visit'])

                user_creation_ago = datetime.datetime.now().timestamp() - last_visit.timestamp()
                if user_creation_ago / 60 / 60 / 24 > 30:
                    return False

            if fresh_osu_data["statistics"]:
                if float(fresh_osu_data["statistics"]["pp"]) < 100:
                    return False

            if str(member.name).lower() != str(fresh_osu_data["username"]).lower():
                return False

            # if fresh_osu_data['discord']:
            #     if "#" in fresh_osu_data['discord']:
            #         if str(member.discriminator) == str(((fresh_osu_data['discord']).split("#"))[-1]):
            #             return True

            return True
        except:
            return False

    async def count_ranked_beatmapsets(self, beatmapsets):
        try:
            count = 0
            if beatmapsets:
                for beatmapset in beatmapsets:
                    if int(beatmapset.approved) == 1 or int(beatmapset.approved) == 2:
                        count += 1
            return count
        except Exception as e:
            print(e)
            return 0

    async def add_obligatory_reaction(self, message, country):
        try:
            if country:
                for stereotype in self.post_verification_emotes:
                    if country == stereotype[0]:
                        await message.add_reaction(stereotype[1])
        except Exception as e:
            print(e)

    def is_new_user(self, user):
        user_creation_ago = datetime.datetime.utcnow() - user.created_at
        if abs(user_creation_ago).total_seconds() / 2592000 <= 1 and user.avatar is None:
            return True
        else:
            return False

    async def check_group_roles(self, channel, member, guild, fresh_osu_data):
        group_roles = [
            [7, await verification_reusables.get_role_from_db(self, "nat", guild)],
            [28, await verification_reusables.get_role_from_db(self, "bn", guild)],
            [32, await verification_reusables.get_role_from_db(self, "bn", guild)],
        ]

        user_qualifies_for_these_roles = await self.get_user_qualified_group_roles(fresh_osu_data, group_roles)

        if user_qualifies_for_these_roles:
            for role_to_add in user_qualifies_for_these_roles:
                try:
                    await member.add_roles(role_to_add)
                    await channel.send(f"additionally, i applied the {role_to_add} role")
                except:
                    pass

    async def get_user_qualified_group_roles(self, fresh_osu_data, group_roles):
        return_list = []
        for group in fresh_osu_data["groups"]:
            for group_role in group_roles:
                if int(group["id"]) == int(group_role[0]):
                    return_list.append(group_role[1])
        return return_list

    def get_correct_embed_trust_color(self, member, fresh_osu_data):
        try:
            if fresh_osu_data['discord']:
                if str(member) == str(fresh_osu_data['discord']):
                    return 0x00ff00
        except KeyError:
            pass

        if self.user_is_suspicious(fresh_osu_data):
            return 0xff0000

        try:
            if fresh_osu_data['discord']:
                if str(member) != str(fresh_osu_data['discord']):
                    return 0xff5500
        except KeyError:
            pass

        return 0xffbb00

    def user_is_suspicious(self, fresh_osu_data):
        join_date = dateutil.parser.parse(fresh_osu_data['join_date'])

        account_age_seconds = datetime.datetime.now().timestamp() - join_date.timestamp()
        if account_age_seconds / 60 / 60 / 24 < 30:
            return True

        if self.last_visit_check(fresh_osu_data):
            return True

        if fresh_osu_data["statistics"]:
            if float(fresh_osu_data["statistics"]["pp"]) < 100:
                return True

        return False

    def last_visit_check(self, fresh_osu_data, day_amount=30):
        if not fresh_osu_data['last_visit']:
            return False

        last_visit = dateutil.parser.parse(fresh_osu_data['last_visit'])

        seconds_since_last_visit = datetime.datetime.now().timestamp() - last_visit.timestamp()
        if seconds_since_last_visit / 60 / 60 / 24 > day_amount:
            return True

        return False


def setup(bot):
    bot.add_cog(MemberVerification(bot))
