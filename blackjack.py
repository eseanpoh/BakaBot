import discord
import asyncio


class Table:
	def __init__(self, channel, playerList):
		self.channel = channel
		self.playerList = playerList


	async def addPlayer(id):
		self.playerList.append(id)