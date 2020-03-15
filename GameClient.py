from Client import Client
from StringTranslator import StringTranslator
import threading
from ClientInterface import ClientInterface


# Client handler to play the game
# Handles player mechanics and communication back to server
class GameClient():
    def __init__(self):
        self.client = Client()
        self.interface = ClientInterface()
        self.state = "alive"

    # Runs the game from the client side
    def run(self):
        self.startGame()  # Starts the game
        while not self.game_over:  # Plays turns until the game is over
            self.game_over = self.playTurn()

    # Sets up the game
    def startGame(self):
        self.game_over = False
        self.client.connect()  # Connects to the server
        self.receive()
        if self.last_comm == "assignment_first":  # If client is first server
            self.sendAutomatedResponse(self.interface.handleFirstUser())
        elif self.last_comm == "assignment_post":
            self.sendDummyResponse()
        else:
            raise Exception(self.last_comm + " is invalid assignment.")
        self.enterUsername()
        self.updatePlayerInfo()
        self.setPlayerType()

    # Allows user to sets username
    def enterUsername(self):
        self.receive()
        self.username = self.interface.getUsername()
        self.sendAutomatedResponse(self.username)

    # Updates information on the rest of the players
    def updatePlayerInfo(self):
        self.receive()
        # print(self.last_comm)
        self.player_info = StringTranslator.decode(self.last_comm)
        self.interface.handleUserInfo(self.player_info)
        self.sendDummyResponse()

    # Receives whether player is mafia, doctor, or villager
    def setPlayerType(self):
        self.receive()
        self.player_type = self.last_comm.split("_")[1]
        if (self.player_type == "mafia"):
            self.interface.sendOutput("You are a MAFIA!")
        elif (self.player_type == "doctor"):
            self.interface.sendOutput("You are a DOCTOR!")
        elif (self.player_type == "basic"):
            self.interface.sendOutput("You are a VILLAGER!")
        else:
            raise Exception("Player has not been properly assigned role.")
        self.sendDummyResponse()

    # Plays a single turn of the game
    def playTurn(self):
        self.turnStart()
        self.updatePlayerInfo()
        game_over = self.checkGameOver()
        if game_over:
            return True
        self.checkDiscussion()
        self.discussion()
        self.vote()
        game_over = self.checkGameOver()
        if game_over:
            return True
        return False

    # Handles mafia/doctor choosing to remove/save at start of turn
    def turnStart(self):
        turn_info = self.receive().split("_")
        self.day_num = turn_info[1]
        self.turn_choice = turn_info[2]
        # If user does not have to choose this turn
        if(self.turn_choice == "null"):
            self.interface.sendOutput(
                "Wait for mafia & doctor to make choices...")
            self.sendDummyResponse()
        # If user is mafia assigned with choosing this turn
        elif self.turn_choice == "kill":
            self.sendAutomatedResponse(self.interface.mafiaKill())
        # If user is doctor assigned with choosing this turn
        elif self.turn_choice == "heal":
            self.sendAutomatedResponse(self.interface.doctorHeal())
        self.handleKillNotification()
        self.sendDummyResponse()

    # Checks if mafia or villagers have won the game
    def checkGameOver(self):
        self.receive()
        self.sendDummyResponse()
        winner = self.last_comm.split("_")[1]
        if winner == "none":
            return False
        else:
            if winner == "mafia":
                mssg = "The Mafia has won. The villagers have been eradicated."
            elif winner == "village":
                mssg = "The Villagers have won. The mafia has been eradicated."
            self.interface.sendOutput(mssg)
            print(mssg)
            self.interface.sendOutput("Press OK to exit game.")
            self.interface.getInput()
            return True

    # Checks if server & client are synced correctly right before discussion
    def checkDiscussion(self):
        self.receive()
        if self.last_comm != "discussion":
            raise Exception("Server should be primed for discussion")
        else:
            self.interface.sendOutput(
                "30-second discussion beginning. See chat output in terminal.")
            self.sendDummyResponse()
        # self.interface.startChat()

    # Facilitates inter-player discussion for specific player
    def discussion(self):
        self.continue_ = True  # Whether to continue discussion
        self.done_sending = False  # Whether code is done sending messages

        # Handles receiving of messages
        def func1(self):
            # self.interface.startChat()
            while self.continue_:
                self.receive()
                self.interface.sendDiscussionOutput(self.last_comm)
                # print(self.last_comm)
                if self.last_comm == "--exit--":
                    self.interface.sendOutput(
                        "Exiting discussion... Please press OK")
                    self.continue_ = False

        # Handles sending of messages
        def func2(self):
            while self.continue_:
                mssg = self.getDiscussionInput()
                self.sendAutomatedResponse(mssg)
            self.done_sending = True

        t1 = threading.Thread(target=func1, args=(self,))
        # t2 = threading.Thread(target=func2, args=(self,))
        t1.start()
        # t2.start()
        func2(self)
        while self.continue_:
            pass
        while not self.done_sending:
            pass
        if self.state != "dead":
            # self.sendAutomatedResponse("exit_discussion")
            pass
        self.sendDummyResponse()
        # print("DISCUSSION COMPLETE")

    # Gets user messages to send for discussion
    def getDiscussionInput(self):
        mssg = self.interface.getDiscussionInput()
        if self.state == "dead":  # Does not send message if user is dead
            return "REDACTED_DEAD"
        return self.username + " >> " + mssg

    # Allows player to vote who to remove from game
    def vote(self):
        self.receive()
        if self.last_comm != "vote_kill":
            raise Exception(
                "Server should send 'vote_kill', not '" + self.last_comm + "'")
        else:
            if self.state == "dead":
                self.sendAutomatedResponse("-1")
            else:
                self.sendAutomatedResponse(self.interface.killVote())
            self.handleKillNotification()
            self.sendDummyResponse()
            self.updatePlayerInfo()

    # Receives notification on who is removed from game
        # Checks if player removed is themselves, updates variables accordingly
    def handleKillNotification(self):
        kill_info = self.receive().split("_")
        if kill_info[2] == "you":  # If you just died
            self.interface.sendOutput("You just died!")
            self.state = "dead"
            # print("DIED")
        else:  # If someone else died
            pass

    # Receives a message from the server
    def receive(self):
        self.last_comm = self.client.receive()
        return self.last_comm

    # Sends a response to server of ---
    def sendDummyResponse(self):
        self.sendAutomatedResponse("---")

    # Send a response to server of the value of parameter
    def sendAutomatedResponse(self, response):
        self.client.send(response)
        return response


if __name__ == '__main__':
    client = GameClient()
    client.run()
