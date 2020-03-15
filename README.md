# The PiMafia Project
##### Torin Kovach
##### Last updated March 14th 2020

### General Description
PiMafia is a client-server structured network and software that allows its users to play a game of Mafia with each other. It can be run between devices on and simple Local Area Network (LAN).

### How to run PiMafia
Actually running PiMafia is quite simple! One device (Raspberry Pi) must act as the server, and other devices (anything that can run Python 3) must act as clients, thus connecting to the server. For both server and client devices, the first step is simply downloading the codebase, which can be found [here]().
To run the server (Raspberry Pi), simply execute the "GameServer.py" file from the codebase. The user should then be prompted to enter a port number. The port can be any number from 1 to 65535, but ports below 1024 may be protected and only available to superusers.
To run the client, simply execute the "GameClient.py" file from the codebase. The user should then be prompted to enter a port number and IP address of the server to connect to. Enter the same port number as the server entered, and then the IP address of the server. From here, a GUI will present itself with further instructions to play the game.
The server must be started before the client can connect without error. One device can be both a client and  server simultaneously. To test PiMafia on one device without a LAN, simply run "GameServer.py"once and GameClient.py" repeatedly as multiple different processes, then enter 127.0.0.1 as the IP address of the server.

### Rules
PiMafia works the same way as normal mafia, but with the server in charge. The first user (client) connected decides basic game rules, specifically the number of users, the number of mafia in the game, and the number of doctors in the game. After the specified number of users have connected, the server randomly assigns the roles of mafia and doctors to users. If a user is neither mafia or doctor, they are simply a villager. Users are not informed of the roles of any of the other users in the game. Then, turns begin until someone wins the game. At the start of the turn, or "night," one mafia and one doctor are picked at random and told to choose a user. Whoever the mafia picks is killed, or removed from the game, unless the doctor picks the same person, in which case they are "saved," and kept in the game. Then, the "day" segment of the game begins, and the users are allowed to digitally message with each other for 30 seconds. After this discussion, the users each vote on a person to "hang," or remove from the game. In the event of a tie, one of the tied users is chosen at random. Users removed from the game can spectate, but cannot be a part of the chat or vote. The game ends when either only mafia are left in the game (the mafia win) or only non-mafia are left in the game (villagers/doctors win).

### Technology Implemented
The entirety of the PiMafia project is built in Python 3. Further, it implements a variety of specific libraries and functionalities of this programming lenguage.
#### Multithreading
Multithreading allows a computer to create multiple different processes, or "threads," to be run concurrently. This allows for increased efficiency and decreased runtime in a piece of code. However, it can often be more difficult to implement and present specific problems, such as deadlock. In this project, multithreading is achieved via the [threading](https://docs.python.org/3/library/threading.html) module, and is primarily used in two major ways. First, it allows the server to communicate with all of the different clients at the same time, by managing each client on a separate thread. Second, it allows reading of both input and output during inter-user. For each user, one thread reads input to send to other users, while another receives input from other users to display.
#### Berkeley socket interface (BSD)
The Berkeley Socket Interface, or BSD socket application programming interface (API), is an interface to allow inter-process network socket communication. This API is what allows the server and clients to communicate in this project. The BSD socket API is handled by the python [socket](https://docs.python.org/3/library/socket.html) module in this project.
#### Graphical User Interface (GUI)
A simple graphical user interface is implemented to allow users to more easily interact with the system. The [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI) library is used to create this GUI. This did present some problems with multithreading, as the library only allows the GUI to be edited on the thread it was created. Thus, output during discussions is displayed not in the GUI, but in standard output. 

### Purpose & Aspirations
Beyond a fun game that we can all enjoy, PiMafia is meant to be a marketable project and product. I aspire to use the Open Source Donation model used by great projects such as Ubunutu, FireFox, and Wikipedia, where the software is free but users are motivated to donate. This will contibute the the overall online gaming market. The online gaming industry, valued at $78.61 billion dollars, contibutes greatly to the world economy, and provides many decent and well-paying jobs. Accordingly, this industry, and the PiMafia project, contibutes to the United Nations Sustainable Development Goal of Decent Work and Economic Growth, providing "sustained, inclusive and sustainable economic growth."