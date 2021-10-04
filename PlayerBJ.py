import asyncio
import datetime
import random
import sys
import discord  # Needs to be installed manually
from discord.ext import commands
from discord.ext.commands import Bot

class PlayerBJ:
    def __init__(self, player, cards):
        self.name = player.name
        self.playerRef = player
        self.number = 0
        self.sum = 0
        self.bust = False
        self.passed = False
        self.win = False
        self.cards = cards
        self.cardValue(self.cards, self.number)

    def cardValue(self, cards, num):
        _cards = []
        for i in cards:
            if i[0] in "QJK":
                _cards.append(10)
            elif i[0] == "A":
                _cards.append(11)
            else:
                _cards.append(int(i[0]))
        self.sum = sum(_cards)
        if num == 0:
            if self.sum == 21:
                self.win = True
            else:
                self.win = False
            num += 1
        else:
            if self.sum > 21:
                new = []
                for card in _cards:
                    if card == 11:
                        new.append(1)
                    else:
                        new.append(card)
                if sum(new) > 21:
                    self.bust = True
                else:
                    self.bust = False
                    self.sum = sum(new)
            elif self.sum == 21:
                self.win = True
            else:
                pass
  
    def addCard(self, card):
        self.cards.append(card)
        self.cardValue(self.cards, 1)
        if self.win:
            return True
        elif self.bust:
            return False
        else:
            return self.sum
        