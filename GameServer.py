from Server import Server
import threading
from random import choice
from StringTranslator import StringTranslator
from time import sleep


# Server handler to play the game
# Handles game mechanics and communication with players
class GameServer:
    def __init__(self):
        self.server = Server()

    # Called to run the actual game from the server side
    def run(self):
        self.startGame()  # starts / sets up game
        while not self.game_over:
            self.game_over = self.playTurn()  # plays turns until game over

    # Runs to start up the game
    def startGame(self):
        self.game_over = False
        self.day_count = 0  # Counts number of turns played
        self.setFirstUser()
        self.setPostUsers()
        self.setUsernames()
        self.setPlayerTypes()
        # Saves states of each player (alive or dead)
        self.player_states = ["alive" for _ in range(self.player_count)]

    # Sets up first user, asks for & sets game rules using the first user
    def setFirstUser(self):
        self.server.connect()
        response = self.server.initial_client.ask("assignment_first")
        response = response.split(" ")
        self.player_count = int(response[0])  # Number of players in the game
        self.mafia_count = int(response[1])  # Number of mafia in the game
        self.doctor_count = int(response[2])  # Number of doctors in the game

    # Sets up all of the users after the first user
    def setPostUsers(self):
        for i in range(1, self.player_count):
            self.server.connect()
            self.getUser(i).ask("assignment_post")

    # Asks and sets the usernames for all players
    def setUsernames(self):
        self.names = self.askAll("username")
        data = [[str(i), self.names[i], "alive", "unknown"]
                for i in range(len(self.names))]
        self.askAll(StringTranslator.encode(data))

    # Sets which players are mafia, doctors, or villagers
    def setPlayerTypes(self):
        players_left = [i for i in range(self.player_count)]
        player_assignments = [None for _ in range(self.player_count)]
        self.mafia = []
        self.doctors = []
        for i in range(self.mafia_count):
            m = choice(players_left)
            players_left.remove(m)
            self.mafia.append(m)
            player_assignments[m] = "player_mafia"
        for i in range(self.mafia_count):
            d = choice(players_left)
            players_left.remove(d)
            self.doctors.append(d)
            player_assignments[d] = "player_doctor"
        for i in players_left:
            player_assignments[i] = "player_basic"
        self.player_assignments = [i.split("_")[1] for i in player_assignments]
        self.askAllDifferent(player_assignments)

    # Plays a single turn of the game
    def playTurn(self):
        # Gets kill and save choices from doctor and mafia
        turn_mafia, turn_doctor, turns = self.askTurnChoices()
        kill_person = int(turns[turn_mafia])  # Who mafia specified to kill
        if turn_doctor == -1:  # If no doctors in game, thus no one to save
            heal_person = -1
        else:
            heal_person = int(turns[turn_doctor])
        if(kill_person == heal_person):  # If mafia and doctor pick same person
            kill_person = -1
            # Notifications sent to each player in the game on who died
            kill_mssg = ["kill_" + str(kill_person) + "_other"
                         for _ in range(self.player_count)]
        else:  # If mafia and doctor pick different people
            self.killPlayer(kill_person)  # Kills person mafia chose
            # Notifications sent to each player in the game on who died
            kill_mssg = ["kill_" + str(kill_person) + "_other"
                         for _ in range(self.player_count)]
            # 'you' specifies that player receiving the message has been killed
            kill_mssg[kill_person] = "kill_" + str(kill_person) + "_you"
        self.askAllDifferent(kill_mssg)  # Sends kill_mssg to everyone
        self.sendPlayerInfo()  # Sends updated info on every player
        game_over = self.checkGameOver()
        if game_over:
            return True
        self.sendDiscussionNotification()  # Starts inter-player discussion
        self.discussion()  # Facilitates inter-player discussion
        self.vote()  # Allows players to vote on who to remove from game
        game_over = self.checkGameOver()
        if game_over:
            return True
        self.day_count += 1
        return False  # If game is not over and another turn must be played

    # Asks mafia who they want to kill, doctor who they want to save
        # turn_mafia is index of player asked to choose someone to kill
        # turn_doctor is index of player asked to choose someone to save
        # turn_choices is responses of each client to save/kill/null question
    def askTurnChoices(self):
        day_string = "day_" + str(self.day_count) + "_"
        turn_choices = ["null" for _ in range(self.player_count)]
        turn_mafia = choice(self.mafia)
        turn_choices[turn_mafia] = "kill"
        if len(self.doctors) == 0:
            turn_doctor = -1
        else:
            turn_doctor = choice(self.doctors)
            turn_choices[turn_doctor] = "heal"
        turn_choices = [day_string + i for i in turn_choices]
        return turn_mafia, turn_doctor, self.askAllDifferent(turn_choices)

    # Checks if the mafia or villagers have won the game
    def checkGameOver(self):
        if self.player_states.count("alive") == 1:
            last_player = self.player_states.index("alive")
            if self.player_assignments[last_player] == "mafia":
                self.askAll("check_mafia")
                return True
            else:
                self.askAll("check_village")
                return True
        elif len(self.mafia) == 0:
            self.askAll("check_village")
            return True
        else:
            self.askAll("check_none")
            return False

    # Allows players to vote on how to remove from the game
    def vote(self):
        votes = self.askAll("vote_kill")
        to_kill = self.countVotes(votes)
        if(to_kill == -1):  # Should never actually be -1
            kill_mssg = ["kill_" + str(to_kill) + "_other"
                         for _ in range(self.player_count)]
        else:
            self.killPlayer(to_kill)
            kill_mssg = ["kill_" + str(to_kill) + "_other"
                         for _ in range(self.player_count)]
            kill_mssg[to_kill] = "kill_" + str(to_kill) + "_you"
        self.askAllDifferent(kill_mssg)
        self.sendPlayerInfo()
        '''
        votes = self.askAll("vote_kill")
        to_kill = self.countVotes(votes)
        kill_mssg = ["kill_" + str(to_kill) + "_other"
                     for _ in range(self.player_count)]
        kill_mssg[to_kill] = "kill_" + str(to_kill) + "_you"
        self.askAllDifferent(kill_mssg)
        self.sendPlayerInfo()
        '''

    # Counts all of the votes responded by each player
    def countVotes(self, x):
        x = [int(i) for i in x if int(i) != -1]
        v = [mitem for mitem in zip((x.count(item) for item in set(x)), set(
            x)) if mitem[0] == max((x.count(item) for item in set(x)))]
        v = [i[1] for i in v]
        return choice(v)

    # Facilitates discussion between players
    def discussion(self):
        self.continue_ = True
        threads = []
        for i in range(self.player_count):
            def func(self, index):
                current_client = self.getUser(index)
                while self.continue_:
                    r = current_client.receive()
                    if self.continue_:
                        self.sendAll(r)
            t = threading.Thread(target=func, args=(self, i,))
            threads.append(t)
            t.start()
        sleep(30)
        self.continue_ = False
        self.askAll("--exit--")
        print("DISCUSSION COMPLETE")

    # Notifies all players that discussion is beginning
    def sendDiscussionNotification(self):
        self.askAll("discussion")

    # Updates player variables to assign player as dead
    def killPlayer(self, index):
        index = int(index)
        if index in self.mafia:
            self.mafia.remove(index)
        elif index in self.doctors:
            self.doctors.remove(index)
        self.player_states[index] = "dead"

    # Sends information about all players to all players
    def sendPlayerInfo(self):
        info = [[i, self.names[i],
                 self.player_states[i],
                 self.player_assignments[i]]
                for i in range(self.player_count)]
        self.askAll(StringTranslator.encode(info))
        print("sent")

    # Asks each player the corresponding message by index from mssg_lst
        # Asking includes sending a message and receiving/returning feedback
    def askAllDifferent(self, mssg_lst):
        replies = [None for _ in range(self.player_count)]
        threads = []
        for i in range(self.player_count):
            def func(self, index):
                reply = self.getUser(index).ask(mssg_lst[index])
                replies[index] = reply
            t = threading.Thread(target=func, args=(self, i,))
            threads.append(t)
            t.start()
        while None in replies:
            pass
        return replies

    # Asks each player the corresponding message by index from mssg_lst
        # messages in mssg_lst is an array that must be converted to string
    def askAllDifferentArrays(self, mssg_lst):
        replies = [None for _ in range(self.player_count)]
        threads = []
        for i in range(self.player_count):
            def func(self, index):
                mssg = StringTranslator.encode(mssg_lst[index])
                reply = self.getUser(index).ask(mssg)
                replies[index] = reply
            t = threading.Thread(target=func, args=(self, i,))
            threads.append(t)
            t.start()
        while None in replies:
            pass
        return replies

    # Asks each player the same message mssg
    def askAll(self, mssg):
        mssg_lst = [mssg for _ in range(self.player_count)]
        return self.askAllDifferent(mssg_lst)

    # Sends each player the corresponding message by index from mssg_lst
    def sendAllDifferent(self, mssg_lst):
        threads = []
        for i in range(self.player_count):
            def func(self, index):
                self.getUser(index).send(mssg_lst[index])
            t = threading.Thread(target=func, args=(self, i,))
            threads.append(t)
            t.start()

    # Sends each player the same message mssg
    def sendAll(self, mssg):
        mssg_lst = [mssg for _ in range(self.player_count)]
        return self.sendAllDifferent(mssg_lst)

    # Returns the Client object for a user by given index
    def getUser(self, index):
        return self.server.client_sockets[index]


if __name__ == '__main__':
    server = GameServer()
    server.run()
