import discord
from discord.ext.commands import Bot
from selenium import webdriver
from selenium.webdriver.common.by import By
from prettytable import PrettyTable
import time
import asyncio
import binascii
import ast
import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

with open('private_key.pem', 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

with open('public_key.pem', 'rb') as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )

# Bot token
TOKEN = ''
invite = 'https://discord.com/api/oauth2/authorize?client_id=1128102633312370838&permissions=380104817664&scope=bot'
# Above is the link for the bot

# Logging data
logging.basicConfig(filename="scrapper.log", filemode="a", format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S", level=logging.INFO)
logging.info('')
logging.info('')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.typing = False
intents.presences = False

# Create bot object
client = Bot(command_prefix="!", intents=intents)

# define a function that is run on the on_message event
bot_id = 1128102633312370838
me_id = 459744351715590173
channels = []
obj_links = []
admins = []
blacklist = []
servers = []
url_check = 'https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept='
setup = False
tskip = 600
guilds = []
cuttime = 24 * 60 * 60
warn = 23 * 60 * 60

tab = PrettyTable(["Command", "Desc"])
tab.add_row(["!hello", "Greetings, what do you expect it to do lol."])
tab.add_row(["!help", "Opens this menu"])
tab.add_row(["!link", "Returns the invite link to add this bot to a server"])
tab.add_row(["!setup", "Allows a one time use of the !add-admin: command by anyone. Can only be activated once"])
tab.add_row(["!ping", "Ping the specified UBC server after setting it up in the channel.\nCan only be run while the"
                      " Scrapper is already running."])

tab2 = PrettyTable(["Admin Cmd", "Admin Cmd Desc"])
tab2.add_row(["!add-admin:@---", "Adds the mentioned user to the list of admins granting authority too run all\nadmin"
                                 " commands"])
tab2.add_row(["!scrapper", "Starts a Scrapper instance for that specific channel"])
tab2.add_row(["!res:", "Restarts a Scrapper instance based on the return from the !hash command."])
tab2.add_row(["!end", "Ends the Scrapper instance for that specific channel"])
tab2.add_row(["!hash", "Returns a runnable command to restart the Scrapper instance from any channel\nif the bot goes"
                       "down or you need to change channels"])
tab2.add_row(["!status", "Check if it is possible to ping the server/run the Scrapper"])
tab2.add_row(["!set-url:---", "Sets the ping url to specified url. Space sensitive (no spaces).\nTo specify the"
                              " Okanagan campus add &campuscd=UBCO to the end of the url.\nWill not work with urls'"
                              " outside of ubc."])
tab2.add_row(["!set-lab:---", "States if there are labs/discussions in the course. Default set to False"])
tab2.add_row(["!set-role:@---", "Takes the first role mentioned and sets it to ping given role when the course\ngets"
                                " some space"])

tab3 = PrettyTable(["Admin Cmd", "Admin Cmd Desc"])
tab3.add_row(["!sec", "Returns the sections already in the sections list"])
tab3.add_row(["!set-sec:---", "Sets if there are specific sections to check for or not. Default set to False"])
tab3.add_row(["!add-sec:---", "Takes the text to the right of colon and added it to sections to check. Space\n"
                              "sensitive (checks for space as part of the section)"])
tab3.add_row(["!rmv-sec:---", "Takes the text to the right of colon and removes it from sections to check.\nSpace"
                              " sensitive (will not be able to remove if not exact match with entry)"])
tab3.add_row(["!emt-sec", "Empties the List of sections"])
tab3.add_row(["!restricted:---", "Sets whether to include when given course has restricted space.\nDefault set to"
                                 " False"])
tab3.add_row(["!waitlist:---", "Sets it the program should return Waitlists' for courses. Default set to False"])
tab3.add_row(["!run", "Runs the bot. It will ping the server every 10 minutes until\nthere is space or the bot is"
                      " stopped."])
tab3.add_row(["!stop", "Stops the bot"])


@client.event
async def on_ready():
    logging.info('Bot Start Up')
    logging.info(f'Logged in as {client.user.name} ({client.user.id})')
    global guilds
    for guild in client.guilds:
        guilds.append(guild)
        i = 0
        while True:
            try:
                await guild.text_channels[i].send("Please set up the scrapping instances again. The bot was down for maintenance")
                break
            except discord.errors.Forbidden:
                i += 1

    await garbage()


# Garbage collector, removes all scrapper instances unless used in last 1 day, based on values.
async def garbage():
    logging.info('Garbage Collector Started')
    while True:
        curr = time.time()
        for obj in obj_links:
            gap = curr - obj.lasttime
            if gap > cuttime:
                logging.info(f'Terminating Scrapping Instance: {obj.chan}')
                await obj.chan.send("This scrapper instance has been closed.")
                place = obj_links.index(obj)
                del channels[place]
                del obj_links[place]
            elif gap > warn:
                await obj.chan.send("This scrapper instance will be closed in 1 hour unless used.")
        await asyncio.sleep(3600)


@client.event
async def on_guild_join(guild):
    global guilds
    guilds.append(guild)
    i = 0
    logging.info(f'Joined new Guild: {guild}')
    while True:
        try:
            await guild.text_channels[i].send("Hello, this is a bot designed to scrap course information & availability"
                    " from UBC website.\nIn order to use, first start a Scrapper instance using !scrapper.\n Then"
                    " set the url to the course overview url using \"!set-url:---\", assign the bot a role to ping"
                    " when there is space using \"!set-role:---\".\nYou should further specify if there are"
                    " labs/discussions included on the page.\nYou can further specify which sections to check.\nThen"
                    " you just need to run Scrapper using then \"!run\" command.\nThe bot is will run itself every 10"
                    " minutes.\nYou can run a different instance of the bot in a separate channel allowing for multiple"
                    " course Scrappers.\nTo find all runnable commands run !help.\n\nIn order to any propose changes,"
                    " please get in contact with the bot creator.")
            break
        except discord.errors.Forbidden:
            i += 1


@client.event
async def on_guild_remove(guild):
    global guilds
    guilds.remove(guild)
    logging.info(f'Removed from Guild: {guild}')


@client.event
async def on_message(message):
    if message.author.bot:
        return
    bypass = False
    if message.author.id == me_id:
        bypass = True
    channel = message.channel
    msg = message.content.lower()

    global channels, obj_links, servers, setup, guilds, blacklist

    # await message.channel.send(f"<@{message.author.id}>")
    # await message.channel.send(f"@everyone")
    # Testing how to ping a role instead of everyone below msg does the same
    # await message.channel.send(message.content)

    if msg[:1] == "!":
        global admins, blacklist
        # Core highest commands
        if bypass:
            global servers
            if "!!!time:" == msg[:8]:
                global tskip
                tskip = int(msg[8:])
                logging.info(f'High  Com.     Check time changed to: {tskip}')
                await message.reply("Rest time set to: " + str(tskip))
            elif "!!!rmv:" == msg[:7]:
                if admins.__contains__(message.mentions[0].id):
                    admins.remove(message.mentions[0].id)
                    logging.info(f'High  Com.     Admin Removal: {message.mentions[0].name} ({message.mentions[0].id})')
            elif "!!!broadcast:" == msg[:13]:
                logging.info(f'High  Com.     Broadcast: {msg[13:]}')
                for guild in guilds:
                    i = 0
                    while True:
                        try:
                            await guild.text_channels[i].send("Message from admin >>>\n" + message.content[13:])
                            await message.channel.send(f"Message sent to server: {guild.name} ({guild.id})")
                            logging.info(f'High  Com.     Broadcast sent to {guild.name} ({guild.id})')
                            break
                        except discord.errors.Forbidden:
                            i += 1
            elif "!!!flush" == msg:
                channels = []
                obj_links = []
                servers = []
                setup = False
                logging.info(f'High  Com.     All flushed')
                await on_ready()
            elif "!!!blacklist:" == msg[:13]:
                for user in message.mentions:
                    if admins.__contains__(user.id):
                        admins.remove(user.id)
                        await message.reply(user.name + " removed from admins")
                        logging.info(f'High  Com.     Admin Removal: {user.name} ({user.id})')
                    if blacklist.__contains__(user.id):
                        await message.reply(user.name + " already in blacklist")
                    else:
                        blacklist.append(user.id)
                        await message.reply(user.name + " added to blacklist")
                        logging.info(f'High  Com.     Blacklist Addition: {user.name} ({user.id})')
            elif "!!!whitelist:" == msg[:13]:
                for user in message.mentions:
                    if blacklist.__contains__(user.id):
                        blacklist.remove(user.id)
                        await message.reply(user.name + " removed from blacklist")
                        logging.info(f'High  Com.     Blacklist Removal: {user.name} ({user.id})')
            elif "!!!gtime:" == msg[:9]:
                t = float(msg[9:])
                global cuttime, warn
                cuttime = t * 24 * 60 * 60
                warn = cuttime - 3600
                await message.reply(f"Garbage time changed to {t} days or {cuttime} seconds.")
                logging.info(f'High  Com.     Garbage time: {t} days / {cuttime} seconds')
            elif "!!!pull1" == msg:
                await message.channel.send("!!!reinstate:" + str(admins))
                logging.info(f'High  Com.     Pull1 Admins Called')
            elif "!!!pull2" == msg:
                await message.channel.send("!!!black:" + str(blacklist))
                logging.info(f'High  Com.     Pull2 Blacklist Called')
            elif "!!!pull3" == msg:
                await message.channel.send("!!!servers:" + str(servers))
                logging.info(f'High  Com.     Pull3 Guilds Called')
            elif "!!!pull4" == msg:
                await message.channel.send(f"!!!times:{tskip},{cuttime},{warn}")
                logging.info(f'High  Com.     Pull4 Application times Called')
            elif "!!!reinstate:" == msg[:14]:
                admins = ast.literal_eval(msg[14:])
                await message.channel.send("Admins back.")
                logging.info(f'High  Com.     Reinstate Admins')
            elif "!!!black:" == msg[:9]:
                blacklist = ast.literal_eval(msg[9:])
                await message.channel.send("Blacklist back")
                logging.info(f'High  Com.     Reinistate Blacklist')
            elif "!!!servers:" == msg[:11]:
                servers = ast.literal_eval(msg[11:])
                await message.channel.send("Servers with setup used back.")
                logging.info(f'High  Com.     Reinstate Guilds')
            elif "!!!times:" == msg[:9]:
                split = msg[9:].split(",")
                tskip = split[0]
                cuttime = split[1]
                warn = split[2]
                await message.channel.send("Timings in place.")
                logging.info(f'High  Com.     Reinstate Times')

        # Everyone commands
        if "!hello" == msg:
            await message.reply("Greetings " + message.author.nick + ".")

        elif "!link" == msg:
            await message.reply(invite)

        elif "!help" == msg:
            tab_str = "```\n" + tab.get_string() + "\n```"
            tab2_str = "```\n" + tab2.get_string() + "\n```"
            tab3_str = "```\n" + tab3.get_string() + "\n```"
            await message.channel.send(tab_str)
            await message.channel.send(tab2_str)
            await message.channel.send(tab3_str)

        elif "!setup" == msg:
            if servers.__contains__(message.guild.id):
                await message.channel.send("This is not a new server, ask a current admin to add privileges for you.")
            else:
                setup = True
                await message.channel.send("The !add-admin:@--- command is available for a one time use by anyone.")
                logging.info(f'Gen.  Com.     Setup Called {message.guild} ({message.guild.id}) by {message.author.name} ({message.author.id})')

        elif channels.__contains__(channel) and "!ping" == msg:
            temp = obj_links[channels.index(channel)]
            if temp.running:
                await _once_(temp, message)

        elif "!add-admin:" == msg[:11]:
            if setup:
                admin = False
                for user in message.mentions:
                    if not (admins.__contains__(user.id) and blacklist.__contains__(user.id)):
                        admins.append(user.id)
                        await message.channel.send(f"<@{user.id}> added to admins.")
                        logging.info(f'Gen.  Com.     {message.author.name} ({message.author.id}) Setup One time user, {message.guild.name} ' +
                                     f'({message.guild.id}); Admin Addition: {user.name} ({user.id})')
                        admin = True
                if admin:
                    servers.append(message.guild.id)
                    setup = False
            elif admins.__contains__(message.author.id) or bypass:
                for user in message.mentions:
                    if not (admins.__contains__(user.id) and blacklist.__contains__(user.id)):
                        admins.append(user.id)
                        await message.channel.send(f"<@{user.id}> added to admins.")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Admin Addition: {user.name} ({user.id})')
            else:
                await message.reply("You do not have sufficient permissions")

        # Admin commands
        elif admins.__contains__(message.author.id) or bypass:
            if "!scrapper" == msg:
                if channels.__contains__(channel):
                    await message.channel.send("This channel already has a scrapper, run !end to end it")
                else:
                    logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Creating Scrapping Instance: {channel}')
                    await message.channel.send("Created scrapper instance for channel")
                    channels.append(channel)
                    obj_links.append(Scrapper(message.channel, ''))

            elif "!res:" == msg[:5]:
                if channels.__contains__(channel):
                    await message.channel.send("This channel already has a scrapper, end its instance using !end first"
                                               " then send this command again.")
                else:
                    temp = binascii.a2b_hex(message.content[5:])
                    result = decryptme(temp)
                    if not result:
                        await message.channel.send("Decrypting failed, value tampered with.")
                    else:
                        channels.append(channel)
                        temp = str(result)[2:][:-1]
                        obj_links.append(Scrapper(message.channel, temp))
                        await message.channel.send("Instance recalled. Scrapper ready to run.")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Restarting Scrapping Instance: {channel} with' +
                                     f' inputs: {result}')

            elif channels.__contains__(channel):
                place = channels.index(channel)
                obj = obj_links.__getitem__(place)

                if "!end" == msg:
                    del channels[place]
                    del obj_links[place]
                    await message.channel.send("Scrapper instance for channel closed")
                    logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Closing scrapping instance {channel}')

                # elif "!print" == msg:
                #     obj.print()

                elif "!hash" == msg:
                    temp = obj.restart()
                    if temp is True:
                        await message.channel.send("The Scrapper is not ready to be run, hence cannot generate a code.")
                    else:
                        val = temp.hex()
                        val = "!res:" + val
                        await message.channel.send(val)

                elif "!status" == msg:
                    if obj.cur_status():
                        await message.channel.send("Required fields filled")
                    else:
                        await message.channel.send("Not Ready")

                elif "!set-url:" == msg[:9]:
                    # To get into the Okanagan website add &campuscd=UBCO. like wise for the van website &campuscd=UBC
                    if url_check in msg[9:97]:
                        await message.channel.send("UBC course url found")
                        obj.set_url(message.content[9:])
                        await message.channel.send("URL set to: " + obj.url)
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan}; URL Changed: {obj.url}')
                    else:
                        await message.channel.send("This bot only supports UBC courses as of now, or the input is in an"
                                                   " incorrect format. An example input would be: !set-url:"
                                            "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname="
                                                   "subj-course&dept=MATH&course=100)\nNot this only works with course"
                                                   " overview not a specific section. Please do not insert spaces.")

                elif "!set-lab:" == msg[:9]:
                    if "false" in msg:
                        obj.set_lab(False)
                        await message.channel.send("Labs/Discussions: False")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Lab Set to: False')
                    elif "true" in msg:
                        obj.set_lab(True)
                        await message.channel.send("Labs/Discussions: True")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Lab Set to: True')
                    else:
                        await message.channel.send("Invalid input")

                elif "!sec" == msg:
                    await message.channel.send(obj.sections)

                elif "!set-sec:" == msg[:9]:
                    if "false" in msg:
                        obj.set_sec(False)
                        await message.channel.send("Specific Sections: False")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Section Checks Set to: False')
                    elif "true" in msg:
                        obj.set_sec(True)
                        await message.channel.send("Specific Sections: True")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Section Checks Set to: True')
                    else:
                        await message.channel.send("Invalid input")

                elif "!add-sec:" == msg[:9]:
                    obj.add_sec(message.content[9:])
                    await message.channel.send(msg[9:] + " added to included sections")
                    logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Section Added: {msg[9:]}')

                elif "!rmv-sec:" == msg[:9]:
                    if obj.rmv_sec(message.content[9:]):
                        await message.channel.send(msg[9:] + " removed from included sections")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Section Removed: {msg[9:]}')
                    else:
                        await message.channel.send(msg[9:] + " section does not exist in list")

                elif "!emt-sec" == msg[:8]:
                    obj.emt_sec()
                    await message.channel.send("Sections list has been emptied")
                    logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Sections Emptied')

                elif "!set-role:" == msg[:10]:
                    obj.set_role(message.role_mentions[0])
                    await message.channel.send("Role ping changed to: " + obj.role)
                    logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Role Ping: {obj.role}')

                elif "!restricted:" == msg[:12]:
                    if "false" in msg:
                        obj.set_restricted(False)
                        await message.channel.send("Return Restricted: False")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Restricted: False')
                    elif "true" in msg:
                        obj.set_restricted(True)
                        await message.channel.send("Return Restricted: True")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Restricted: True')
                    else:
                        await message.channel.send("Invalid input")

                elif "!waitlist:" == msg[:10]:
                    if "false" in msg:
                        obj.set_waitlist(True)
                        await message.channel.send("Waitlists: False")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Waitlist: False')
                    elif "true" in msg:
                        obj.set_waitlist(False)
                        await message.channel.send("Waitlists: True")
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Waitlist: True')
                    else:
                        await message.channel.send("Invalid input")

                elif "!run" == msg:
                    if obj.cur_status():
                        obj.running = True
                        await _main_(obj, message)
                        logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Running')

                elif "!stop" == msg:
                    obj.running = False
                    logging.info(f'Admin Com.     {message.author.name} ({message.author.id}) Channel {obj.chan} Stopped')
        else:
            await message.channel.reply("This Command does not exist or you do not have sufficient privileges.")


def encryptme(inp):
    message = inp.encode()
    encrypted = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted


def decryptme(inp):
    try:
        decrypted = private_key.decrypt(
            inp,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return str(decrypted)
    except ValueError:
        print("Decrypting failed, value tampered")
        return False


async def _once_(obj, message):
    obj.lasttime = time.time()
    obj.__main__()
    obj.rmv_n_fill()
    if obj.empty():
        await obj.chan.send("No changes to course.")
        print("No change to course " + obj.role)
    else:
        await ping(obj, message)
        i = 0
        t = PrettyTable(["Status", "Course", "Link"])
        for space in obj.status:
            t.add_row([space, obj.course[i], obj.links[i]])
            i += 1
        await obj.chan.send(t)


async def _main_(obj, message):
    while obj.running:
        obj.__main__()
        obj.rmv_n_fill()
        obj.lasttime = time.time()
        if obj.empty():
            await obj.chan.send("No changes to course.")
        else:
            await ping(obj, message)
            i = 0
            t = PrettyTable(["Status", "Course", "Link"])
            for space in obj.status:
                t.add_row([space, obj.course[i], obj.links[i]])
                i += 1
            await obj.chan.send(t)
            obj.running = False
            logging.info(f'               Channel {obj.chan}; Role {obj.role}; Instance found. Stopping Bot...')
        if obj.running:
            await asyncio.sleep(tskip)
            # change this to change frequency of pings


async def ping(obj, message):
    role = discord.utils.get(message.guild.roles, name=obj.role)
    if role:
        await message.channel.send(f'{role.mention}')


# how to send a msg
# await message.channel.send("One msg (message.content)" + message.content)

# Web Scrapping code, copied to not have multiple files.

class Scrapper(object):
    chan = None
    url = ''
    labs = False
    specific = False
    sections = []
    ready = False
    keep_restricted = False
    role = ''
    running = False
    waitlist = True
    ubco = False
    lasttime = 0

    status = []
    course = []
    links = []

    def __init__(self, channel, data):
        self.chan = channel
        if data == '':
            self.url = ''
            self.labs = False
            self.specific = False
            self.sections = []
            self.ready = False
            self.keep_restricted = False
            self.role = ''
            self.waitlist = False
            self.ubco = False
        else:
            split = data.split("//")
            i = 0
            self.url = url_check + split[i]
            i += 1
            if split[i] == 'T':
                self.labs = True
            else:
                self.labs = False
            i += 1
            if split[i] == "T":
                self.specific = True
                i += 1
                self.sections = ast.literal_eval(split[i])
            else:
                self.specific = False
            i += 1
            if split[i] == "T":
                self.ready = True
            else:
                self.ready = False
            i += 1
            if split[i] == "T":
                self.keep_restricted = True
            else:
                self.keep_restricted = False
            i += 1
            self.role = split[i]
            i += 1
            if split[i] == "T":
                self.waitlist = True
            else:
                self.waitlist = False
            i += 1
            if split[i] == "T":
                self.ubco = True
            else:
                self.ubco = False

        self.running = False

        self.lasttime = time.time()

        self.status = []
        self.course = []
        self.links = []

    def restart(self):
        if not self.cur_status():
            return True
        text = self.url[88:]
        if self.labs:
            text = text + "//T"
        else:
            text = text + "//F"

        if self.specific:
            text = text + "//T//"
            text = text + str(self.sections)
        else:
            text = text + "//F"

        if self.ready:
            text = text + "//T"
        else:
            text = text + "//F"

        if self.keep_restricted:
            text = text + "//T"
        else:
            text = text + "//F"

        text = text + "//" + self.role

        if self.waitlist:
            text = text + "//T"
        else:
            text = text + "//F"

        if self.ubco:
            text = text + "//T"
        else:
            text = text + "//F"

        return encryptme(text)

    # This was for testing
    # def print(self):
    #     print(f"Channel: \t {self.chan}")
    #     print(self.chan)
    #     # I am not dealing with the channel, so I just need to ignore this.
    #     # The following are good to go
    #     print(f"Url: \t {self.url}")
    #     print(f"Labs: \t {self.labs}")
    #     print(f"Specific: \t {self.specific}")
    #     print(f"Sections: \t {self.sections}")
    #     print(f"Ready: \t {self.ready}")
    #     print(f"Keep Restricted: \t {self.keep_restricted}")
    #     print(f"Role: \t {self.role}")
    #     print(f"Waitlist: \t {self.waitlist}")
    #     print(f"UBCO: \t {self.ubco}")

    def cur_status(self):
        self.lasttime = time.time()
        if not len(self.url) == 0:
            if not len(self.role) == 0:
                if self.specific:
                    self.ready = not (len(self.sections) == 0)
                    return self.ready
                self.ready = True
                return self.ready
        self.ready = False
        return self.ready

    def set_url(self, inp):
        self.lasttime = time.time()
        self.url = inp
        if "&campuscd=UBCO" in inp:
            self.ubco = True
        print("Set the url to: " + inp)

    def set_lab(self, inp):
        self.lasttime = time.time()
        self.labs = inp
        print("Set labs to: " + str(inp))

    def set_sec(self, inp):
        self.lasttime = time.time()
        self.specific = inp
        print("Set specifications to: " + str(inp))

    def add_sec(self, inp):
        self.lasttime = time.time()
        if inp in self.sections:
            return
        self.sections.append(inp)
        print("Added section: " + inp)

    def rmv_sec(self, inp):
        self.lasttime = time.time()
        if self.sections.__contains__(inp):
            self.sections.remove(inp)
            print("Removed section: " + inp)
            return True
        else:
            return False

    def emt_sec(self):
        self.lasttime = time.time()
        self.sections.clear()
        print("Sections list has been emptied")

    def set_restricted(self, inp):
        self.lasttime = time.time()
        self.keep_restricted = inp
        print("Return Restricted: " + str(inp))

    def set_role(self, inp):
        self.lasttime = time.time()
        self.role = str(inp)
        print("Role ping changed to: " + str(inp))

    def set_waitlist(self, inp):
        self.lasttime = time.time()
        self.waitlist = inp
        print("Waitlist changed to: " + str(inp))

    # Scrapper code
    def __main__(self):
        self.status = []
        self.course = []
        self.links = []

        driver = webdriver.Chrome()
        driver.implicitly_wait(1)
        driver.get(self.url)

        # section1 = lec
        # section2 = labs || discussions
        # a waitList can be either. All waitlists are removed by default.
        # in the event there are no labs|discussions, section2 is another lec
        if self.labs:
            l = driver.find_elements(By.CLASS_NAME, 'section1')
        else:
            l1 = driver.find_elements(By.CLASS_NAME, 'section1')
            l2 = driver.find_elements(By.CLASS_NAME, 'section2')
            l = []
            no_last = False
            if len(l1) == len(l2):
                no_last = True
            for i in range(0, len(l2)):
                l.append(l1[i])
                l.append(l2[i])
            if not no_last:
                l.append(l1[-1])

        i = 0
        while self.waitlist:
            if i >= len(l):
                break
            if "Waiting List" in str(l[i]):
                l.remove(l[i])
                i -= 1
            i += 1

        found = False

        if self.specific:
            # Had to remove another for loop cause it was breaking my code :(
            i = 0
            while True:
                if i >= len(l):
                    break
                data = l[i].get_attribute('innerHTML')
                for section in self.sections:
                    if section in data:
                        found = True
                        break
                if not found:
                    l.remove(l[i])
                    i -= 1
                found = False
                i += 1

        for item in l:
            data = item.get_attribute('innerHTML')
            split = data.split('</td>')
            if ' ' in split[0].split('>')[1]:
                self.status.append('Space')
            else:
                self.status.append(split[0].split('>')[1])
            self.course.append(split[1].split('">')[1].split('</')[0])
            temp = 'https://courses.students.ubc.ca' + split[1].split('">')[0].split('"')[1]
            link = ''
            for part in temp.split('amp;'):
                link = link + part
            if self.ubco:
                link = link + "&campuscd=UBCO"
            else:
                link = link + "&campuscd=UBC"
            self.links.append(link)

    def rmv_n_fill(self):
        if not self.empty():
            # for loops use lists so the direct manipulation of vars not good, while is better. Change
            # range(0,5) returns a list of [0,1,2,3,4,5] so the i manipulation changes the int at i index, we never
            # check that int again making that code useless.
            i = 0
            while True:
                if i >= len(self.status):
                    break
                if self.keep_restricted:
                    if not (('Space' == self.status[i]) or ('Restricted' == self.status[i])):
                        self.status.remove(self.status[i])
                        self.course.remove(self.course[i])
                        self.links.remove(self.links[i])
                        i -= 1
                else:
                    if not ('Space' == self.status[i]):
                        self.status.remove(self.status[i])
                        self.course.remove(self.course[i])
                        self.links.remove(self.links[i])
                        i -= 1
                i += 1

    def empty(self):
        if len(self.status) == 0:
            return True
        else:
            return False


client.run(TOKEN)
