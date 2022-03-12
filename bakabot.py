# bakabot.py
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import random
import asyncio
import asyncpg
import uwuify
import blackjack as blackjackInitiate


# Set to True to use the test bot, False to use the real bot
test_env = True 

bot_token = ""
if test_env:
	bot_token = "OTM4ODA0MTgyMzA2MTU2NTc1.Yfvnhw.T9ghDZe0gZe57Mo6--G-Vadv3M8"
	bot_channel_id = 938410969221202021
else:
	bot_token = "ODkwNTIzODk5NzQ4NTgxMzk3.YUxDAg.DXg9TPad2LjJUjcHzq5-8gPgQRQ"


# Connect client to database
async def create_db_pool():
	client.db = await asyncpg.create_pool(dsn='postgres://bakaadmin:bakarissa@42.191.241.188:5432/bakabot')
	print('BakaBot has connected to the BakaBot database!')

# Create client with intents to be able to check members of a guild
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!baka ', case_insensitive=True, intents=intents, help_command=None)


# When bot is ready
@client.event
async def on_ready():
	# im sorry carissa
	# :)
	print('I-it\'s not like I l-like you or anything... B-{0.user}!'.format(client))


# Triggers on each command message
@client.event
async def on_message(msg):
	# Ensures the bot doesn't respond to its own message
	if msg.author == client.user:
		return

	channel = msg.channel

	if test_env and channel.id != bot_channel_id:
		return
	elif not test_env and channel.id == 938410969221202021:
		return

	message = msg.content.lower()
	if message == "baka" or message == "!baka" or message == "baka!":
		await channel.send("means stupid!")
		return

	await client.process_commands(msg)


# When an invalid command is entered
@client.event
async def on_command_error(ctx, error):
	if isinstance(error, CommandNotFound):
		# Removes the "!baka " part of the original message
		message = ctx.message.content[6:]
		await ctx.send('You sussy baka! There is no "' + message + '" command!')


# Coin flip function
@client.command()
async def coinFlip(ctx):
	print("Coinflip by " + ctx.author.name + " in " + ctx.guild.name)
	if random.choice([0, 1]) == 0:
		await ctx.send('Heads!')
	else:
		await ctx.send('Tails!')


# Hmph command
@client.command(aliases=["hmph!"])
async def hmph(ctx):
	print("Hmph by " + ctx.author.name + " in " + ctx.guild.name)
	await ctx.send("I-it's not like I l-like you or anything, b-baka!")


# Bogdanoff command
@client.command()
async def he(ctx, argument: str = "n/a"):
	print("He bought/sold? by " + ctx.author.name + " in " + ctx.guild.name)
	argument = argument.lower()
	# Embeds image and sends it
	if argument == "bought?" or argument == "bought":
		dumpit = discord.Embed()
		dumpit.set_image(url="https://cdn.discordapp.com/attachments/251353278389026816/935197301645918218/aPZjBwn_460s.png")
		await ctx.send(embed=dumpit)
	elif argument == "sold?" or argument == "sold":  # TODO: This currently does the exact same thing as bought, someone please create a new image and change the image url - Carissa
		dumpit = discord.Embed()
		dumpit.set_image(url="https://cdn.discordapp.com/attachments/251353278389026816/935197301645918218/aPZjBwn_460s.png")
		await ctx.send(embed=dumpit)
	else:  # If no argument is provided or argument is invalid
		await ctx.send("He what?")


# Timer function to asynchronously parse the time given, and countdown, then returns to the message
@client.command()
async def timer(ctx, *, message: str = None):
	print("Timer by " + ctx.author.name + " in " + ctx.guild.name)
	# Checks if the arguments are empty
	if message is None:
		await ctx.send("Idiot! You forgot to add the time! You can do it like this: !baka timer [hr]:[min]:[sec] [message]")
		return

	# Splits message into list and gets the time argument
	message = message.split(" ")
	time_list = message[0].split(":")
	message.pop(0)

	# Checks for correct formatting
	if len(time_list) != 3:
		await ctx.send("Idiot, if you can't even enter a correct time, it's time to get a watch! Use [hr]:[min]:[sec]")
		return
	elif not all(i.isdigit() for i in time_list):
		await ctx.send("Hey, if you think a clock can be made out of alphabets or symbols, you might want to go back to elementary school. Use [hr]:[min]:[sec]!")
		return

	# Converts inputted time to number of seconds
	seconds = (int(time_list[0]) * 3600) + (int(time_list[1]) * 60) + int(time_list[2])
	# Waits for the time specified
	await asyncio.sleep(seconds)

	# I reworked this part to be more straightforward instead of using loops and excess concatenations - Carissa
	if len(message) == 0:
		# Default timer message if no message is provided
		await ctx.send("Timer Alert: Your time is up dumbass! Hahahaha!")
	else:
		# Joins every word in the list together with a space
		message = ' '.join(message)
		message = 'Timer Alert: ' + message
		await ctx.send(message)


# Function for uploading Hope pictures
@client.command()
async def hope(ctx, argument: str = None):
	print("Hope by " + ctx.author.name + " in " + ctx.guild.name)
	# Fetches the total number of Hope pics from the database
	count = (await client.db.fetch("SELECT count(*) FROM hopepics"))[0].get("count")

	if argument is None:
		# If nothing else is specified, get random hope pic
		id = random.randint(0, count-1)
		await ctx.send((await client.db.fetch("SELECT url FROM hopepics WHERE id = $1", id))[0].get("url"))
		return

	argument = argument.lower()

	# If block for all arguments
	if argument == "count":  # Sends the total number of Hope pictures
		await ctx.send('The idiot has uploaded {} Hope pictures.'.format(count))

	elif argument == "upload":  # For uploading Hope photos
		# Prevents anyone other than Carissa from being able upload photos
		if ctx.message.author.id != 259841976696832030:
			await ctx.send("Wait a minute you're not Carissa, why are you trying to upload Hope pics?")
			return

		# Get attachments linked to message
		attachments = ctx.message.attachments

		# Checks if no attachments are in message
		if not attachments:
			await ctx.send("Either you're blind, or you've just uploaded Schrodinger's cat!")
			return

		# Uploads each photo attached to message and increases count for each one
		for picture in attachments:
			link = picture.url
			await client.db.execute("INSERT INTO hopepics (id, url) VALUES ($1, $2)", count, link)
			print("Picture uploaded with ID: {} and Link: {}".format(count, link))
			count += 1
		await ctx.send("Hey dummy Hope simp, all pictures have been uploaded.")

	elif argument.isdigit():  # If the user wants a specific Hope picture
		id = int(argument)

		# If the photo is out of range, get a random one instead
		if id < 0 or id >= count:
			id = random.randint(0, count-1)

		await ctx.send((await client.db.fetch("SELECT url FROM hopepics WHERE id = $1", id))[0].get("url"))

	else:  # If the argument doesn't match anything else
		await ctx.send("This idiot can't type numbers hahaha! Use !baka hope [number] to get a specific picture.")


# Cursed command to uwuify a sentence
@client.command(aliases=["owo", "uwuify", "uwufy"])
async def uwu(ctx, *, message: str = None):
	print("Uwu by " + ctx.author.name + " in " + ctx.guild.name)
	# If no sentence is provided
	if message is None:
		await ctx.send("OwO")
		return
	flags = uwuify.SMILEY
	await ctx.send(uwuify.uwu(message, flags = flags))
	return


blackjackTables = []


# Blackjack
@client.command()
async def blackjack(ctx, argument: str = None):
	print("Blackjack join/leave by " + ctx.author.name + " in " + ctx.guild.name)
	# If no arguments are provided
	if argument is None:
		await ctx.send("Hey doofus, you need another command in '!baka blackjack [join/leave]'.")
		return
	argument = argument.lower()
	if argument == 'join':
		if await checkActivePlayer(ctx.message.author.id):
			await ctx.send("You're already in a game, smooth brain.")
			return
		await addBlackjack(ctx, ctx.message.author, ctx.channel)

	elif argument == 'leave':
		if not await checkActivePlayer(ctx.message.author.id):
			await ctx.send("You're not in a game, smooth brain.")
			return
		await ctx.send(await removeBlackjack(ctx.message.author, ctx.channel))
	else:
		await ctx.send("Dimwit, the command is '!baka blackjack [join/leave]'.")
		return


async def addBlackjack(ctx, user, channel):
	for table in blackjackTables:
		if len(table.playerList) + len(table.playerQueue) - len(table.playerLeaving) == 0:
			blackjackTables.remove(table)
			continue
		if table.channel == channel:
			if len(table.playerList) + len(table.playerQueue) - len(table.playerLeaving) < 4:
				await ctx.send("Added to Blackjack table {}, please wait for the current turn to end to begin playing.".format(table.tableid))
				await table.addPlayer(user)
				return
	tableid = await generateBlackjackID()
	await ctx.send("Added to Blackjack table {}".format(tableid))
	blackjackTables.append(blackjackInitiate.Table(client, channel, user, tableid))
	await blackjackTables[-1].runTable()
	return


async def removeBlackjack(user, channel):
	for table in blackjackTables:
		if table.channel == channel:
			for player in table.playerList:
				if player.id == user.id:
					tableid = table.tableid
					await table.removePlayer(player)
					removemessage = "Removed from Blackjack table {}, please finish your current turn to leave.".format(tableid)
	for table in blackjackTables:
		if len(table.playerList) + len(table.playerQueue) - len(table.playerLeaving) == 0:
			blackjackTables.remove(table)
	return removemessage


async def checkActivePlayer(userid):
	for table in blackjackTables:
		for player in table.playerList:
			if player.id == userid:
				return True
	return False


async def generateBlackjackID():
	existingIDs = []
	for table in blackjackTables:
		existingIDs.append(table.tableid)
	num = 1
	while num in existingIDs:
		num += 1
	return num


# Command that handles coins
@client.command(aliases=["bakacoin", "coins"])
async def coin(ctx, *arguments):
	print("Coin by " + ctx.author.name + " in " + ctx.guild.name)
	# If no arguments are provided
	if not arguments:
		await ctx.send("Coin? Coin what? Use !baka coin [initiate/amount/pay/leaderboard].")
		return

	argument = arguments[0].lower()
	id = ctx.message.author.id

	# For initiating a new account
	if argument == "initiate":
		if not await checkUserMoneyExists(id):
			await ctx.send(await initiateWallet(id, 100))
		else:
			await ctx.send("This idiot is trying to get more free money. Hahahahahaha!")
	elif argument == "amount" or argument == "wallet" or argument == "balance":  # For checking balance
		await ctx.send(embed = await checkMoney(ctx.message.author))
	elif argument == "pay":  # For giving coins to others
		await ctx.send(await transferMoney(id, arguments))
	elif argument == "leaderboard":
		await ctx.send(await richestUsers())
	else:  # If the argument is not valid
		await ctx.send("Coin? Coin what? Use !baka coin [initiate/balance].")


# Transfers money from one user to another
async def transferMoney(id, arguments):
	if not await checkUserMoneyExists(id):
		return "You have not initiated your wallet. Go get your free coins."

	if len(arguments) == 3:
		if arguments[1].isdigit():
			amount = int(arguments[1])
			if amount > 0:
				if await checkEnoughMoney(id, transfer_amount=amount):
					mention = arguments[2]
					to_id = parseUserIdFromMention(mention)

					if not to_id:
						return "Mention the person you want to pay."
					elif to_id == int(id):
						return "You can't pay yourself."
					elif not await checkUserMoneyExists(to_id):
						return "The user has not initiated their wallet."
					else:
						return await giveMoney(give_id=id, receive_id=to_id, amount=amount)
				else:
					return "You don't have enough money, smh broke bitches."
			else:
				return "You can't pay someone nothing."
		else:
			return "Put in a real amount, dummy!"
	else:
		return "Use !baka coin pay [amount] [mention]."


# Checks whether or not the user has initiated their coin wallet
async def checkUserMoneyExists(id):
	count = (await client.db.fetch("SELECT count(*) FROM usereconomy WHERE id = $1", id))[0].get("count")
	if count != 0:
		return True
	return False


# Initiates user wallet
async def initiateWallet(id, amount):
	await client.db.execute("INSERT INTO usereconomy (id, moneyamount) VALUES ($1, $2)", id, amount)
	print("Money of amount {} added to user id: {}".format(amount, id))

	return "Your wallet has been initiated. You have received {} BakaCoins.".format(amount)


# Adds money to a user's wallet
async def addMoney(id, amount):
	await client.db.execute("UPDATE usereconomy SET moneyamount = moneyamount + $1 WHERE id = $2", amount, id)
	print("Money of amount {} added to user id: {}".format(amount, id))

	return "You've been paid {} BakaCoins.".format(amount)


async def removeMoney(id, amount):
	await client.db.execute("UPDATE usereconomy SET moneyamount = moneyamount - $1 WHERE id = $2", amount, id)
	print("Money of amount {} removed from user id: {}".format(amount, id))

	return "You have paid {} BakaCoins.".format(amount)


# Transfers money to a user's wallet
async def giveMoney(give_id, receive_id, amount):
	await removeMoney(give_id, amount)
	await addMoney(receive_id, amount)

	return f"You have paid <@{receive_id}> {amount} BakaCoins."


"""# Tells the user how many coins they have in their wallet
async def checkMoney(id):
	# If wallet has not been initiated yet
	if not await checkUserMoneyExists(id):
		return "You have not initiated your wallet. Go get your free coins."

	# Fetches coin amount from database
	amount = (await client.db.fetch("SELECT moneyamount FROM usereconomy WHERE id = $1", id))[0].get("moneyamount")
	if amount == 1:
		return "You have 1 BakaCoin remaining. Better make it count loser, hahahaha."

	return "You have {} BakaCoins in your wallet.".format(amount)"""


# Tells the user how many coins they have in their wallet
async def checkMoney(user):
	# If wallet has not been initiated yet
	if not await checkUserMoneyExists(user.id):
		embed = discord.Embed(
			title = "{}'s Wallet".format(user.name),
			description = "You have not initiated your wallet. Go get your free coins.",
			colour = user.colour
			)
		embed.set_thumbnail(url = user.avatar_url)
		embed.set_author(name = "BakaCoin", icon_url = client.user.avatar_url)
		return embed

	# Fetches coin amount from database
	amount = (await client.db.fetch("SELECT moneyamount FROM usereconomy WHERE id = $1", user.id))[0].get("moneyamount")
	if amount == 1:
		embed = discord.Embed(
			title = "{}'s Wallet".format(user.name),
			description = "You have not initiated your wallet. Go get your free coins.",
			colour = user.colour
			)
		embed.set_thumbnail(url = user.avatar_url)
		embed.set_author(name = "BakaCoin", icon_url = client.user.avatar_url)
		return embed
	embed = discord.Embed(
		title = "{} BakaCoins",
		description = "Better make them count loser!",
		colour = user.colour
		)
	embed.set_thumbnail(url = user.avatar_url)
	embed.set_author(name = "{}'s Wallet".format(user.name), icon_url = user.avatar_url)
	return embed


# Checks if user has enough coins in wallet
async def checkEnoughMoney(id, transfer_amount):
	# Fetches coin amount from database
	amount = (await client.db.fetch("SELECT moneyamount FROM usereconomy WHERE id = $1", id))[0].get("moneyamount")
	if amount >= transfer_amount:
		return True
	else:
		return False


# Parse user id from Mention format
def parseUserIdFromMention(mention: str = ""):
	if not mention:
		return False

	if mention.startswith('<@') and mention.endswith('>'):
		user_id = mention[1:][:len(mention)-2].replace("@", "").replace("!", "")
		if user_id.isdigit():
			return int(user_id)
		else:
			return False
	else:
		return False


async def richestUsers():
	msg = '```'
	richlist = await client.db.fetch("SELECT * FROM usereconomy ORDER BY moneyamount DESC")
	for account in richlist:
		msg += str(await client.fetch_user(account.get("id"))) + '    ' + str(account.get("moneyamount")) + '\n'
	return msg + '```'


# Function to get the role object given the name of the role
def getRole(reaction, guild):
	if reaction == 'OW':
		role = "Overwatch"
	elif reaction == 'Apex':
		role = "Apex Legends"
	elif reaction == 'MonHun':
		role = "Monster Hunter"
	elif reaction == "Minecraft":
		role = "Minecraft"
	else:
		return None
	return discord.utils.get(guild.roles, name=role)


# When bot gets a reaction
@client.event
async def on_raw_reaction_add(payload):
	message_id = payload.message_id
	# If reaction is from a specified message
	if message_id == 934046929824923680:
		# Get server object
		guild = client.get_guild(payload.guild_id)

		# Select the correct role for the reaction
		role = getRole(payload.emoji.name, guild)

		# If role exists
		if role is not None:
			# Get the member object of the user who reacted
			member = guild.get_member(payload.user_id)

			# If the user exists
			if member is not None:
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
	if message_id == 934046929824923680:
		# Get server object
		guild = client.get_guild(payload.guild_id)

		# Select the correct role for the un-reaction
		role = getRole(payload.emoji.name, guild)

		# If role exists
		if role is not None:
			# Get the user id of the user who un-reacted
			member = guild.get_member(payload.user_id)

			# If the user exists
			if member is not None:
				# Remove role from the user
				await member.remove_roles(role)
				print("{} role removed for user {}".format(role, member))
			else:
				print('User not found')
		else:
			print('Role not found')


# Run database continuously
client.loop.run_until_complete(create_db_pool())


# Grabs the bot's unique token and runs it, do not leak this token or we are fucked
client.run(bot_token)
