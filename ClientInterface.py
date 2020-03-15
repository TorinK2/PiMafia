import PySimpleGUI as sg
import os


# Handles GUI for one player
class ClientInterface:
    def __init__(self):
        self.theme = "DarkAmber"  # PySimpleGUI theme
        self.window_title = "PiMafia"  # Title of GUI window
        self.makeWindow()
        self.primer()
        '''
        while True:
            self.getInput()
            self.sendOutput("GAME OVER")
        '''

    # Build the GUI window
    def makeWindow(self):
        sg.theme(self.theme)
        self.layout = [[sg.Multiline(default_text='Press OK to begin!',
                                     key="output",
                                     size=(75, 15),
                                     autoscroll=True,
                                     font=(20))],
                       [sg.InputText(size=(75, 5), font=(20), key="input"),
                        sg.Button('OK')]]
        self.window = sg.Window(self.window_title, self.layout)

    # Gets the first input from the input box and sets up further input
    def getFirstInput(self):
        self.event, self.values = self.window.read()
        self.output_stream = (self.values['output'] +
                              ">> " + self.values['input'])
        self.window.Element('output').Update(self.output_stream)
        self.window.Element('input').Update("")
        return self.values['input']

    # Gets input after 'getFirstInput' has been run
    def getInput(self):
        self.event, self.values = self.window.read()
        self.output_stream += "\n>> " + self.values['input']
        self.window.Element('output').Update(self.output_stream)
        self.window.Element('input').Update("")
        return self.values['input']

    # Displays output on the GUI window
    def sendOutput(self, mssg):
        self.output_stream += "\n" + mssg
        self.window.Element('output').Update(
            self.output_stream)
        self.window.Refresh()

    # Sets up the GUI for further use
        # Displays the game rules
    def primer(self):
        self.getFirstInput()
        self.sendOutput(
            "Hello and welcome to PiMafia! " +
            "Do you want to see the rules? (y/n)")
        while True:
            input = self.getInput()
            if input.lower() == "y":
                # Gets rules from this filepath
                # Uses 'os' in case the game is run from terminal,
                        # and thus local directory is not the one
                        # the .py files exist in.
                path = os.path.dirname(os.path.abspath(
                    __file__)) + '/PiMafiaRules'
                with open(path, 'r') as out:
                        # Displays rules on GUI
                    self.sendOutput(out.read())
                break
            # If user does not want rules to be displayed
            elif input.lower() == "n":
                self.sendOutput("Alright, here we go then!")
                break
            else:  # Sanitizes input
                self.sendOutput("Please enter 'y' or 'n'")
        self.sendOutput("Connecting...")

    # Handles I/O for the first user to specify game settings
    def handleFirstUser(self):
        self.sendOutput("You are the first player connected to the system!" +
                        " You will need to define some " +
                        "variables about the game.")
        p_count = int(self.getSpecificChoice("How many players? (3-10)",
                                             range(3, 11), number=True))
        m_max = int(p_count / 2.0) + 1
        mafia_count = int(self.getSpecificChoice("How many mafia? (1-" +
                                                 str(m_max) + ")",
                                                 range(1, m_max + 1),
                                                 number=True))
        doctor_count = int(self.getSpecificChoice("How many doctors? (1-" +
                                                  str(m_max - 1) + ")",
                                                  range(1, m_max),
                                                  number=True))
        r_val = " ".join([str(a)
                          for a in [p_count, mafia_count, doctor_count]])
        # print(r_val)
        self.sendOutput("Waiting for others to connect...")
        return r_val

    # Handles I/O to get choice from user from choices
        # Prompts choice with value of question
        # If number=True is used, choices are treated as int
    def getSpecificChoice(self, question, choices, number=False):
        self.sendOutput(question)
        while True:
            input = self.getInput()
            if number:
                try:
                    input = int(input)
                except Exception as _:
                    self.sendOutput("Please provide valid input. " +
                                    "Input should be a number.")
                    continue
            if input in choices:
                return input
            else:
                self.sendOutput("Please provide valid input.")
                self.sendOutput(question)

    # Displays info on all users in the GUI and saves it in dict
    def handleUserInfo(self, info):
        self.info = info
        info_str = self.translateUserInfo()
        self.readUserInfo()
        self.sendOutput("Current player info:")
        self.sendOutput(info_str)

    # Translates user info into string to print
    def translateUserInfo(self, info=None):
        if info is None:
            info = self.info
        header_format = "{:>11}" * 3
        info_format = "{:>15}" * 3
        info_str = header_format.format(*["Number", "Username", "State"])
        info_str += "\n" + "-" * len(info_str)
        for line in info:
            new_line = [line[i] for i in range(3)]
            info_str += "\n" + info_format.format(*new_line)
        return info_str

    # Reads user info into dictionary to save
    def readUserInfo(self):
        info = self.info
        player_dict = {}
        for p_lst in info:
            main_key = int(p_lst[0])
            sub_keys = ["name", "state", "role"]
            sub_values = [p_lst[i] for i in range(1, 4)]
            sub_dict = {}
            for key, value in zip(sub_keys, sub_values):
                sub_dict.update({key: value})
            player_dict.update({main_key: sub_dict})
        self.player_dict = player_dict

    # Handles I/O for getting username from the user
    def getUsername(self):
        self.sendOutput("Please enter a Username:")
        return self.getInput()

    # Gets list of players that are alive
    def getValidPlayers(self):
        valid_input = []
        for p_key in self.player_dict:
            if self.player_dict[p_key]["state"] == "alive":
                valid_input.append(p_key)
        return valid_input

    # Asks mafia who they would like to remove from the game
    def mafiaKill(self):
        self.sendOutput("As mafia, you get to choose a person to kill!")
        return str(self.getSpecificChoice(
            "Please enter the number of the person you would like to kill:",
            self.getValidPlayers(),
            number=True))

    # Asks doctor who they would like to save
    def doctorHeal(self):
        self.sendOutput("As doctor, you get to choose a person to save!")
        return str(self.getSpecificChoice(
            "Please enter the number of the person you would like to save:",
            self.getValidPlayers(),
            number=True))

    # Gets input from user during discussion
    def getDiscussionInput(self):
        mssg = self.getInput()
        return mssg

    # Sends output from dicussion to user
    def sendDiscussionOutput(self, output):
        print(output)

    # Handles I/O for user to vote on who to remove from game
    def killVote(self):
        self.sendOutput("As a villager, you get to vote on a person to kill!")
        return str(self.getSpecificChoice(
            "Please enter the number of the person you would like to kill:",
            self.getValidPlayers(),
            number=True))


# Test of ClientManager functionality:
if __name__ == '__main__':
    test = ClientInterface()
    # test.primer()
    test.handleUserInfo([["0", "Alpha", "alive", "Basic"],
                         ["1", "Beta", "alive", "Mafia"],
                         ["2", "Gamma", "dead", "Doctor"],
                         ["2", "Lambda", "dead", "Basic"]])
    print(test.player_dict)
    print(test.getValidPlayers())
