# Installation

The most adaptable way to install talisMUD is through code itself.  It might sound a bit confusing, but modifications will be so much easier and bug fixes can be implemented much more easily.

## Python 3.9 required

TalisMUD requires Python 3.9 or more recent to run.

The way to get it might be different on your system.

### On Linux

The easiest way to install Python 3.9 is probably through a package installer, if you have this option.  On Debian or Ubuntu, you would do this:

    sudo apt-get install python3.9

Installing through a package installer isn't always an option.  You can install from source if you prefer: to do so, [you might follow these instructions](https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/).

### On Windows or Mac OS

The easiest way to do it on these platforms is to head to [the Python website / downloads / Python 3.9](https://www.python.org/downloads/release/python-3912/) and follow instructions.  At the bottom of the page is the download table.  Download an installer for your system and run it, following instructions.

## Cloning TalisMUD from Github

The next step is to clone the repository from Github.

### Don't have Git?

If you're on Linux, again, you should be able to install Git quite easily through a package manager:

    sudo apt-get install git

On Windows or Mac OS, you could head over to [the Git download page](https://git-scm.com/downloads).  Again, download the installer and run it as per instructions.

### Cloning from Github

You can `cd` to the directory where you keep your projects.  Then run:

    git clone https://github.com/talismud/talismud.git

Or via SSH:

    git clone git@github.com:talismud/talismud.git

Either command should create a directory, named `talismud`, within which is the code of your future game.

## Creating a virtual environment

After cloning, move into the newly-created `talismud` directory:

    cd talismud

Then, let's create a virtual environment.  TalisMUD uses many dependencies; it's best to keep them separated from your system:

On Linux or Mac OS, where you have access to `python3.9` as a command, run:

    python3.9 -m venv pyenv --upgrade-deps

On Windows, you probably don't, but you could run `python` without specifying the version:

    python -m venv pyenv --upgrade-deps

(Here we call the directory to be created `pyenv`.  This is arbitrary, you can change this name.)

## Activating the virtual environment

Once created, you can activate the virtual environment.

-   On Windows, the command is as follows:

        pyenv\scripts\activate

    (Once again, adapt this to your virtual environment name if necessary.)

-   On Linux and Mac OS, use the command:

        source pyenv/bin/activate

In any case, if the operation is successful, you should see it in your prompt (the name of the active virtual environment should appear between brackets at the beginning of the line).

## Installing TalisMUD and its dependencies

The next step is to install all TalisMUD's dependencies.  Fortunately, it's quite easy:

    pip install .

This might take awhile.  Let it work.  If all goes well, you should see a line "Successfully installed..." with a lot of package names.

## Running TalisMUD for the first time

You can now go to the `src` directory:

    cd src

And run TalisMUD:

    talismud status

Starting the game is quite simple:

    talismud start

Now you can point your MUD client to `localhost`, port `4000` and access your newly-installed TalisMUD!

## Using TalisMUD again afterward

All the steps in the previous process aren't to be repeated each time you want to use TalisMUD, thanfully.  However, you still have to activate your virtual environment and move into the right directory.

    cd talismud
    # On Windows
    pyenv\scripts\activate
    # Or on Linux / Mac OS
    source pyenv/bin/activate
    # All systems:
    cd src
    # Playing around with TalisMUD:
    talismud sessions

> Can't I install `talismud` in the system itself?

If you have administration privileges on your platform and you don't use it except to run `talismud` and a few services you control, then you could:

    cd talismud
    sudo pip install .

That will install `talismud` as a system package and you will have the `talismud` command no matter where.  Notice that you still have to `cd` into your `src` game directory.

I would recommend using a virtual environment in production or development.  That might sound like a bit of overhead, but it has a lot of advantages.

Next step: [Learn TalisMUD's basics](basic.md).
