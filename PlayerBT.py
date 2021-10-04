import asyncio
import datetime
import random
import sys
import discord  # Needs to be installed manually
from discord.ext import commands
from discord.ext.commands import Bot
import bigTwo as bt

class PlayerBT:

    def __init__(self, player, cards):
        self.name = player.name
        self.playerRef = player
        self.passed = False
        self.win = False
        self.cards = cards
        self.score = 0
    
    def played(self, cards):
        for card in cards:
            self.cards.remove(card)
    
    def newRound(self):
        self.passed = False
        self.win = False
        self.cards = []

    def addCard(self, card):
        self.cards.append(card)
        self.cards.sort(key=bt.get_card_score)
    
