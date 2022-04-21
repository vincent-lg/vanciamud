# TalisMUD basics

Have you [installed TalisMUD on your system](install.md)?  Great!  The fun can begin.  You're on your way to creating the MUD you wish!  But you still have things to learn.  Let's familiarize ourselves with we have.

## TalisMUD directory

Whether you have cloned or downloaded the TalisMUD directory, you probably have a structure like this:

    LICENSE  README.md  config  docs  poetry.lock  pyenv  pyproject.toml  src  world

Let's examine some of these files and directories:

- `config`: this directory holds your configuration, that is, options that you can easily change.  Yes, you can easily change the code too, but a lot of things can be done by simply updating the configuration.  You might want to explore this directory and to read (or update) the file within it.
- `docs`: this directory holds the documentation, the very one you're reading now.  Some people prefer reading the documentation on a nice website.  But if you prefer to read the Markdown, you can definitely find it here.
- `pyenv`: that's the Python environment, if you followed the [installation steps](install.md), though it can have a different name.  It's not important, as long as its active when you use the `talismud` command.
- `src`: that's all the source code of TalisMUD, soon to become your game's source code.  You'll spend a lot of time in it, if playing with the code is your goal.
- `world`: this directory holds your persistent world definitions, called blueprints.  I don't mean your database, I mean the definition of your world that will be generated each time your database is deleted.  Chances are, you won't use that directory in production, except if you work with other builders.  But you will probably use it a lot in development, since it saves time and allows to run from a clean install.
- `poetry.lock`: this file is used to tell `pip` what to install.  It's an advanced (and replicable) requirement file.
- `pyproject.toml`: this is the game file that gives information on TalisMUD from a technical point of view.  You can edit it, but you don't really have to, unless you want to add dependencies.

It's worth insisting once more: do activate your virtual environment before running the `talismud` commands.

    # On Windows
    pyenv\scripts\activate
    cd src
    # On Linux or Mac OS
    source pyenv/bin/activate
    cd src

## Start the game, start the fun!

Enough theories!  Let's start the game to see what it does.

Through the console: run the command:

    talismud start

The `talismud` program will run a bit like a Linux Daemon: you need to start it, but it won't stop unless you ask it.  You can close the console after you have received the confirmation from this command and your game will keep on running.

    Starting the portal ...
    ... portal started.
    Starting the game ...
    ... game started (id=OjoxOjUyNDI1OjA6MA==, ...).

For the time being, let's ignore this talk about a [portal](#the-portal) and [game](#the-game), you don't really need to understand these processes right now.  If it's your first time running `talismud`, you will also be asked to create an administrator account.

If you haven't run the game previously (or if there's no administrator in your game), you will be asked to create one.  The administrator is the user that can run administrative commands in your game.  You don't want everyone to be able to do that, so you should choose a username, password (preferably strong password) and optionally an email address (you don't have to specify an email address).  You can create more administrator accounts afterward.

Once this is done, the game should indicate your administrator account has been set up.

While TalisMUD is running, you can connect to your game through a MUD client (like Telnet, TinTin++, MushClient).  To do so, open your favorite client and connect to:

*   Host name: localhost

    (Meaning your own machine.)

*   Port : 4000

If everything goes well, inside your client you should see a welcome message:

    Welcome to
              *   )           )                   (    (  (
            ` )  /(  (     ( /((        (  (      )\   )\ )\
             ( )(_))))\(   )\())\  (    )\))(  ((((_)(((_)(_)
            (_(_())/((_)\ (_))((_) )\ )((_))\   )\ _ )\)_()_)
            |_   _(_))((_)| |_ (_)_(_/( (()(_)  (_)_\(_) || |
              | | / -_|_-<|  _|| | ' \)) _` |    / _ \ | || |
              |_| \___/__/ \__||_|_||_|\__, |   /_/ \_\|_||_|
                                       |___/
    If you already have an account, enter its username.
    Otherwise, type 'new' to create a new account.
    Your username:

This welcome screen can be changed, and easily so, but let's not do it right now.  Let's check that your administrator account exists.  Enter the username you have selected earlier, then press RETURN.  You will be asked for the password.  Enter it.  You'll then see a list of characters to play from.  So far there shouldn't be more than one character in this account, so you can type 1 and then press RETURN.

You now should be inside your game world.  You can type in commands and see the result.  Congratulations!  There's much to be done for this TalisMUD experience to become your very own game, but everything that comes after that should hopefully be fun to do.

While TalisMUD is running, you can also access TalisMUD's website.  Open your favorite browser (Mozilla Firefox, Google Chrome, Microsoft Edge) and connect to http://localhost:4001/ .  This is your game website, and you can, of course, customize it.  That's part of your game experience, after all, and although you don't necessarily have to add a website to your game, it's not a bad idea, especially since TalisMUD offers one.

## Restart the game

When you'll start customizing, either your game or your website, you will probably make modifications in your game code.  This is how it's supposed to happen.  But whatever you've modified won't appear instantly in your current game.  This would be too dangerous.  Instead, you can modify (add or change Python files) in your code, but TalisMUD will keep on running on its current version until you tell it to restart.

The nice thing is, restarting TalisMUD won't disconnect any of your players.  It will create a short moment during which players can't type in commands, usually one second, and then the game will be up and running again.

To restart your game, you have several options:

-   Inside your game, with an administrator account, you can type the command:

        restart

    Players won't have access to this command and you should make sure not a lot of people have access to it.  It might only stop the game for a second, but if players are actively engaged in play and don't see it coming, they might grumble, especially if it happens every minute.  So try to make sure this restart command isn't open to a lot of people.

        > restart

        Restarting the game ...
        ... game restarted!

    And then you can go on.  This is unvaluable to fix bugs, add commands, fix small errors.  It's not common to completely shutdown the game and start it all over again.

-   In the console, you can achieve the same thing by running:

        talismud restart

    And if everything goes according to plans, you should see something like:

        Game stopping ...
        ... game stopped.
        Start game ...
        ... game started (id=OjoxOjUyNDg5OjA6MA==).

> How does it work?  It feels like magic!

This is a stark contrast to older MUD games that need to completely shutdown (disconnect everyone) to start over again.  This is accomplished through the [portal](#the portal) and [game](#the game) processes which will be discussed later.

## Stop the game completely

Sometimes it's necessary to stop the game altogether.  That might not be frequent in production, but that's probably going to happen a lot while developing on your local machine.  Again you have two options:

-   From the game, and an administrator account, type the command:

        shutdown

    The game will stop without confirmation and disconnect everyone.

-   In the console, enter the command:

        talismud stop

These commands will both stop the [game](#the-game) and [portal](#the-portal) processes.

## Two processes

It's time to see what the portal and game processes are, at least to have a basic understanding of the principle allowing TalisMUD to restart without disconnecting anyone.

### The portal

The portal is one of TalisMUD's processes.  The role of the portal is to listen to connections.  The portal doesn't do much but listens and forwards commands to [the game process](#the-game).  On the other hand, it does have an important role: players connect to the portal through different ports.  The portal doesn't contain your game at all (no command, context or web pages).  When the game is restarted, the portal just waits, patiently, for the game to be back.  Since players are connected to the portal, they're not disconnected and experience just a slight lag.

### The game

The game process contains, well, your game: your commands, your contexts, your web pages, your settings and everything else that makes up your game.  The only thing the game process doesn't contain is a mechanism to listen to new connections on ports, this role is devoted to the portal.

So the portal sits on ports, it's a gateway through which all traffic must go.  When the game restarts, the portal just waits for it to be back and then sends the commands again.

In short, your players will only interact with the portal.  You could picture it like pedestrians walking in the street.  They can stop at a house, or rather, in front of the portal.  The game (your house in this context) won't be accessible to them directly, but the portal is nice and allows your players to interact with the game.

## Up and running?  What next?

Hopefully, TalisMUD is now running on your machine.  What can you do next?  A lot of things, but where to start?

The next step will depend on you and your skills, or rather, what you want to learn:

*   I want to create things but not code.

    The good news is that you can potentially create everything (including commands) without coding.  Of course, you will have to write scripts to do so, which is a bit like coding, but that will be more simple and you will learn little by little through a custom tutorial.  In any case, you should head to the [builder tutorial](building).

*   I want to code, know how things work and modify them as early as I can.

    In this case, head to the [developer tutorial](dev/tutorial), a step-by-step guide on things to do to customize TalisMUD.  If you're already familiar with this tutorial, or with parts of TalisMUD, you might prefer to check out [the developer documentation](dev) which lists all topics you can learn.  It's somewhat more arid and might get you dizzy, but it's detailed and pragmatic.

## TalisMUD won't start, what's wrong?

Unfortunately, it's not completely impossible TalisMUD won't start, especially if you tweak the portal or game.  In this context it might be hard to know what's wrong, though not impossible.

### The start process freezes

One common problem is in the start process.  Say you have typed in the console:

    talismud start

It tells you it's trying to start the portal... and will wait... and will wait... and will finally fail, telling you it couldn't.  Or it will start the portal just fine, but will hang when starting the game.

TalisMUD will try to tell you what's wrong, but it can't always know.  The first thing is to head over to the log files.

Inside your "src" directory, you should see a sub-directory called "logs".  Inside should be several log files, that is files describing what has happened.  With luck they will contain your error.  Try to open either "portal.log" (containing the errors of the portal process) or "game.log" (containing the errors of the game process).  Look at the bottom of the files.  It's likely you'll find your error there with a full traceback.

Of course, a traceback is somewhat useless when you don't know the process used by TalisMUD, but the final line might help you understand the problem.  If not, don't hesitate to [contact a TalisMUD developer](contact.html).

If you don't even see a log file, it's possible that either process couldn't even log the error.  It's unusual, but not unheard of.  In this case you should run them separately.  (You see why these executables exist now!)

Go to the console and start your game, not through TalisMUD commands, but through the game script:

    python game.py

If everything goes well, the game should tell you that it's able to run.  If not, you will find a full traceback.

You can stop the game with `CTRL + C`.  If you think your error might come from the portal, run it in the console as well:

    python portal.py

Again, if the portal can connect, it will tell you.  Otherwise you will see a nice traceback.

TalisMUD will try to tell you if an error occurred, in particular, when you restart the game.  But it's not a guarantee of course.

Still stuck?  It might be time to reach out.  Please [contact the project developers](contact.md) and we'll try to help.  And update this page, if that's a question we often get!
