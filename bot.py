import discord
from dotenv import load_dotenv
from os import getenv
import os
import time
from commands import *

class buttonRole:
    def __init__(self, role: discord.Role, style, emoji: str):
        self.role = role
        self.label = role.name
        if style.lower() == 'primary' or style.lower() == 'blurple':
            self.style = discord.ButtonStyle.primary
        elif style.lower() == 'secondary' or style.lower() == 'gray':
            self.style = discord.ButtonStyle.secondary
        elif style.lower() == 'success' or style.lower() == 'green':
            self.style = discord.ButtonStyle.success
        elif style.lower() == 'danger' or style.lower() == 'red':
            self.style = discord.ButtonStyle.danger
        elif style.lower() == 'link' or style.lower() == 'url':
            self.style = discord.ButtonStyle.link
        elif style.lower() == 'dropdown':
            self.style = None
        else:
            raise NameError('Button Style Not Found')
        self.emoji = emoji

def start():
    # Load Token
    load_dotenv()
    TOKEN = getenv('TOKEN')
    if TOKEN is None:
        print('oi mate you might wanna give me ur token, just sayin')
        raise NameError('Missing Token')
    
    # Set Bot Intents
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    # Set Client Variables
    global client
    global tree
    client = discord.Client(intents=intents)
    tree = discord.app_commands.CommandTree(client)

    # Set Dynamic Variables
    global channels
    global roles
    global emojis
    global assets
    global importedCommands
    channels = []
    roles = {}
    emojis = {}
    assets = []
    importedCommands = []

    # Set Functions/Lambdas
    def printEmoji(emoji: str):
        return f'<:{emojis[emoji].name}:{emojis[emoji].id}>'

    async def memberStatusUpdate(inServer: bool, member):
        for channel in client.get_all_channels():
            if channel.guild == member.guild and member.guild.system_channel == channel:
                if isinstance(channel, discord.TextChannel):
                    if inServer:
                        await channel.send(f'{member.mention} Welcome to the Chaos')
                    else:
                        await channel.send(f'{member.mention} Couldn\'t handle the chaos smh')
                    break

    async def sendButtonRoles(buttonRole, channel, message: str, dropdown: bool = False):
        def gen_callback(role):
            async def button_callback(interaction: discord.Interaction):
                if interaction.user in role.members:
                    await interaction.user.remove_roles(role)  # type: ignore
                    await interaction.response.send_message(f'Removed Role: `{role.name}`', ephemeral=True)
                else:
                    await interaction.user.add_roles(role)  # type: ignore
                    await interaction.response.send_message(f'Added Role: `{role.name}`', ephemeral=True)
            return button_callback
        def gen_select_callback(select: discord.ui.Select):
            async def select_callback(interaction: discord.Interaction):
                response=''
                for role in buttonRole:
                    if interaction.user in role.role.members:
                        await interaction.user.remove_roles(role.role)  # type: ignore
                        response+=f'Removed Role: `{role.role.name}`\n'
                for role in buttonRole:
                    if select.values[0] == role.label:
                        if interaction.user in role.role.members:
                            await interaction.user.remove_roles(role.role)  # type: ignore
                            response+=f'Removed Role: `{role.role.name}`\n'
                        else:
                            await interaction.user.add_roles(role.role)  # type: ignore
                            response+=f'Added Role: `{role.role.name}`\n'
                await interaction.response.send_message(response, ephemeral=True)
            return select_callback

        view = discord.ui.View(timeout=None)
        if dropdown:
            select = discord.ui.Select()
            for role in buttonRole:
                option = discord.SelectOption(
                    label=role.label,
                    emoji=role.emoji
                )
                select.append_option(option)
            view.add_item(select)
            select.callback = gen_select_callback(select)
        else:
            for role in buttonRole:
                button = discord.ui.Button(
                    label=role.label,
                    style=role.style,
                    emoji=role.emoji
                )
                button.callback = gen_callback(role.role)
                view.add_item(button)

        await channel.send(message, view=view)

    # Set Events
    @client.event
    async def on_ready():
        print(f'{client.user} active')
        if 'debug' in os.listdir('./'):
            await client.change_presence(activity=discord.Game(name="DEBUG MODE"))
            print('Bot Presence changed to \"Playing DEBUG MODE\"')
            for guild in client.guilds:
                for channel in guild.text_channels:
                    if channel.topic != None:
                        if 'Bot Info' in channel.topic:
                            await channel.send(embed=discord.Embed(
                                title='Online Status',
                                description=f'Skyline\'s Alter Ego Online Since <t:{str(int(time.time()))}:R> <@&1071866381894692895>',
                                color=discord.Color.green()
                                ))
        else:
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the chaos unfold"))
            print('Bot Presence changed to \"Watching the chaos unfold\"')
            for guild in client.guilds:
                for channel in guild.text_channels:
                    if channel.topic != None:
                        if 'Bot Info' in channel.topic:
                            await channel.send(embed=discord.Embed(
                                title='Online Status',
                                description=f'Skyline\'s Alter Ego Online Since <t:{str(int(time.time()))}:R>',
                                color=discord.Color.green()
                                ))

        # Channel Detection
        for guild in client.guilds:
            for channel in guild.channels:
                channels.append(channel)

        # Role Detection
        for guild in client.guilds:
            for role in guild.roles:
                roles[f'@{role.name}'] = role

        # Emoji Detection
        for guild in client.guilds:
            for emoji in guild.emojis:
                emojis[f':{emoji.name}:'] = emoji

        # Command Import
        for command in os.listdir('commands'):
            for command in os.listdir('commands'):
                if command.endswith('py'):
                    if '__init__.py' not in command:
                        if 'template.py' not in command:
                            if command not in importedCommands:
                                exec(f'import commands.{command[:-3]}')
                                exec(
                                    f'commands.{command[:-3]}.import_command()')
                                importedCommands.append(command)

        # Send Button Roles
        for guild in client.guilds:
            for channel in guild.text_channels:
                if channel.topic != None:
                    if 'Button Roles' in channel.topic:
                        await channel.purge()
                        pingRoles = [
                            buttonRole(
                                role=roles['@Announcement Ping'],
                                style='gray',
                                emoji='🔔'
                            ),
                            buttonRole(
                                role=roles['@Game Night Ping'],
                                style='gray',
                                emoji='🎮'
                            ),
                            buttonRole(
                                role=roles['@Upload Ping'],
                                style='gray',
                                emoji='🆙'
                            )
                        ]
                        # regionRoles = [
                        #     buttonRole(
                        #         role=roles['@American Eagles'],
                        #         style='Dropdown',
                        #         emoji='🇺🇸'
                        #     ),
                        #     buttonRole(
                        #         role=roles['@Tea Sippers'],
                        #         style='Dropdown',
                        #         emoji='🇬🇧'
                        #     ),
                        #     buttonRole(
                        #         role=roles['@Kangaroos'],
                        #         style='Dropdown',
                        #         emoji='🇦🇺'
                        #     ),
                        #     buttonRole(
                        #         role=roles['@Meatball Kings'],
                        #         style='Dropdown',
                        #         emoji='🇸🇪'
                        #     ),
                        #     buttonRole(
                        #         role=roles['@pain'],
                        #         style='Dropdown',
                        #         emoji='🇪🇸'
                        #     )
                        # ]
                        await sendButtonRoles(pingRoles, channel, 'Click a Button to choose from various *Ping Roles*')
                        # await sendButtonRoles(regionRoles, channel, 'Choose an item from the Dropdown to choose from various *Region Roles*', dropdown=True)
        await tree.sync()

    @client.event
    async def on_member_join(member):
        await memberStatusUpdate(True, member)

    @client.event
    async def on_member_remove(member):
        await memberStatusUpdate(False, member)

    client.run(TOKEN)