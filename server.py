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
        while flask.session["game"]["players"][flask.session["player"] - 1]["passed"]:
            flask.session["player"] += 1
            if flask.session["player"] > 3:
                flask.session["player"] = 0
        p = 0
        for i in flask.session["game"]["players"]:
            if not i["passed"]:
                p += 1
        if p == 1:
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
    flask.session.setdefault("tricks", 0)
    flask.session.pop("tricks")
    flask.session.setdefault("widow", 0)
    flask.session.pop("widow")
    game = rook.Game()
    game.setupGame()
    flask.session["game"] = game.getDict()
    flask.session["state"] = "bid"
    flask.session["tricks"] = []
    flask.session["startplayer"] = 0
    flask.session["follow"] = "None"
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
    flask.session["player"] = flask.session["startplayer"]
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
    selected = int(flask.request.form["card"])
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
        return flask.redirect("/game/trickDone")
    nextPlayer()
    return flask.redirect("/game/next")

@app.route("/game/trickDone")
def trickDone():
    game = rook.parseGame(flask.session["game"])
    
    flask.session["game"] = game.getDict()
    return flask.render_template("trickOver.html", game=flask.session["game"], player=flask.session["player"])

app.run(debug=True)