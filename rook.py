import random

class Card(object):
    def __init__(self, color, value):
        self.color = color
        self.value = value
    
    def getPoints(self):
        if self.value == 5:
            return 5
        elif self.value == 10 or self.value == 14:
            return 10
        elif self.value == 20:
            return 20
        else:
            return 0
    def showCard(self):
        if self.value == 20:
            print "The Rook"
        else:
            print self.color, self.value

    def getDict(self):
        return {"color":self.color,"value":self.value}

class Deck(object):
    def makeDeck(self):
        self.cards = []
        colors = ["Red", "Yellow", "Green", "Black"]
        for i in colors:
            for j in range (1, 15):
                self.cards.append(Card(i, j))
        self.cards.append(Card("Blue", 20))

    def shuffle(self):
        for i in range(0, len(self.cards)):
            r = random.randrange(0, len(self.cards))
            temp = self.cards[i]
            self.cards[i] = self.cards[r]
            self.cards[r] = temp

    def showDeck(self):
        for i in self.cards:
            i.showCard()

    def __init__(self):
        self.makeDeck()
        self.shuffle()

class Hand(object):
    def __init__(self):
        self.cards = []

    def addCard(self, card):
        self.cards.append(card)
    
    def playCard(self, ind):
        return self.cards.pop(ind)

    def showHand(self):
        for i in self.cards:
            i.showCard()
    
    def sort(self):
        self.cards = sorted(self.cards, key=lambda card: (card.color, -card.value))
    
    def getDict(self):
        cardList = []
        for i in self.cards:
            cardList.append(i.getDict())
        return {"cards":cardList}

class Trick(object):
    def totalPoints(self):
        self.points = 0
        for i in self.cards:
            self.points += i.getPoints()
    def __init__(self, cards):
        self.cards = cards
        self.totalPoints()
    def addCard(self, card):
        self.cards.append(card)
        self.points += card.getPoints()
    def getDict(self):
        cardList = []
        for i in self.cards:
            cardList.append(i.getDict())
        return {"cards":cardList,"points":self.points}

class Player(object):
    def __init__(self, hand, team):
        self.hand = hand
        self.bid = 0
        self.tricks = []
        self.team = team
        self.passed = False
    
    def getDict(self):
        trickList = []
        for i in self.tricks:
            trickList.append(i.getDict())
        return {"hand":self.hand.getDict(),"bid":self.bid,"tricks":trickList,"team":self.team,"passed":self.passed}
        
def deal(deck):
    dealt = [Hand(), Hand(), Hand(), Hand(), Hand()]
    count = 0
    while len(dealt[4].cards) < 5:
        dealt[count % 5].addCard(deck.cards.pop())
        count += 1
    while len(deck.cards) > 0:
        dealt[count % 4].addCard(deck.cards.pop())
        count += 1
    return dealt
    
class Game(object):
    def __init__(self):
        self.players = []
        self.trump = "None"
        self.widow = Trick([])
        self.inPlay = Trick([])
    
    def setupGame(self):
        self.deck = Deck()
        self.hands = deal(self.deck)
        for i in self.hands:
            i.sort()
        for i in range(0, 4):
            self.players.append(Player(self.hands[i], (i % 2) + 1))
        self.widow = Trick(self.hands[4].cards)
    
    def getDict(self):
        playerList = []
        for i in self.players:
            playerList.append(i.getDict())
        return {"players":playerList,"trump":self.trump,"widow":self.widow.getDict(),"inPlay":self.inPlay.getDict()}
    
def parseCard(d):
    return Card(d["color"], d["value"])
def parseHand(d):
    cards = []
    for i in d["cards"]:
        cards.append(parseCard(i))
    h = Hand()
    h.cards = cards
    return h
def parseTrick(d):
    cards = []
    for i in d["cards"]:
        cards.append(parseCard(i))
    return Trick(cards)
def parsePlayer(d):
    h = parseHand(d["hand"])
    trickList = []
    for i in d["tricks"]:
        trickList.append(parseTrick(i))
    p = Player(h, d["team"])
    p.bid = d["bid"]
    p.passed = d["passed"]
    p.tricks = trickList
    return p
def parseGame(d):
    g = Game()
    playerList = []
    for i in d["players"]:
        playerList.append(parsePlayer(i))
    g.players = playerList
    g.widow = parseTrick(d["widow"])
    g.trump = d["trump"]
    g.inPlay = parseTrick(d["inPlay"])
    return g