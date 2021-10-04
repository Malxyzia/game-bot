# Game Bot by Hayton Lam (SuperNovae#6180)

import asyncio
import datetime
import random
import sys
import discord  # Needs to be installed manually
from discord.ext import commands
from discord.ext.commands import Bot
from PlayerBJ import PlayerBJ
from PlayerBT import PlayerBT
import bigTwo as bt
import json


room_status = {1 : False, 2 : False, 3 : False, 4 : False, 5 : False}
rooms = {}

_party = []
playerPoints = {}
confirm = False
users = {}




class Party:
    def __init__(self, member, name):
        self.owner = member
        self.members = [member]
        self.name = name.title()
        self.possibleCards = []
        self.players = []
        self.wagers = {}
        self.roundCount = 0
        self.gameID = None
        self.cardToBeat = None
        self.cardToBeatPlayerRef = None
        self.startTrick = True
        self.roomNum = None
        self.room = None
        self.winner = []
        self.friendly = False
        self.startRound = True
        self.ctx = None
    
    async def createMessage(self, ctx):
        self.ctx = ctx
        embed = discord.Embed(title="Party Lobby: {}".format(self.name.title()), color=discord.Color.from_rgb(255, 0, 0),
        description='Currently there are {}/4 people in the party.'.format(len(self.members)))
        embed.add_field(name="Members:", value='\n'.join(i.name for i in self.members)) 
        return await ctx.send(embed=embed)

    async def addMember(self, ctx, user):
        self.members.append(user)
        if len(self.members) == 4:
            colour = discord.Colour.from_rgb(0, 255, 0)
        else:
            colour = discord.Colour.from_rgb(255, 0, 0)
        embed = discord.Embed(title="Party Lobby: {}".format(self.name.title()), color=colour,
        description='Currently there are {}/4 people in the party.'.format(len(self.members)))
        embed.add_field(name="Members:", value='\n'.join(i.name for i in self.members))
        logs = await ctx.channel.history(limit=20).flatten()
        for msg in logs:
            if msg.author.name == "GameBot":
                await msg.edit(embed=embed)
                break
        count = 1
        mgs = []
        log = await ctx.channel.history(limit=count).flatten()
        for x in log:
            mgs.append(x)
        await ctx.channel.delete_messages(mgs)
        return
    
    async def removeMember(self, ctx, user):
        self.members.remove(user)
        embed = discord.Embed(title="Party Lobby: {}".format(self.name.title()), color=discord.Colour.from_rgb(66, 244, 78),
        description='Currently there are {}/4 people in the party.'.format(len(self.members)))
        embed.add_field(name="Members:", value='\n'.join(i.name for i in self.members))
        logs = await ctx.channel.history(limit=20).flatten()
        for msg in logs:
            if msg.author.name == "GameBot":
                await msg.edit(embed=embed)
                break
        count = 1
        mgs = []
        log = await ctx.channel.history(limit=count).flatten()
        for x in log:
            mgs.append(x)
        await ctx.channel.delete_messages(mgs)
        await ctx.send(f"You have successfully left the party {self.name}.")

    async def blackJack(self):
        self.gameID = 'bj'
        RANK_ORDER = '234567890JQKA'
        SUIT_ORDER = 'DCHS'
        for i in range(3):
            for i in RANK_ORDER:
                for suits1 in SUIT_ORDER:
                    self.possibleCards.append(i+suits1)
        for i in range(20):
            random.shuffle(self.possibleCards)
            random.shuffle(self.members)
        for i in self.members:
            self.players.append(PlayerBJ(i, []))
        self.index = 0
        self.playerTurn = self.players[self.index]
        for i in range(2):
            for mem in self.players:
                if i == 0:  
                    mem.cards.append(self.possibleCards[-1])
                    self.possibleCards.pop()                                                            
                    await mem.playerRef.send("{} is your hidden card. Don't show anyone else.".format(mem.cards))
                else:
                    card = await self.drawCard()
                    mem.addCard(card)
        await self.channel.send("It's {}'s turn".format(self.playerTurn.name))
        await self.channel.send("Their current hand is: ?, {}\nHit or pass?".format(self.playerTurn.cards[1:]))

    async def updatePlayerTurn(self):
        self.index += 1
        if self.index == 4:
            self.index = 0
        self.playerTurn = self.players[self.index]
        await self.channel.send("It's {}'s turn".format(self.playerTurn.name))
        if self.gameID == "bj":
            if self.playerTurn.passed:
                await self.channel.send(f"Unfortunately {self.playerTurn.name} has already passed with a score of {self.playerTurn.sum}.")
                await self.updatePlayerTurn()
                return
            elif self.playerTurn.bust:
                await self.channel.send(f"{turn.name} has already busted. NEXT!")
                await self.updatePlayerTurn()
                return
            await self.channel.send("Their current hand is: ?, {}\nHit or pass?".format(self.playerTurn.cards[1:]))
        else:
            if self.playerTurn.passed:
                await self.channel.send(f"{self.playerTurn.name} has already passed. NEXT!")
                await self.interim(None)
                return
            if len(self.cardToBeat) > 1:
                await self.channel.send(f"The current cards to beat are {', '.join(self.cardToBeat)}.")
                await self.playerTurn.playerRef.send(f"Your hand is as follows: {', '.join(self.playerTurn.cards)}")
            elif len(self.cardToBeat) == 0:
                await self.channel.send("And they're starting the trick!")
                await self.playerTurn.playerRef.send(f"Your hand is as follows: {', '.join(self.playerTurn.cards)}")
            else:
                await self.channel.send(f"The current card to beat is {', '.join(self.cardToBeat)}.")
                await self.playerTurn.playerRef.send(f"Your hand is as follows: {', '.join(self.playerTurn.cards)}")
                
    async def drawCard(self):
        card = self.possibleCards.pop()
        return card

    async def initiateBJ(self, room):
        self.channel = discord.utils.get(room.channels, name='playing-room')
        self.room = room
        await self.channel.send("The game of BlackJack has begun!")
        await self.blackJack()

    async def winCondition(self, player):
        totalPoints = sum([self.wagers[bet] for bet in self.wagers])
        for i in player:
            playerPoints[i.name] += totalPoints/len(player)
        update()
        await self.channel.send(f"{' ,'.join([i.name for i in player])} has earned {totalPoints} points for winning!")
        await self.channel.send("Party has automatically been disbanded. I hope to see you again!")
        _party.remove(self)
        for mem in self.room.members:
            try:
                if mem.name == "GameBot":
                    continue
                await mem.kick()
                await mem.send("The game is over! See you next time!")
            except:
                pass
        for channel in self.room.channels:
            try:
                async for msg in channel.history():
                    await msg.delete()
            except:
                pass
        room_status[self.roomNum] = False
    
    async def winBotCondition(self):
        await self.channel.send(f"It looks like I won with a score of {self.botP.sum}!")
        await self.channel.send("Party has automatically been disbanded. I hope to see you again!")
        _party.remove(self)
        for mem in self.room.members:
            try:
                if mem.name == "GameBot":
                    continue
                await mem.kick()
                await mem.send("The game is over! See you next time!")
            except:
                pass
        for channel in self.room.channels:
            try:
                async for msg in channel.history():
                    await msg.delete()
            except:
                pass
        room_status[self.roomNum] = False

    async def botPlay(self):
        self.botP = PlayerBJ(bot.user, self.possibleCards[-2:])
        self.possibleCards.pop()
        self.possibleCards.pop()
        await self._botPlay()

    async def _botPlay(self):
        highest = 0
        for i in self.players:
            if i.sum > highest:
                highest = i.sum
        if self.botP.sum > highest:
            await self.channel.send("Pass")
            await self.winBotCondition()
            return
        else:
            await self.channel.send("Hit")
            bCard = await self.drawCard()
            await self.channel.send(f"I drew a {bCard}.")
            result = self.botP.addCard(bCard)
            if result == True:
                await self.winBotCondition()
                return
            elif result == False:
                await self.channel.send("DAMMIT! I busted!")
                await self.winCondition([i for i in self.players if i.sum == highest])
                return
            else:
                await self._botPlay()

    async def initiateBT(self, room):
        self.channel = discord.utils.get(room.channels, name='playing-room')
        self.room = room
        await self.channel.send("Let the Big Two Game start!")
        await self.bigTwo()
    
    async def bigTwo(self):
        self.roundCount += 1
        self.gameID = 'bt'
        RANK_ORDER = '34567890JQKA2'
        SUIT_ORDER = 'DCHS'
        for i in RANK_ORDER:
            for suits1 in SUIT_ORDER:
                self.possibleCards.append(i+suits1)
        for i in range(20):
            random.shuffle(self.possibleCards)
            random.shuffle(self.members)
        if self.roundCount == 1:
            for i in self.members:
                self.players.append(PlayerBT(i, []))
        for i in range(13):
            for mem in self.players:
                mem.addCard(self.possibleCards.pop())
        for i in self.players:
            await i.playerRef.send(f"You cards are as follows: {', '.join(i.cards)}")
        self.index = 0
        for i in self.players:
            if "3D" in i.cards:
                break
            self.index += 1
        self.playerTurn = self.players[self.index]
        await self.channel.send(f"It's {self.playerTurn.name}'s' turn.")

    async def cardPlayed(self, cards, player):
        if self.startRound == True:
            self.startRound = False
        self.cardToBeat = cards
        self.cardToBeatPlayerRef = player
        self.playerTurn.played(cards)
        await self.channel.send(f"{self.playerTurn.name} has played {cards}.")
        await self.interim(None)

    async def resetRound(self, winner):
        tally = 0
        for mem in self.players:
            if mem == winner:
                continue
            num = len(mem.cards)
            if num < 10:
                tally += num*1
                mem.score -= num*1
            elif num >= 10 and num <= 12:
                tally += num*2
                mem.score -= num*2
            else:
                tally += 39
                mem.score -= 39
        winner.score += tally
        if self.roundCount == 10 or winner.score >= 100:
            await self.channel.send(f"{winner.name} has won! Congratulations! They get 5 points!")
            placings = [(i.score, i.name) for i in self.players if i != winner]
            placings.sort(key= lambda x : x[0], reverse=True)
            await self.channel.send(f"{placings[0][1]} came second with a score of {placings[0][0]}. They get 3 points!")
            await self.channel.send(f"{placings[1][1]} came third with a score of {placings[1][0]}. They get 1 points!")
            await self.channel.send(f"{placings[2][1]} came last with a score of {placings[2][0]}. They don't get any points!")
            await self.channel.send("Thanks for playing! Party will be disbanded automatically.")
            _party.remove(self)
            if self.friendly == False:
                playerPoints[winner.name] += 5
                playerPoints[placings[0][1]] += 3
                playerPoints[placings[1][1]] += 1
            else:
                pass
            for mem in self.room.members:
                try:
                    if mem.name == "GameBot":
                        continue
                    await mem.kick()
                    await mem.send("The game is over! See you next time!")
                except:
                    pass
            for channel in self.room.channels:
                try:
                    async for msg in channel.history():
                        await msg.delete()
                except:
                    pass
            room_status[self.roomNum] = False
            return
        self.cardToBeat = None
        self.startRound = True
        self.cardToBeatPlayerRef = None
        self.startTrick = True
        for i in self.players:
            i.newRound()
        await self.bigTwo()

    async def interim(self, keyword):
        if keyword == 'pass':
                await self.channel.send(f"{self.playerTurn.name} has decided to pass! The hand to beat is still {self.cardToBeat}.")
        qWin = [i for i in self.players if len(i.cards) == 0]
        if len(qWin) > 0:
            await self.channel.send(f"{self.playerTurn.name} has no more cards in their hand! They win this round!")
            await self.resetRound(self.playerTurn)
            return
        check = [i for i in self.players if i.passed == True and i.playerRef != self.cardToBeatPlayerRef]
        if len(check) == 3:
            await self.channel.send(f"{self.cardToBeatPlayerRef.name} has won the trick with {self.cardToBeat}! They get to start the next trick.")
            starter = [i for i in self.players if i.playerRef == self.cardToBeatPlayerRef][0]
            self.startTrick = True
            self.cardToBeat = []
            self.cardToBeatPlayerRef = None
            for i in self.players:
                i.passed = False
            self.index = self.players.index(starter)-1
        await self.updatePlayerTurn()
    

TOKEN = 'NDgyMzU1NzkzMzYyOTQ0MDIw.DmEq1A.KpFPHTZAxpAhEpVZiZVGh8Ltuak'

bot = commands.Bot(command_prefix='$')
bot.remove_command("help")

def update():
    _list = {}
    for line in playerPoints:
        _list[line.id] = playerPoints[line]
    Score = open("Points.json", "w")
    json.dump(_list, Score) 
    Score.close()
    return    

@bot.command(pass_context = True)
async def party(ctx, name):
    for p in _party:
        if p.owner == ctx.message.author:
            await ctx.send("You've already created a party doofus!")
            return
        elif p.name == name:
            await ctx.send(f"There's already a party with the name {name}, you uninspired hack!")
            return
    party = Party(ctx.message.author, name)
    _party.append(party)
    await party.createMessage(ctx)


@bot.command(pass_context = True)
async def join(ctx, name):
    if name not in [i.name for i in _party]:
        await ctx.send(f"You must've gotten the wrong details. No party called {name} has been created!")
        return
    target = [i for i in _party if i.name == name][0]
    if len(target.members) >= 4:
        await ctx.send("Sorry, the party's full. Try again later.")
        return
    elif ctx.message.author == target.owner:
        await ctx.send("You are the owner...")
        return
    elif ctx.message.author in target.members:
        await ctx.send("You're already in the party!")
        return
    await target.addMember(ctx, ctx.message.author)
    return
    
@bot.command(pass_context = True)
async def disband(ctx, name):
    try:
        target = [i for i in _party if i.name == name][0]
    except:
        await ctx.send("There's no party with that name")
        return
    if target.owner != ctx.message.author:
        await ctx.send("You are not the owner!")
        return
    _party.remove(target)
    return await ctx.send("Party disbanded.")


@bot.command(pass_context = True)
async def playBJ(ctx, action):
    user = ctx.message.author
    actions = ['hit', 'pass']
    try:
        target = [i for i in _party if user in i.members][0]
    except:
        await ctx.send("You're not in a party...")
        return
    turn = target.playerTurn.playerRef
    if user != turn:
        await ctx.send("It's not your turn yet you heartless cheater!")
        return
    elif action.lower() not in actions:
        await ctx.send("I don't know what you want to do... You can either hit or pass.")
        return
    if action.lower() == 'hit':
        card = await target.drawCard()
        await ctx.send(f"{target.playerTurn.name} has drawn a.... {card}!")
        result = target.playerTurn.addCard(card)
        if result == True:
            await ctx.send(f"{target.playerTurn.name} has won! Congratulations!")
            await target.winner.append(target.playerTurn.playerRef)
        elif result == False:
            await ctx.send(f"Oh no! {target.playerTurn.name} has busted! Unlucky!")
            target.playerTurn.bust = True
            await target.updatePlayerTurn()
        else:
            await ctx.send(f"{target.playerTurn.name} is now on {result}")
            await ctx.send("Your current hand is: ?, {}\nHit or pass?".format(target.playerTurn.cards[1:]))
    else:
        target.playerTurn.passed = True
        await ctx.send(f"{turn.name} has decided to pass with a score of {target.playerTurn.sum}!")
        await target.updatePlayerTurn()
    
    if len([i for i in target.players if i.passed == True or i.bust == True]) == 4:
        await ctx.send("Everyone has passed! Time for me to play!")
        target.botPlay()
    elif len([i for i in target.players if i.win == True or i.bust == True or i.passed == True]) == 4:
        await ctx.send("That's the end of the round!")
        await target.winCondition([i.playerRef for i in target.players if i.win == True])
    
@bot.command(pass_context = True)
async def playBT(ctx, cards): 
    user = ctx.message.author
    try:
        target = [i for i in _party if user in i.members][0]
        if target.gameID != 'bt':
            await ctx.send("You're playing the wrong game. Use playBJ to play BlackJack.")
            return
    except:
        await ctx.send("You're not in a party...")
        return
    if target.playerTurn.playerRef != user:
        await ctx.send("It's not your turn!")
        return
    if cards.lower() == 'pass':
        if target.startTrick == True:
            await ctx.send("You can't pass when you're starting a trick!")
            return
        target.playerTurn.passed = True
        await target.interim('pass')
        return
    intake = cards.split(",")
    if bt.valid_play(intake) == False:
        await ctx.send("You didn't play a valid hand. Cards played were not of the same rank or were not a proper five hand combo.")
        return
    for card in intake:
        if card not in target.playerTurn.cards:
            await ctx.send(f"You sneaky little cheater. Thought I wouldn't check if those cards were in your hands? THINK AGAIN! You don't have this card {card}!")
            return
    if target.startTrick == True:
        if target.startRound == True:
            if "3D" in intake:
                await target.cardPlayed(intake, user)
                target.startTrick = False
                return
            else:
                await ctx.send("You're starting the round! You have to play your 3D!")
                return
        await target.cardPlayed(intake, user)
        target.startTrick = False
        return
    result = bt.is_better_play(intake, target.cardToBeat)
    if result == True:
        await target.cardPlayed(intake, user)
    else:
        await ctx.send(f"You've played a hand that does not beat {target.cardToBeat}! Play another hand or pass.")

    

@bot.command(pass_context = True)
async def leave(ctx): 
    user = ctx.message.author
    try:
        target = [i for i in _party if user in i.members][0]
    except:
        await ctx.send("You're not in a party...")
        return
    await target.removeMember(ctx, user)

@bot.command(pass_context = True)
async def start(ctx, game):
    try:
        target = [i for i in _party if i.owner == ctx.message.author][0]
    except:
        await ctx.send("You are not the owner of any party!")
        return
    if len(target.members) != 4:
        await ctx.send("Not enough players")
        return
    check = [rooms[i] for i in rooms if room_status[i] == False ]
    if len(check) == 0:
        await ctx.send("Sorry, no rooms are available currently. Use $status to check whether a room will become free later.")
        return
    if game.lower() not in ['bj', 'bt', 'btf']:
        await ctx.send("I don't know that game...")
        return
    for room in rooms:
        if room_status[room] == False:
            ref = room
            room = rooms[room]
            break
    if game.upper() == "BJ":
        await ctx.send("Please place your bets everyone!")
    elif game.upper() == "BTF":
        target.friendly = True
        room_status[ref] = True
        target.roomNum = ref
        invite = await discord.utils.get(room.channels, name='playing-room').create_invite(max_uses=4)
        for i in target.members:
            await i.send(invite)
        await target.initiateBT(room)

    elif game.upper() == "BT":
        room_status[ref] = True
        target.roomNum = ref
        invite = await discord.utils.get(room.channels, name='playing-room').create_invite(max_uses=4)
        for i in target.members:
            await i.send(invite)
        await target.initiateBT(room)


@bot.command(pass_context = True)
async def scoreboard(ctx):
    f = open("Points.json", "r")
    f = json.load(f)
    lead = []
    for i in f:
        lead.append((int(f[i]), users[i]))
    lead.sort(key=lambda x: x[0], reverse=True)
    board = []
    place = 1
    for i in lead:
        if lead.index(i) == 10:
            break
        score, user = i[0], i[1]
        if str(place)[-1] == "1":
            local = "st"
        elif str(place)[-1] == "2":
            local = "nd"
        elif str(place)[-1] == "3": 
            local = "rd"
        else:
            local = "th"   
        board.append("|{}{}| {}: {}".format(place, local, user, score))
        place += 1
    embed = discord.Embed(title="Points Leaderboard:", color=discord.Color.from_rgb(255, 255, 102),
    description=f'As of currently:')
    embed.add_field(name="Points:", value='\n\n'.join(board))
    await ctx.send(embed=embed)
    f.close()

@bot.command(pass_context = True)
async def status(ctx):
    embed = discord.Embed(title="Game Rooms Available: ", color=discord.Color.from_rgb(66, 244, 78),
        description='Status of Rooms')
    for i in room_status:
        if room_status[i] == False:
            embed.add_field(name=f"Game Room #{i}", value="```css\nThis room is available!\n```")
        else:
            embed.add_field(name=f"Game Room #{i}", value="```diff\n-This room is being used.\n```")
    await ctx.send(embed=embed)

@bot.command(pass_context = True)
async def balance(ctx):
    user = ctx.message.author.name
    await ctx.send(f"You currently have {''.join([str(playerPoints[i]) for i in playerPoints if i == user])} points.")

@bot.command(pass_context = True)
async def bet(ctx, amount):
    user = ctx.message.author
    try:
        target = [i for i in _party if user in i.members][0]
    except:
        await ctx.send("You're not in a party...")
        return
    try:
        amount = int(amount)
    except:
        await ctx.send("Could you please bet in a base-10 amount?")
        return
    if user in target.wagers:
        await ctx.send("You've already betted...")
        return
    elif amount > playerPoints[user.name]:
        await ctx.send("You can't bet more points than you have genius...")
        return
    elif amount == 0:
        await ctx.send("You can't bet nothing... Try again!")
        return
    elif amount < 0:
        await ctx.send("Hey! I see what you're trying to do... Taking advantage of me? NO. Place a positive integer bet.")
        return
    else:
        target.wagers[user] = amount
        playerPoints[user.name] -= amount
        update()
        if len(target.wagers) == 4:
            for room in rooms:
                if room_status[room] == False:
                    ref = room
                    room = rooms[room]
                    break
            room_status[ref] = True
            target.roomNum = ref
            invite = await discord.utils.get(room.channels, name='playing-room').create_invite(max_uses=4)
            for i in target.members:
                await i.send(invite)
            await target.initiateBJ(room)

@bot.command(pass_context = True)
async def help(ctx):
    messages = {
        "General Commands:" : "**- $party {party_name} -** Creates a party with the desired name given. Keep in mind that this bot will automatically correct it to title case.\n**- $join {party_name} -** Join a party with the given party name.\n**- $leave -** Leave the current party you are in.\n**- $disband {party_name} -** Disband a party with the name given. Must be the party owner.\n**- $viewParty {party_name} -** View the status of the given party.\n**- $status -** View the current stastuses of the avaiable game rooms.\n**- $balance -** View how many points you currently have.\n**- $scoreboard -** Displays a scoreboard with all users and their points.\n**- $start {game_name} -** Start a game of either Blackjack (bj), Big Two (bt) or Big Two Friendly (btf). You must have a party and that party must have four members.\n**- $rules {game_name} -** Displays the game rules for the specified game.",
        "Game Commands:" : "**- $playBJ {action} -** Indicates your decision to either hit or pass. Action parameter must either be 'pass' or 'hit'\n**- $playBT {cards} -** Play your selection of cards. When playing more than one card, please adhere to this format: $playBT Card1,Card2,Card3,Card4,Card5. Must use in your personal dm/pm of the bot unless you want people to see your cards.\n**- $bet {amount} -** Bet a certain amount of points to the BlackJack match."
    }
    embed = discord.Embed(title="Help Menu", color=discord.Color.from_rgb(100, 149, 237),
    description=f'These are the commands that this bot currently has:')
    for cmd in messages:
        embed.add_field(name=cmd, value=messages[cmd], inline=False)
    embed.set_footer(text="Good luck and have fun! Bot created by Hayton Lam (SuperNovae#6180).")
    await ctx.send(embed=embed)

@bot.command(pass_context = True)
async def rules(ctx, game):
    game = game.lower()
    if game not in ["bt", "bj"]:
        await ctx.send("Perhaps you meant Big Two (bt) or Blackjack (bj)?")
        return
    await ctx.send("Rules haven't been coded by my lazy, good-for-nothing programmer yet. Sorry :( Come back another time!")



@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    status = discord.Activity(name='Type $help for commands.', type=discord.ActivityType.playing)
    await bot.change_presence(status=type, activity=status)
    checkRef = []
    for guild in bot.guilds:
        for member in guild.members:
            if member in checkRef:
                continue
            users[str(member.id)] = member
            checkRef.append(member)
    f = open("Points.json", 'r')
    f = json.load(f)
    for i in f:
        playerPoints[users[i]] = f[i]
    count = 1
    for i in bot.guilds:
        if "Game Room #" in i.name and i.name != "Game Room #0":
            rooms[count] = i
            count += 1





bot.run(TOKEN)



