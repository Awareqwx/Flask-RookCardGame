import flask, rook

app = flask.Flask(__name__)
app.secret_key="BirdIsTheWord"

def isInt(value):
    try:
        int(value)
        return True
    except:
        return False

def nextPlayer():
    flask.session["player"] += 1
    if flask.session["player"] > 3:
        flask.session["player"] = 0
    if flask.session["state"] == "bid":
        while flask.session["game"]["players"][(flask.session["player"] - 1) if (flask.session["player"] != 0) else 3]["passed"]:
            flask.session["player"] += 1
            if flask.session["player"] > 3:
                flask.session["player"] = 0
        p = 0
        for i in flask.session["game"]["players"]:
            if not i["passed"]:
                p += 1
        if p == 1:
            flask.session["game"]["players"][flask.session["player"]]["bid"] = flask.session["bid"] if flask.session["bid"] != 25 else 0
            flask.session["state"] = "widow"
            flask.session["widow"] = "false"

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/newgame")
def newgame():
    #DEBUG: Clear out the session's database and send a warning if a game is in progress
    # return flask.redirect("/game/select") #DEBUG: Start using this when the database is up and running
    #DEBUG CODE BEGIN
    flask.session.setdefault("player", 0) #DEBUG Populate this with values at some point
    flask.session.pop("player")
    flask.session.setdefault("game", 0)
    flask.session.pop("game")
    flask.session.setdefault("widow", 0)
    flask.session.pop("widow")
    flask.session.setdefault("endHand", False)
    flask.session.pop("endHand")
    game = rook.Game()
    game.setupGame()
    flask.session["game"] = game.getDict()
    flask.session["state"] = "bid"
    flask.session["startplayer"] = 0
    flask.session["follow"] = "None"
    flask.session["bidStart"] = 0
    return flask.redirect("/game/start")
    #DEBUG CODE END

@app.route("/continue")
def cont():
    # #DEBUG: Load data from database
    # return flask.redirect("/game/select") #DEBUG: Start using this when the database is up and running
    #DEBUG CODE BEGIN
    if flask.session.setdefault("player", -1) == -1:
        return flask.redirect("/newgame")
    return flask.redirect("/game/start")
    #DEBUG CODE END


# @app.route("/game/select")
# def select():
#     return flask.render_template("select.html") #DEBUG: Start using this when the database is up and running



#@app.route("/game/start", methods=["POST"]) #DEBUG: Start using this when the database is up and running
@app.route("/game/start")
def start():
    #flask.session["player"] = flask.request.form["num"] #DEBUG: Start using this when the database is up and running
    #DEBUG: Start the game and initialize everything with database once that works properly
    #DEBUG CODE START
    flask.session["state"] = "bid"
    flask.session["player"] = flask.session["bidStart"]
    flask.session["bid"] = 25
    #DEBUG CODE END
    return flask.redirect("/game/play")

@app.route("/game/play")
def play():
    if flask.session.setdefault("player", -1) == -1:
        return flask.redirect("/game/select")
    if flask.session["state"] == "bid":
        if flask.session.setdefault("badbid", False):
            flask.session.pop("badbid")
            return flask.render_template("bid.html", game=flask.session["game"], player=flask.session["player"], bid=flask.session["bid"], bad=True)
        return flask.render_template("bid.html", game=flask.session["game"], player=flask.session["player"], bid=flask.session["bid"])
    elif flask.session["state"] == "widow":
        return flask.render_template("widow.html", game=flask.session["game"], player=flask.session["player"])
    elif flask.session["state"] == "trick":
        return flask.render_template("trick.html", game=flask.session["game"], player=flask.session["player"], follow=flask.session.setdefault("follow", "None"))
    else:
        return("/")

@app.route("/game/bid", methods=["POST"])
def bid():
    if(not isInt(flask.request.form["bidbox"])):
        print "Hello"
        flask.session["badbid"]=True
        return flask.redirect("/game/next")
    bid = int(flask.request.form["bidbox"])
    if bid == 0:
        flask.session["game"]["players"][flask.session["player"] - 1]["passed"] = True
        nextPlayer()
        return flask.redirect("/game/next")
    elif bid <= flask.session["bid"] or bid % 5 != 0:
        print "World"
        flask.session["badbid"]=True
        return flask.redirect("/game/play")
    flask.session["bid"] = bid
    nextPlayer()
    return flask.redirect("/game/next") 

@app.route("/game/next")
def next():
    return flask.render_template("next.html", player=flask.session["player"])

@app.route("/game/widow", methods=["POST"])
def widow():
    selectedCards = []
    for i in range(0, 5):
        selectedCards.append(int(flask.request.form["card" + str(i)]))
    game = rook.parseGame(flask.session["game"])
    cards = []
    for i in game.players[flask.session["player"] - 1].hand.cards:
        cards.append(i)
    for i in game.widow.cards:
        cards.append(i)
    hand = rook.Hand()
    newWidow = rook.Trick([])
    j = 0
    for i in range(0, len(cards)):
        print i, j, selectedCards[j], len(selectedCards)
        if i == selectedCards[j]:
            print "Hello"
            newWidow.addCard(cards[i])
            j += 1
            if j >= len(selectedCards):
                j = 0
        else:
            hand.addCard(cards[i])
    hand.sort()
    game.players[flask.session["player"] - 1].hand = hand
    game.trump = flask.request.form["trump"]
    game.widow = newWidow
    flask.session["game"] = game.getDict()
    flask.session["state"] = "trick"
    return flask.redirect("/game/play")

@app.route("/game/trick", methods=["POST"])
def trick():
    selected = int(flask.request.form["cardPlayed"]) - 1
    print selected
    game = rook.parseGame(flask.session["game"])
    print flask.session["player"]
    game.inPlay.addCard(game.players[flask.session["player"] - 1].hand.playCard(selected))
    if len(game.inPlay.cards) == 1:
        if game.inPlay.cards[0].color == "Blue":
            flask.session["follow"] = game.trump
        else:
            flask.session["follow"] = game.inPlay.cards[0].color
    flask.session["game"] = game.getDict()
    if len(game.inPlay.cards) == 4:
        print "Hello, World!"
        return flask.jsonify({"url":"/game/trickDone"})
    nextPlayer()
    print "Goodbye, World!"
    return flask.jsonify({"url":"/game/next"})

@app.route("/game/trickDone")
def trickDone():
    game = rook.parseGame(flask.session["game"])
    
    messages = []

    if(len(game.inPlay.cards) == 0):
        return flask.redirect("/game/nextTrick")

    #Checking to see who won the trick
    cards = game.inPlay.cards
    color = cards[0].color
    value = cards[0].value
    trumped = 0
    if color == game.trump:
        trumped = 1
    elif color == "Blue":
        trumped = 3
    index = 0
    for i in range(1, 4):
        print (color, value, i, cards[i].color, cards[i].value)
        if color != game.trump and color != "Blue":
            if cards[i].color == game.trump or cards[i].color == "Blue":
                color = cards[i].color
                value = cards[i].value
                index = i
                trumped = 2 if cards[i].color != "Blue" else 3
            else:
                if color == cards[i].color and value < cards[i].value:
                    color = cards[i].color
                    value = cards[i].value
                    index = i
        else:
            if (color == cards[i].color and value < cards[i].value) or color == "Blue":
                color = cards[i].color
                value = cards[i].value
                index = i
    winner = (flask.session["player"] + index + 1) % 4    #The index will be 0 if the first person to play a card won the trick, so
    trick = rook.Trick(cards)                             #if the current player is player 4 (index 3), the index of the winner should wrap
    game.players[winner].addTrick(trick)                  #around to 0. Likewise, if the 3rd player won (index 2) and the current player is 3
                                                          #(index 2), it should wrap around to player 2 (index 1).
    flask.session["player"] = winner #In Rook, the winner of the trick goes first on the next one
    game.inPlay = rook.Trick([])
    messages.append("Player " + str(winner + 1) + " won the trick.")
    messages.append("The trick goes to the " + ("odd" if winner % 2 == 0 else "even") + " team")
    if trumped == 0:
        messages.append("The trick was not trumped")
    elif trumped == 1:
        messages.append("Trump was led")
    elif trumped == 2:
        messages.append("The trick was trumped by Player " + str(winner + 1))
    else:
        messages.append("The rook was played by Player " + str(winner + 1))

    flask.session["game"] = game.getDict()
    return flask.render_template("trickOver.html", game=flask.session["game"], player=flask.session["player"], winning=trick, messages=messages)

@app.route("/game/nextTrick")
def nextTrick():
    game = rook.parseGame(flask.session["game"])
    if len(game.players[0].hand.cards) == 0:
        game.players[flask.session["player"]].addTrick(game.widow)
        game.widow = rook.Trick([])
        return flask.redirect("game/endHand")
    else:
        return flask.redirect("game/next")

@app.route("/game/endHand")
def endHand():
    game = rook.parseGame(flask.session["game"])

    reshow = flask.session.setdefault("endHand", False)

    flask.session["endHand"] = True

    messages = []

    oddPoints = 0
    evenPoints = 0
    oddBid = False
    bid = 0
    for i in range(0, 4):
        if(i % 2 == 0):
            if game.players[i].bid != 0:
                oddBid = True
                bid = game.players[i].bid
            for t in game.players[i].tricks:
                oddPoints += t.points
        else:
            if game.players[i].bid != 0:
                oddBid = False
                bid = game.players[i].bid
            for t in game.players[i].tricks:
                evenPoints += t.points
    messages.append("Score: Even - " + str(evenPoints) + " | Odd - " + str(oddPoints))
    if oddBid:
        if not reshow:    
            game.points[0] += evenPoints
        messages.append("Odd team won the bid with " + str(bid))
        if oddPoints >= bid:
            messages.append("Odd team made their bid")
            if not reshow:
                game.points[1] += oddPoints
        else:
            messages.append("Odd team did not make their bid")
            if not reshow:
                print (game.points, bid)
                game.points[1] -= bid
    else:
        if not reshow:
            game.points[1] += oddPoints
        messages.append("Even team won the bid with " + str(bid))
        if evenPoints >= bid:
            messages.append("Even team made their bid")
            if not reshow:    
                game.points[0] += evenPoints
        else:
            messages.append("Even team did not make their bid")
            if not reshow:    
                game.points[0] -= bid
    messages.append("Point Tally: Even - " + str(game.points[0]) + " | Odd - " + str(game.points[1]))
    
    flask.session["game"] = game.getDict()
    return flask.render_template("endHand.html", game=flask.session["game"], player=flask.session["player"], messages=messages)

@app.route("/game/newHand")
def newHand():
    flask.session.setdefault("endHand", False)
    flask.session.pop("endHand")
    game = rook.parseGame(flask.session["game"])

    game.newHand()

    flask.session["game"] = game.getDict()

    return flask.redirect("/game/start")

app.run(debug=True)