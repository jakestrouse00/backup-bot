import discord
from discord.ext import commands
import random
import pickle
import os

bot = commands.Bot(command_prefix='-')
bot.remove_command('help')


@bot.event
async def on_ready():
    game = discord.Activity(name="for backups", type=3)
    await bot.change_presence(status=None, activity=game)
    print(f"Bot in {len(bot.guilds)} servers")




@bot.event
async def on_guild_join(guild):
    print(f"\nBot joined {guild.name} | {guild.id}\n")


@bot.event
async def on_message(message):
    if message.content.startswith('-backup'):
        serverRoles = message.guild.roles
        roles = []
        for role in serverRoles:
            if role.name != '@everyone':
                roles.append({'name': role.name, 'perms': role.permissions, 'color': role.color, 'hoist': role.hoist, 'mentionable': role.mentionable})
        catagorys = message.guild.by_category()
        holding = []
        for catagory in catagorys:
            p = 0
            hold = []
            for channel in catagory[1]:
                hold.append({'id': channel.id, 'name': channel.name, 'type': str(channel.type)})
            try:
                holding.append({'id': catagory[0].id, 'name': catagory[0].name, 'channels': hold})
            except:
                holding.append({'id': None, 'name': None, 'channels': hold, 'roles': roles})
        b = {'categories': holding, 'roles': roles}
        key = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-', k=9))
        with open('backups/'+key + '.txt', 'wb') as fp:
            pickle.dump(b, fp)

        await message.channel.send(f'Backup code: {key}')
    elif message.content.startswith('-load'):

        await message.channel.send(
            '```Please send the backup code```')

        def check(m):
            # change if bot account changes from testapp
            if m.author.id != 641406576942514178:
                if m.author.id == message.author.id:
                    if m.channel == message.channel:
                        return 1

        try:
            msg = await bot.wait_for('message', check=check, timeout=60)
        except:
            await message.channel.send(
                f"<@{message.author.id}> ```Load timed out!```")
            return None
        backups = os.listdir('backups')
        if msg.content+'.txt' not in backups:
            await message.channel.send('```Invalid backup code!```')
            return None
        with open('backups/'+msg.content + '.txt', 'rb') as fp:
            backupLoad = pickle.load(fp)
        for category in backupLoad['categories']:
            if category['id'] is not None:
                j = await message.guild.create_category(name=category['name'])
            else:
                j = None
            for channel in category['channels']:
                if channel['type'] == 'text':
                    await message.guild.create_text_channel(name=channel['name'], category=j)
                elif channel['type'] == 'voice':
                    await message.guild.create_voice_channel(name=channel['name'], category=j)
                else:
                    await message.guild.create_text_channel(name=channel['name'], category=j)
        for role in reversed(backupLoad['roles']):
            await message.guild.create_role(name=role['name'], permissions=role['perms'], colour=role['color'], hoist=role['hoist'], mentionable=role['mentionable'])
        channels = message.guild.text_channels
        for i in channels:
            if i.name == 'temp':
                await i.delete()
        await message.author.send('Server load complete!')
    elif message.content.startswith('-wipe'):
        catagorys = message.guild.by_category()
        for catagory in catagorys:
            for channel in catagory[1]:
                await channel.delete()
            try:
                await catagory[0].delete()
            except:
                pass
        roles = message.guild.roles
        for role in roles:
            try:
                await role.delete()
            except:
                pass
        await message.guild.create_text_channel(name="temp")
        await message.author.send('Server wipe complete!')

bot.run('YOUR_BOT_TOKEN')
