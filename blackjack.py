import discord
import asyncio
import random


class Table:
	def __init__(self, channel, playerID):
		print("Blackjack table initialized")
		self.channel = channel
		self.playerList = [Player(playerID)]

	# Adds a player to the table
	async def addPlayer(self, id):
		self.playerList.append(Player(id))


	# Removes a player from the table
	async def removePlayer(self, id):
		for i, player in enumerate(playerList):
		    if player.id == id:
		        del playerList[i]
		        break

	# Continuously runs table
	async def runTable(self):
		message = await self.channel.send("""```Blackjack\n\nPlace your bets\n\n""" +
											"```")
		layout = Layout(message)
		deck = Deck()
		while(len(self.playerList) != 0):
			self.doTurn()


	# Does a single turn of blackjack on the table
	async def doTurn(self):
		deck.shuffleCards()

		Layout.getBets()





class Layout:
	def __init__(self, message):
		self.message = message
"""
	async def updateLayout(self):



	async def getBets():



	async def dealCards():



	async def 
"""


# 6 Decks, Shuffle at 75%
class Deck:

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
					   'K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K','K',]


	def __init__(self):
		self.unplayedCards = random.shuffle(unshuffledCards)
		self.playedCards = []


	async def shuffleCards(self):
		if len(playedCards) >= 234:
			self.playedCards = []
			self.unplayedCards = random.shuffle(unshuffledCards)


	# async def discardCard():


# Player's state in a turn
class Player:
	def __init__(self, id):
		self.id = id
		self.bet = 0
		self.hand = []

	async def setBet(self, amount):
		self.bet = amount


