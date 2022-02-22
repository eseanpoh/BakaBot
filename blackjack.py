import discord
from discord.ext import commands
import asyncio
import random

class Table:
	def __init__(self, client, channel, user):
		self.client = client
		self.channel = channel
		self.playerList = [Player(user)]
		print("Blackjack table initialized")


	# Adds a player to the table
	async def addPlayer(self, user):
		self.playerList.append(Player(user))


	# Removes a player from the table
	async def removePlayer(self, id):
		for i, player in enumerate(self.playerList):
		    if player.id == id:
		        del self.playerList[i]
		        break

	# Continuously runs table
	async def runTable(self):
		message = await self.channel.send("```\nBlackjack\n\n```")
		cache_msg = discord.utils.get(self.client.cached_messages, id=message.id)
		layout = Layout(cache_msg, self.playerList)
		deck = Deck()
		await self.doTurn(layout, deck)
		'''while(len(self.playerList) != 0):
			await self.doTurn(layout, deck)'''


	# Does a single turn of blackjack on the table
	async def doTurn(self, layout, deck):
		if len(self.playerList) == 0:
			return
		await deck.shuffleCards()
		await layout.getBets()
		# await layout.dealCards()





class Layout:
	def __init__(self, message, playerList):
		self.message = message
		self.playerList = playerList


	async def getBets(self):
		await self.message.edit(content = self.message.content[:-3] + 'Place your bets\n\n```')
		await self.message.add_reaction('1️⃣')
		await self.message.add_reaction('2️⃣')
		await self.message.add_reaction('3️⃣')
		await self.message.add_reaction('4️⃣')
		await self.setBets()
		await self.message.edit(content = self.message.content[:-20] + 'Bets have been set\n\n```')
		for player in self.playerList:
			await self.message.edit(content = self.message.content[:-3] + '{}\n{}\n\n```'.format(player.user.name, player.bet))


	async def hasBets(self):
		for player in self.playerList:
			if player.bet == 0:
				return False
		return True


	async def setBets(self):
		allBetsPlaced = False
		while not allBetsPlaced:
			allBetsPlaced = True
			for player in self.playerList:
				if player.bet == 0:
					allBetsPlaced = False
				else:
					continue
				for reaction in self.message.reactions:
					async for user in reaction.users():
						if reaction.emoji =='1️⃣':
							amount = 5
						elif reaction.emoji == '2️⃣':
							amount = 10
						elif reaction.emoji == '3️⃣':
							amount = 25
						elif reaction.emoji == '4️⃣':
							amount = 50
						else:
							amount = 0
						if player.id == user.id:
							player.bet = amount
							print("player {} has betted {}".format(player.id, amount))


	async def dealCards(self):
		await self.message.edit(content = self.message.content[:-23] + 'Dealing cards...\n\n```')




	# async def 



# 6 Decks, Shuffle at 75%
class Deck:
	def __init__(self):
		unshuffledCards = ['A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A',
						   '2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2',
						   '3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3',
						   '4','4','4','4','4','4','4','4','4','4','4','4','4','4','4','4','4','4','4','4','4','4','4','4',
						   '5','5','5','5','5','5','5','5','5','5','5','5','5','5','5','5','5','5','5','5','5','5','5','5',
						   '6','6','6','6','6','6','6','6','6','6','6','6','6','6','6','6','6','6','6','6','6','6','6','6',
						   '7','7','7','7','7','7','7','7','7','7','7','7','7','7','7','7','7','7','7','7','7','7','7','7',
						   '8','8','8','8','8','8','8','8','8','8','8','8','8','8','8','8','8','8','8','8','8','8','8','8',
						   '9','9','9','9','9','9','9','9','9','9','9','9','9','9','9','9','9','9','9','9','9','9','9','9',
						   '10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10','10',
						   'J','J','J','J','J','J','J','J','J','J','J','J','J','J','J','J','J','J','J','J','J','J','J','J',
						   'Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q','Q',
						   'K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K']
		self.unplayedCards = unshuffledCards
		random.shuffle(self.unplayedCards)
		self.playedCards = []


	async def shuffleCards(self):
		print("No shuffle needed")
		if len(self.playedCards) >= 234:
			print("Shuffle needed")
			self.unplayedCards = unshuffledCards
			random.shuffle(self.unplayedCards)
			self.playedCards = []


	# async def discardCard():


# Player's state in a turn
class Player:
	def __init__(self, user):
		self.user = user
		self.id = user.id
		self.bet = 0
		self.hand = []


	async def setBet(self, amount):
		self.bet = amount