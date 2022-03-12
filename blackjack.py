import discord
from discord.ext import commands
import asyncio
import random
import time
import math


class Table:
	def __init__(self, client, channel, user, tableid):
		self.client = client
		self.channel = channel
		self.playerList = [Player(user)]
		self.tableid = tableid
		self.playerQueue = []
		self.playerLeaving = []
		print("Blackjack table {} initialized with player {}".format(tableid, user.name))


	# Adds a player to the table
	async def addPlayer(self, user):
		print("Player {} added to blackjack".format(user.name))
		self.playerQueue.append(Player(user))


	async def addPlayerlist(self):
		self.playerList.extend(self.playerQueue)
		self.playerQueue = []


	# Removes a player from the table
	async def removePlayer(self, player):
		print("Player {} removed from blackjack".format(player.user.name))
		self.playerLeaving.append(player)


	async def removePlayerlist(self):
		for player in self.playerLeaving:
			self.playerList.remove(player)
		self.playerLeaving = []


	# Continuously runs table
	async def runTable(self):
		message = await self.channel.send("```\nBlackjack Table {}\n\n```".format(self.tableid))
		cache_msg = discord.utils.get(self.client.cached_messages, id=message.id)
		deck = Deck()
		layout = Layout(cache_msg, self.playerList, deck)
		while(len(self.playerList) != 0):
			await self.doTurn(layout, deck)
			await self.removePlayerlist()
			await self.addPlayerlist()
		await cache_msg.delete()


	# Does a single turn of blackjack on the table
	async def doTurn(self, layout, deck):
		if len(self.playerList) == 0:
			return
		await deck.shuffleCards()
		await layout.getBets(self.client)
		dealer = Dealer(await layout.dealCards())
		await layout.getPlays(self.client)
		await layout.getDealerPlay(dealer)
		await layout.determineWinners(dealer, self.client)
		await layout.finishTurn()


class Layout:
	def __init__(self, message, playerList, deck):
		self.message = message
		self.playerList = playerList
		self.playerRemoveList = []
		self.deck = deck
		self.headermessage = message.content[:-3]
		self.dealermessage = ''
		self.playermessage = ''
		self.instructionmessage = ''


	async def getBets(self, client):
		self.instructionmessage = 'Place your bets\n1️⃣: 5 Bakacoins\n2️⃣: 10 Bakacoins\n3️⃣: 25 Bakacoins\n4️⃣: 50 Bakacoins'
		await self.updateTable()
		await self.message.add_reaction('1️⃣')
		await self.message.add_reaction('2️⃣')
		await self.message.add_reaction('3️⃣')
		await self.message.add_reaction('4️⃣')
		await self.setBets(client)
		await self.message.clear_reactions()
		self.instructionmessage = 'Bets have been set'
		await self.updateTable()
		for player in self.playerList:
			self.playermessage += '{}\n{}\n\n'.format(player.user.name, player.bet)
		await self.updateTable()


	async def setBets(self, client):
		allBetsPlaced = False
		start_time = time.perf_counter()
		while not allBetsPlaced and time.perf_counter() - start_time < 30:
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
							if not await self.sufficientCoins(player.id, amount, client):
								self.instructionmessage = 'Player {} does not have {} BakaCoins in their wallet, please select another bet amount.'.format(player.user.name, amount)
								await self.updateTable()
								await reaction.remove(player.user)
							else:
								player.bet = amount
								await reaction.remove(player.user)
								print("Player {} has betted {}".format(player.user.name, amount))
		if not allBetsPlaced:
			for player in self.playerList:
				if player.bet == 0:
					self.instructionmessage = 'Player {} did not bet and will be removed from the game.'.format(player.user.name)
					await self.updateTable()
					self.playerList.remove(player)

		for player in self.playerList:
			await self.removeMoney(player.id, player.bet, client)


	async def sufficientCoins(self, id, amount, client):
		if (await client.db.fetch("SELECT count(*) FROM usereconomy WHERE id = $1", id))[0].get("count") != 0:
			walletamount = (await client.db.fetch("SELECT moneyamount FROM usereconomy WHERE id = $1", id))[0].get("moneyamount")
			if walletamount >= amount:
				return True
		return False


	async def removeMoney(self, id, amount, client):
		await client.db.execute("UPDATE usereconomy SET moneyamount = moneyamount - $1 WHERE id = $2", amount, id)
		print("Money of amount {} removed from user id: {}".format(amount, id))


	async def addMoney(self, id, amount, doubledown, client):
		if doubledown:
			amount += amount
		await client.db.execute("UPDATE usereconomy SET moneyamount = moneyamount + $1 WHERE id = $2", amount, id)
		print("Money of amount {} added to user id: {}".format(amount, id))


	async def getPlays(self, client):
		self.instructionmessage = 'Select your play\n🇭: Hit\n🇸: Stand\n🇩: Double Down\n🇵: Split'
		await self.updateTable()
		await self.message.add_reaction('🇭')
		await self.message.add_reaction('🇸')
		await self.message.add_reaction('🇩')
		await self.message.add_reaction('🇵')	
		await self.setPlays(client)
		await self.message.clear_reactions()


	async def setPlays(self, client):
		message = self.message.content[:-19]
		allPlaysFinished = False
		start_time = time.perf_counter()
		while not allPlaysFinished and time.perf_counter() - start_time < 60:
			allPlaysFinished = True
			for player in self.playerList:
				if player.finishedturn == False:
					allPlaysFinished = False
					for reaction in self.message.reactions:
						async for user in reaction.users():
							if player.id == user.id:
								if reaction.emoji == '🇭':
									player.hand.append(await self.deck.dealCard())
									self.instructionmessage = '{} hits and now has a hand total of {}\n🇭: Hit\n🇸: Stand\n🇩: Double Down\n🇵: Split'.format(player.user.name, await player.calculateTotal())
									await self.updatePlayerMessage()
									await self.updateTable()
									player.turnone = False
								elif reaction.emoji == '🇸':
									self.instructionmessage = '{} stands and finishes his hand with a total of {}\n🇭: Hit\n🇸: Stand\n🇩: Double Down\n🇵: Split'.format(player.user.name, await player.calculateTotal())
									await self.updatePlayerMessage()
									await self.updateTable()
									player.finishedturn = True
								elif reaction.emoji == '🇩' and player.turnone == True:
									if not await self.sufficientCoins(player.id, player.bet, client):
										self.instructionmessage = 'Player {} does not have {} BakaCoins in their wallet to double down.'.format(player.user.name, player.bet)
										await self.updateTable()
									else:
										await self.removeMoney(player.id, player.bet, client)
										player.doubledown = True
										player.hand.append(await self.deck.dealCard())
										self.instructionmessage = '{} double downs and finishes his hand with a total of {}\n🇭: Hit\n🇸: Stand\n🇩: Double Down\n🇵: Split'.format(player.user.name, await player.calculateTotal())
										await self.updatePlayerMessage()
										await self.updateTable()
										player.finishedturn = True
								elif reaction.emoji == '🇵' and player.turnone == True and player.hand[0] == player.hand[1]:
									if not await self.sufficientCoins(player.id, player.bet, client):
										self.instructionmessage = 'Player {} does not have {} BakaCoins in their wallet to split.'.format(player.user.name, player.bet)
										await self.updateTable()
									else:
										await self.removeMoney(player.id, player.bet, client)
										player.splithand.append(player.hand.pop(1))
										player.hand.append(await self.deck.dealCard())
										self.instructionmessage = '{} splits and now has a new hand total of {} on his first splitted hand\n🇭: Hit\n🇸: Stand\n🇩: Double Down\n🇵: Split'.format(player.user.name, await player.calculateTotal())
										await self.updatePlayerMessage()
										await self.updateTable()
								if player.finishedturn and player.splithand:
									start_time += 60
									await player.resetSplit()
									player.hand.append(await self.deck.dealCard())
									self.instructionmessage = '{} is now playing his second splitted hand and now has a hand total of {}\n🇭: Hit\n🇸: Stand\n🇩: Double Down\n🇵: Split'.format(player.user.name, await player.calculateTotal())
									await self.updatePlayerMessage()
									await self.updateTable()
								await reaction.remove(player.user)
				else:
					continue
		if not allPlaysFinished:
			for player in self.playerList:
				if player.finishedturn == False:
					self.instructionmessage = 'Player {} failed to complete their turn in time and will finish their hand with a total of {}'.format(player.user.name, await player.calculateTotal())
					await self.updatePlayerMessage()
					await self.updateTable()
				while player.splithand:
					await player.resetSplit()
					player.hand.append(await self.deck.dealCard())
					self.instructionmessage = 'Player {} failed to complete their turn in time and will finish their splitted hand with a total of {}'.format(player.user.name, await player.calculateTotal())
					await self.updatePlayerMessage()
					await self.updateTable()
				player.finishedturn = True


	async def dealCards(self):
		self.instructionmessage = 'Dealing cards...'
		await self.updateTable()
		for player in self.playerList:
			player.hand.append(await self.deck.dealCard())
		dealer = [await self.deck.dealCard()]
		for player in self.playerList:
			player.hand.append(await self.deck.dealCard())
		dealer.append(await self.deck.dealCard())
		self.dealermessage = 'Dealer\n█ {}'.format(dealer[1])
		await self.updatePlayerMessage()
		await self.updateTable()
		return dealer


	async def updatePlayerMessage(self):
		newplayermessage = ''
		for player in self.playerList:
			for card in player.hand:
				newplayermessage += '{} '.format(card)
			newplayermessage += '\n{}\n{}\n\n'.format(player.user.name, player.bet)
		self.playermessage = newplayermessage


	async def getDealerPlay(self, dealer):
		self.dealermessage = 'Dealer\n{} {}'.format(dealer.hand[0], dealer.hand[1])
		await self.updateTable()
		await dealer.calculateTotal()
		while dealer.handtotal < 17:
			dealer.hand.append(await self.deck.dealCard())
			newdealermessage = 'Dealer\n'
			for card in dealer.hand:
				newdealermessage += '{} '.format(card)
			self.dealermessage = newdealermessage
			self.instructionmessage = 'Dealer hits and now has a hand total of {}'.format(await dealer.calculateTotal())
			await self.updateTable()


	async def determineWinners(self, dealer, client):
		for player in self.playerList:
			for outcome in player.splitoutcomes:
				if outcome <= 21:
					if dealer.handtotal > 21 or outcome > dealer.handtotal:
						self.instructionmessage = '{} wins with a hand total of {}!'.format(player.user.name, outcome)
						await self.updateTable()
						if outcome == 21:
							await self.addMoney(player.id, math.ceil(player.bet * 2.5), player.splitdoubledowns.pop(0), client)
						else:
							await self.addMoney(player.id, player.bet * 2, player.splitdoubledowns.pop(0), client)
						continue
					elif outcome == dealer.handtotal:
						self.instructionmessage = '{} ties with a hand total of {}!'.format(player.user.name, outcome)
						await self.updateTable()
						await self.addMoney(player.id, player.bet, player.splitdoubledowns.pop(0), client)
						continue
				self.instructionmessage = '{} loses in his splitted hand with a hand total of {}!'.format(player.user.name, outcome)
				if player.splitdoubledowns.pop(0):
					await self.removeMoney(player.id, player.bet, client)
				await self.updateTable()

			if player.bust == False:
				if dealer.handtotal > 21 or player.handtotal > dealer.handtotal:
					self.instructionmessage = '{} wins with a hand total of {}!'.format(player.user.name, player.handtotal)
					await self.updateTable()
					if player.handtotal == 21:
						await self.addMoney(player.id, math.ceil(player.bet * 2.5), player.doubledown, client)
					else:
						await self.addMoney(player.id, player.bet * 2, player.doubledown, client)
					continue
				elif player.handtotal == dealer.handtotal:
					self.instructionmessage = '{} ties with a hand total of {}!'.format(player.user.name, player.handtotal)
					await self.updateTable()
					await self.addMoney(player.id, player.bet, player.doubledown, client)
					continue
			self.instructionmessage = '{} loses with a hand total of {}!'.format(player.user.name, player.handtotal)
			if player.doubledown:
				await self.removeMoney(player.id, player.bet, client)
			await self.updateTable()


	async def updateTable(self):
		await self.message.edit(content = self.headermessage + self.dealermessage + '\n\n\n' + self.playermessage + '\n\n\n' + self.instructionmessage + '\n\n```')
		time.sleep(2)


	async def finishTurn(self):
		for player in self.playerList:
			await player.resetPlayer()
		self.dealermessage = ''
		self.playermessage = ''
		self.instructionmessage = ''


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
			self.unplayedCards = ['A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A',
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
			random.shuffle(self.unplayedCards)
			self.playedCards = []


	async def dealCard(self):
		card = self.unplayedCards.pop(0)
		self.playedCards.append(card)
		return card


# Player's state in a turn
class Player:
	def __init__(self, user):
		self.user = user
		self.id = user.id
		self.bet = 0
		self.hand = []
		self.handtotal = 0
		self.soft = False
		self.bust = False
		self.finishedturn = False
		self.turnone = True
		self.splithand = []
		self.splitoutcomes = []
		self.doubledown = False
		self.splitdoubledowns = []


	async def setBet(self, amount):
		self.bet = amount


	async def calculateTotal(self):
		self.handtotal = 0
		for card in self.hand:
			if card.isdigit():
				self.handtotal += int(card)
			else:
				if card == 'J' or card == 'Q' or card == 'K':
					self.handtotal += 10
				else:
					self.soft = True
					self.handtotal += 11
			if self.handtotal > 21:
				if self.soft == False:
					self.bust = True
					self.finishedturn = True
				else:
					self.handtotal -= 10
					self.soft = False
					if self.handtotal > 21:
						self.bust = True
						self.finishedturn = True
			elif self.handtotal == 21:
				self.finishedturn = True
		return self.handtotal


	async def resetPlayer(self):
		self.bet = 0
		self.hand = []
		self.handtotal = 0
		self.soft = False
		self.bust = False
		self.finishedturn = False
		self.turnone = True
		self.splithand = []
		self.splitoutcomes = []
		self.doubledown = False
		self.splitdoubledowns = []



	async def resetSplit(self):
		self.hand = [self.splithand.pop()]
		self.soft = False
		self.bust = False
		self.finishedturn = False
		self.turnone = True
		self.splitoutcomes.append(self.handtotal)
		self.handtotal = 0
		self.splitdoubledowns.append(self.doubledown)
		self.doubledown = False


class Dealer:
	def __init__(self, hand):
		self.hand = hand
		self.handtotal = 0
		self.soft = False
		self.bust = False


	async def calculateTotal(self):
		self.handtotal = 0
		for card in self.hand:
			if card.isdigit():
				self.handtotal += int(card)
			else:
				if card == 'J' or card == 'Q' or card == 'K':
					self.handtotal += 10
				else:
					self.soft = True
					self.handtotal += 11
			if self.handtotal > 21:
				if self.soft == False:
					self.bust = True
				else:
					self.handtotal -= 10
					self.soft = False
					if self.handtotal > 21:
						self.bust = True
		return self.handtotal