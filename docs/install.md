# Installation

The most adaptable way to install talisMUD is through code itself.  It might sound a bit confusing, but modifications will be so much easier and bug fixes can be implemented much more easily.

## Python 3.9 required

TalisMUD requires Python 3.9 or more recent.

The way to get it might be different on your system.

## Clone TalisMUD from Github

## Create a virtual environment

After cloning, move into the newly-created `talismud  directory:

    cd talismud

Then, lets create a virtual environment.  TalisMUD uses may ndependencies; it's best to keep them separated from your system:

    python3.9 -m venv pynv --upgrade-deps

(Here we call the directory to be created `pyenv`.  This is arbitrary, you can change the name.)

## Activate the virtual environment

Once created, you can activate the virtual environment.

-   On Windows, the command is as follows:

        pyenv\scripts\activate

    (Once again, adapt this to your virtual environment name if necessary.)

-   On Linux and Mac OS, use the command:

        source pyenv/bin/activate

In any case, if the operation is successful, you should see it in your prompt (the name of the active virtual environment should appear between brackets at the beginning of the line).

## Install TalisMUD and its dependencies

The next step is to install all TalisMUD's dependencies.  Fortunately, it's quite easy:

    pip install .

This might take awhile.  Let it work.  If all goes well, you should see a line "Successfully installed..." with a lot of package names.

## Run TalisMUD for the first time

You can now go to the `src` directory:

    cd src

And run TalisMUD:

    python talismud.py status

Starting the game is quite simple:

    python talismud.py status

Now you can point your MUD client to `localhost`, port `4000` and access your newly-installed TalisMUD!

## Use TalisMUD again afterward

All the steps in the previous process aren't to be repeated each time you want to use TalisMUD, thanfully.  However, you still have to activate your virtual environment.

You can create a link (in Linux / Mac OS) or a Doskey (in Windows) to point `talismud` to the virtual environment no matter whether it's active or not.

