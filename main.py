#main.py
import discord
from discord.ext import commands
import random
import asyncio
import asyncpg
import os

# Connect client to database
async def create_db_pool():
	client.db = await asyncpg.create_pool(dsn='postgres://bakaadmin:bakarissa@localhost:5432/bakabot')
	print("Bakabot is connected to the bakabot database!")


# Coin flip function
def coinFlip():
	if random.randint(0,1) == 0:
		return "Heads!"
	else:
		return "Tails!"

# Timer function to asynchronously parse the time given, and countdown, then returns to the message
async def timer(time_str, message = None):
	time_list = time_str.split(':')
	if (len(time_list) != 3):
		return "Idiot, if you can't even enter a correct time, it's time to get a watch!"
	elif not all(i.isdigit() for i in time_list):
		return "Hey, if you think a clock can be made out of alphabets or symbols, you might want to go back to elementary school."
	seconds = (int(time_list[0]) * 3600) + (int(time_list[1]) * 60) + int(time_list[2])
	await asyncio.sleep(seconds)
	if message is not None:
		completemessage = 'Timer Alert: '
		for i in message:
			completemessage = completemessage + i + ' '
		return completemessage
	else:
		return "Timer Alert: Your time is up dumbass! Hahahaha!"

# Function to get the role object given the name of the role
def getRole(reaction, guild):
	if (reaction == 'OW'):
		role = discord.utils.get(guild.roles, name='Overwatch')
	elif (reaction =='Apex'):
		role = discord.utils.get(guild.roles, name='Apex Legends')
	elif (reaction == 'MonHun'):
		role = discord.utils.get(guild.roles, name='Monster Hunter')
	return role

async def uploadHope(attachments):
	count = (await client.db.fetch("SELECT count(*) FROM hopepics"))[0].get("count")
	for picture in attachments:
		link = picture.url
		await client.db.execute("INSERT INTO hopepics (id, url) VALUES ($1, $2)", count, link)
		print("Picture uploaded with ID: {} and Link: {}".format(count, link))
		count += 1
	return "Hey dummy Hope simp, all pictures have been uploaded."

async def getHope(id = -1):
	count = (await client.db.fetch("SELECT count(*) FROM hopepics"))[0].get("count")
	if id >= 0 and id < count:
		return (await client.db.fetch("SELECT url FROM hopepics WHERE id = $1", id))[0].get("url")
	id = random.randint(0, count-1)
	return (await client.db.fetch("SELECT url FROM hopepics WHERE id = $1", id))[0].get("url")

async def HopeCount():
	count = (await client.db.fetch("SELECT count(*) FROM hopepics"))[0].get("count")
	return ('The idiot has uploaded {} Hope pictures.'.format(count))



# Create client
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '!baka', intents = intents)

# When bot is ready
@client.event
async def on_ready():
	# im sorry carissa
	# :)
	print('I-it\'s not like I l-like you or anything... B-{0.user}!'.format(client))

# When bot reads a message
@client.event
async def on_message(message):
	# If message is from the bot, return
	if message.author == client.user:
		return

	# If message is a command starting with '!baka'
	if message.content.startswith('!baka'):
		command = message.content.lower().split(' ')
		
		# If command has no arguments
		if len(command) < 2:
			await message.channel.send('means stupid!')

		# If command has 1 or more arguments
		else:
			
			if command[1] == 'coinflip':
				await message.channel.send(coinFlip())

			elif command[1] == 'hmph!':
				await message.channel.send('I-it\'s not like I l-like you or anything, b-baka!')

			elif command[1] == 'timer':
				if len(command) < 3:
					await message.channel.send('Idiot! You forgot to add the time! You can do it like this: !baka timer [hr]:[min]:[sec] [message]')
				else:
					if (len(command) < 4):
						await message.channel.send(await timer(command[2]))
					else:
						await message.channel.send(await timer(command[2], command[3:]))

			elif command[1] == 'he':
				if command[2] == 'bought?' or command[2] == 'sold?':
					dumpit = discord.Embed()
					dumpit.set_image(url="https://cdn.discordapp.com/attachments/251353278389026816/935197301645918218/aPZjBwn_460s.png")
					await message.channel.send(embed=dumpit)
				else:
					await message.channel.send('He what?')

			elif command[1] == 'hope':
				if len(command) == 3 and command[2] == 'upload':
					if message.author.id == 259841976696832030:
						if message.attachments:
							await message.channel.send(await uploadHope(message.attachments))
						else:
							await message.channel.send('Either you\'re blind, or you\'ve just uploaded Schrodinger\'s cat.')
					else:
						await message.channel.send('Wait a minute you\'re not Carissa, why are you trying to upload Hope pics?')
				elif len(command) == 3 and command[2] == 'count':
					await message.channel.send(await HopeCount())
				else:
					if len(command) == 3 and not command[2].isdigit() and command[2] != 'upload':
						await message.channel.send('This idiot can\'t type numbers hahaha!')
					elif len(command) == 3:
						await message.channel.send(await getHope(int(command[2])))
					else:
						await message.channel.send(await getHope())

			else:
				nocommand = 'You sussy baka! There is no'
				first = True
				for i in command[1:]:
					if first:
						nocommand += ' \''
						first = False
					else:
						nocommand += ' '
					nocommand += i
				nocommand += '\' command!'
				await message.channel.send(nocommand)

# When bot gets a reaction
@client.event
async def on_raw_reaction_add(payload):
	message_id = payload.message_id
	# If reaction is from a specified message
	if (message_id == 934046929824923680):
		# Get server object
		guild = client.get_guild(payload.guild_id)

		# Select the correct role for the reaction
		role = getRole(payload.emoji.name, guild);

		# If role exists
		if (role != None):
			# Get the member object of the user who reacted
			member = guild.get_member(payload.user_id)

			# If the user exists
			if (member != None):
				# Add role to the user
				await member.add_roles(role)
				print("{} role added for user {}".format(role, member))
			else:
				print('User not found')
		else:
			print('Role not found')

# When bot gets an un-reaction
@client.event
async def on_raw_reaction_remove(payload):
	message_id = payload.message_id
	# If un-reaction is from a certain message
	if (message_id == 934046929824923680):
		# Get server object
		guild = client.get_guild(payload.guild_id)

		# Select the correct role for the un-reaction
		role = getRole(payload.emoji.name, guild);

		# If role exists
		if (role != None):
			# Get the user id of the user who un-reacted
			member = guild.get_member(payload.user_id)

			# If the user exists
			if (member != None):
				# Remove role from the user
				await member.remove_roles(role)
				print("{} role removed for user {}".format(role, member))
			else:
				print('User not found')
		else:
			print('Role not found')

# Run database continuously
client.loop.run_until_complete(create_db_pool())

# Grabs bot's unique token and runs it, do not leak this token or we are fucked
client.run('ODkwNTIzODk5NzQ4NTgxMzk3.YUxDAg.DXg9TPad2LjJUjcHzq5-8gPgQRQ')