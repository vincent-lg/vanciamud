# Delays in commands

When we create a command, we sometimes need to make it "pause" for awhile, before going on.

## Creating delays in commands

Creating delays means creating different functions (or methods, in this context).  You won't be able to just use `time.sleep` in the middle of your command and have the command just pause before executing the next line of code.

> That's strange, I've just tried putting a `time.sleep` in my command, it works just fine...

Yes, it does work.  But if you have tried to enter another command, or connect with another session, or access the website, you may have noticed... nothing happens.  `time.sleep` "works" in that it makes a pause and blocks the program.  And blocking the program in a command means nothing runs.

Are you interested in why?  You might want to learn more about [TalisMUD's balance between async and sync](../dev/async.md).

So the answer is, `time.sleep` freezes the entire program and for that reason, it's not a very good option.  Fortunately, implementing the delays in commands is quite simple and it has additional advantages.

First, let's create a command to introduce the syntax.  In your "command/general" folder, create a file called "listen.py", adding the following code in it:

```python
from command import Command


class Listen(Command):

    """Intensely listen.

    Usage:
        listen

    """

    def run(self):
        """Run the command."""
        self.msg("You intensely listen for the smallest sound...")
        self.call_in(10, self.ear_horse)

    def ear_horse(self):
        """Called after 10 seconds."""
        self.msg("Finally you hear a horse neighing in the distance.")
```

Save your file, and restart TalisMUD.  Then try to listen:

```
> listen

You intensely listen for the smallest sound...
(... 10 seconds elapse...)
Finally you hear a horse neighing in the distance.
```

All that should be familiar, and if not, you might want to read more about commands in the [command tutorial](command.md).

Let's focus on the `run` method and the following lines:

*   We begin by sending a message to the character having called the command.  So far so good.
*   We then have a line with the `call_in` method.  You should read this line as "call the method ear_horse in 10 seconds".  Notice that there is no parents after `ear_horse`.  We give a reference to the method without calling it.

The lines below contain the definition for our `ear_horse` method.  It's pretty short.

> Why divide in two methods?  Couldn't we have used a keyword or something to "pause" the command without freezing the program?

There are other ways we could have paused this command.  The separation between two methods seems overkill at first... but it has an advantage:

Try to listen again... but while it's waiting, restart the game:

```
> listen

You intensely listen for the smallest sound...
(... a few seconds elapse...)

> restart

Restarting the game ...
... game restarted!
(... a few more seconds elapse...)
Finally you hear a horse neighing in the distance.
```

So the benefit is simple: one can restart the game (even shutting it down completely) and the delayed command will still proceed afterward.

In our simple use case, this might sound like a tiny advantage.  But consider commands that will need to store some information for a limited time and "block" the player while they do something.  If the delayed action disappeared while restarting the game, this could freeze players in states where they couldn't do anything (except, possibly, call for help).

> How does it even work?  I don't get it.  Nice to have but better to understand it!

When executing `call_in`, TalisMUD will generate a delay, containing the callback you have specified.  TalisMUD will schedule this delay to run in the given amount of time you have specified.  If the game is stopped, the service handling the delay will save to the database all the delays that haven't run yet.  When the game is back up, these delays will be read from the database and scheduled again, according to their new time frame.

> Can I pass in arguments to `call_in`?

Yes, you can send arguments, by passing them after the callback itself:

```python
    def run(self):
        """Run the command."""
        self.msg("You intensely listen for the smallest sound...")
        self.call_in(10, self.ear_horse, 35, key=True)

    def ear_horse(self, number, key=False):
        """Called after 10 seconds."""
        self.msg(
            f"Finally you hear a horse neighing in the "
            f"distance: {number} and {key}."
        )
```

In this case we specify two arguments to `call_in` after the callback:

* 35: this is a positional argument and will be sent as first argument to `ear_horse` (after `self`) ;
* `key=True`: this is a keyword argument and will be sent (as-is) to the `ear_horse` method.

Arguments have to be storable, though, meaning they cannot be of types that can't be stored by the `pickle` module.  To prevent errors (and bad surprises), `call_in` will perform a check right away to make sure whatever you give to it can be stored in the database, and will refuse if not.  If there's an error, you will see it in your MUD client when the `call_in` method executes.

> Can I have more than one callback?

Yes, there's no true limit to the number of delays in one command.  You could use `call_in` to call several methods, or even have these methods called after awhile use `call_in` as well.  That's not an issue:

```python
from random import choice

from command import Command


class Listen(Command):

    """Intensely listen.

    Usage:
        listen

    """

    def run(self):
        """Run the command."""
        self.msg("You intensely listen for the smallest sound...")
        methods = [self.hear_horse, self.hear_dog, self.hear_voice]
        self.call_in(10, choice(methods))

    def hear_horse(self):
        """Hearing a horse."""
        self.msg("Finally you hear a horse neighing in the distance.")

    def hear_dog(self):
        """Hearing a dog."""
        self.msg("Finally, you hear a dog barking.")

    def hear_voice(self):
        """Hearing a voice."""
        self.msg(
            "Finally, you hear a voice... but can't make words out... "
            "and listen harder."
        )
        self.call_in(15, self.hear_words)

    def hear_words(self):
        """Hearing words."""
        self.msg("You finally make out some words.")
```

That's a more interesting and complex example.  In the `run` method, we have three possible choices: `hear_horse`, `hear_dog` and `hear_voice`.  Again notice that we don't use parents after the name, that's just a referrence to the method.  We use `random.choice` to select one of them (randomly) and call it in 10 seconds.  But if the choice is `hear_voice`, we schedule another callback 15 seconds later.  Let's see it in action:

```
> listen

You intensely listen for the smallest sound...
(... after 10 seconds...)
Finally, you hear a dog barking.

> listen

You intensely listen for the smallest sound...
(... after 10 seconds...)
Finally, you hear a voice... but can't make words out... and listen harder.
(... after 15 seconds...)
You finally make out some words.
```

Of course, you can `restart` at any point while this method is waiting.  It will just start again whenever it can.

> Can I call `listen` several times while it's waiting?

You can.  At this point there's no way to avoid running the command several tiems.  If you type "listen" twice in your MUD client, it will start two different commands that might have different results.

```
> listen

You intensely listen for the smallest sound...
(... after 2 seconds...)

> listen

You intensely listen for the smallest sound...
(... after 8 seconds...)
Finally, you hear a voice... but can't make words out... and listen harder.
(... after 2 seconds...)
Finally, you hear a dog barking.
(... after 13 seconds...)
You finally make out some words.
```

That might seem surprising: why doesn't TalisMUD prevent this situation?  The answer is that TalisMUD has no way to know whether it's a normal situation or it should be avoided.  You can explain it using the command namespace.

## Using the command namespace as cooldown

To prevent the previous example from running, we should allow the character to run the command once... but then not be able to do so again, until the command has finished.

It's quite simple to do using the [command namespace](command-namespace.md):

```python
from random import choice

from command import Command


class Listen(Command):

    """Intensely listen.

    Usage:
        listen

    """

    def run(self):
        """Run the command."""
        is_running = self.db.get("is_running", False)
        if is_running:
            self.msg("Wait a little, the command is still running!")
            return

        self.db.is_running = True
        self.msg("You intensely listen for the smallest sound...")
        methods = [self.hear_horse, self.hear_dog, self.hear_voice]
        self.call_in(10, choice(methods))

    def hear_horse(self):
        """Called after 10 seconds."""
        self.msg("Finally you hear a horse neighing in the distance.")
        del self.db.is_running

    def hear_dog(self):
        """Hearing a dog."""
        self.msg("Finally, you hear a dog barking.")
        del self.db.is_running

    def hear_voice(self):
        """Hearing a voice."""
        self.msg(
            "Finally, you hear a voice... but can't make words out... "
            "and listen harder."
        )
        self.call_in(15, self.hear_words)

    def hear_words(self):
        """Hearing words."""
        self.msg("You finally make out some words.")
        del self.db.is_running
```

We have slightly modified the `run` method and the following methods.  We create an attribute on the [command namespace](command-namespace.md), called `is_running`.  If this attribute is present, we prevent the command from running.  Otherwise, we create the attribute and remove it when the command has stopped waiting:

```
> listen

You intensely listen for the smallest sound...
(... after 5 seconds...)

> listen

Wait a little, the command is still running!
(... after 5 seconds...)
Finally you hear a horse neighing in the distance.
```

The command namespace stores the information inside of the character, so it's only accessible to this character and this command.  It's a very good choice for a cooldown.  In terms of code, it can behave like a normal namepsace (you can use the dot notation to get, set and del attributes) and a dictionary (you can use the bracket notations `[]` and the dictionary methods, like `get` or `setdefault`).

Read more about [the command namespace in this tutorial](command-namespace.md).
