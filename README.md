# Seija
Hi, if you are reading this, I am most likely gone, otherside you would not have access to this.
Anyways, I am leaving the source code behined so the next person who will take my role can get the place back up and running with minimal effort. 

This bot is built using discord.py rewrite library and uses sqlite3 database.

---

## Installation Instructions

1. Unpack files
2. Install git.
3. Install `python 3.6.7` or newer
4. Install `discord.py rewrite library` using this command `python -m pip install -U discord.py[voice]` for Windows and `python3 -m pip install -U discord.py[voice]` for Linux.
5. `pip install upsidedown feedparser pycountry Pillow`. (`pip3` on linux)
6. Before using, you need to create a folder called `data` and create `token.txt` and `osuapikey.txt` in it. Then put your bot token and osu api key in the files. 
7. If you have an access to `maindb.sqlite3` file which is a database backup, put it in `data` folder before running the bot. Make sure you add your discord id in `admins` table though with permissions of `1`. There can only be one user with that perms, so, remove any other id with permissions of `1`. You can use [this](https://sqlitebrowser.org/) to manually edit sqlite3 database files.
8. Run `run.py` with command line, like `python run.py` on windows or `python3 run.py` on linux or use the batch file or however you want. It's recommended to run it in a loop so it restarts when it exits. Built-in updater requires this.

## After running do these

1. Type following commands in chat. (the first id in each command is the id if the Mapset Management Server.)
```
'sql INSERT INTO config VALUES ('verifychannelid', '460935664712548366', '460952470634496001', '0')
'sql INSERT INTO config VALUES ('vetochannelid', '460935664712548366', '502705804990742573', '0')
'sql INSERT INTO config VALUES ('verifyroleid', '460935664712548366', '463790447912026132', '0')
'sql INSERT INTO config VALUES ('dbdumpchannelid', '460935664712548366', '532397839784083458', '0')
'sql INSERT INTO config VALUES ('guildmapsetcategory', '460935664712548366', '460935665165795328', '0')
'sql INSERT INTO config VALUES ('guildqueuecategory', '460935664712548366', '488831339634753546', '0')
'sql INSERT INTO config VALUES ('guildarchivecategory', '460935664712548366', '491572368221929472', '0')
```
2. Use `'makeadmin <new admin discord id>` to make users bot admins.
3. Use `'track <mapsetid> <mapset host discord id>` to track mapsets.
4. Figure out the rest yourselves. `'help` and `'help admin` commands exist.
