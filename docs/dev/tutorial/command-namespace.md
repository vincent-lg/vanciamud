# Command namespace

The command namespace is a simple shortcut between a [command](command.md) and the [database](database.md).  Its aim is to store persistent data for a command and a character.

## Scope and limits

The command namespace is a wrapper around the command object and the character (player or non-playing character) using it.  Therefore, each character using the same command has a different namespace.

> Why is it useful?

Oftentimes, you will find yourself wanting to store some data in the command for the character calling it, but you don't need this data to be shared by other commands.  Some examples of this feature could be:

-   I need to create a command with a cooldown (that is, a command that can't be run by the same character more than once every X seconds).

    In this case, it would be useful to just store the time when the command was called... and check this attribute the next time this command is called by the same character.

-   I need to store statistics on this command usage, for a character:

    That's pretty simple too.  If you want to store the number of times this command was called by each character, that's easy to do with the command namespace.

-   I need to store command-specific data.

    Not all data has to be shared.  If you want to create a command like 'goto' which allows administrators to move around the world without restraint, it would be useful to support aliasing some places.  Instead of typing "goto zone:sub:barcode", you could associate this barcode with an alias, like "home", and then just type "goto home".  Much easier to type.  But you don't want "home" to be the same for every administrator using it.  In this case, it makes sense to store aliases in the command namespace as well.

> How long will this data be stored?

The command namespace is permanent, so data that is stored there is never deleted, unless you do it (manually or not).  However, there are some cases when the data is removed, and that's the case when the character who has run this command is deleted (when the player is completely removed from the database, or when the non-playing character dies, for instance).  For players, that's almost never the case, and if it happens, all data related to a player is removed altogether (and this never happens unless you allow players to "suicide" themselves permanently).  For non-playing characters, it might happen when they die, because it removes the character in the database (by default, though there are workarounds).

> Can't another command access my command namespace?

Yes, another command can request access to your command namespace, although that's not often needed.  If you need it, consider sharing the data in another way, the command namespace is supposed to remain specific to a command and not be shared.

## Command namespace syntax

In your command, you can call `db` on the command instance.  This will return a namespace handler specific to the command and the character running it.  Sounds complicated?  Fortunately, it's easy to use:

```python
from command import Command


class Listen(Command):

    """Intensely listen.

    Usage:
        listen

    """

    def run(self):
        """Run the command."""
        # With `self.db`, you can query attributes on the command namespace.
        # That can be used like a dict to retrieve data that might be absent.
        example = self.db.get("example", None)

        # But if you're confident the data does exist, don't bother.
        # This will raise an exception if 'example' is absent.
        example = self.db.example

        # Modify an attribute, whether it exists or not.
        self.db.example = 128
        # (The previous line will trigger a save in the database).

        # And if it does exist and you want to remove it, just use del.
        del self.db.example
        # (Again, the previous line will trigger a save in the database).

        # Want all attributes?  You can easily browse the handler like a dict.
        for name, value in self.db.items():
            print(f"{name} = {value}")

        # Or know if an attribute exists, but don't retrieve its value?
        if "example" in self.db:
            # ...

        # In addition, if you're familiar with the dict type,
        # you can use these methods to make your code more concise.
        value = self.db.setdefault("number", 0)
        # (In the previous line, if the attribute "number" exists
        # in the namespace, its value will be returned.  Otherwise,
        # `0` will be set to this attribute (this will trigger a database
        # save) and it will be returned as well.)

        # Remove an attribute you're not sure exists.
        old_value = self.db.pop("number", 135)
        # (The previous line will remove the attribute "number" in
        # the command namespace, if it exists, and return its value.
        # A database save will be generated.  If the attribute
        # doesn't exist, `135` will be returned.)

        # Do a mass-modification (assign several attributes).
        self.db.update({"number": 10, "current_room": self.character.room})
        # (This will update two attributes at once.  They will
        # be written in the namespace, replacing their former value,
        # if they had any, triggering a database save in any case.)
```

In short, use `self.db` like a Python namespace: write in it, read from it, using the dot notation (`self.db.attribute`).  But it also supports the methods of a dictionary, which you can use to make your code more concise.

## The technical explanation

> If I'm not mistaken, my commands aren't stored in database... how come their namespace is?

Commands are definitely not stored in the database, except in some rare cases (like [command delays](command-delay.md)).  Their namespace is stored inside of the character namespace though.

The character namespace, which you can use with `character.db`, behaves exactly the same, but store data directly in the character.

So when, inside a command class, you do something like `self.db.attribute = 3`:

* The key is changed depending on the command creating it.
* Then the value is added to the character namespace.

> Hold on, I thought that was sort of the point, to avoid conflicts between commands?

And various command namespaces are kept separate.  If you're really curious, try executing the `listen` command with [a cooldown, the last example in this tutorial](command-delay.md) and while it's running, enter:

    py self.db

That will display your character's namespace.  And it, you will see a strange attribute:

    {..., '_command_general_listen_is_running': True, ...}

The command namespace is directly stored in your character's namespace.  But it makes sure to use a set of keys you are not likely to use by accident.

> Can I store anything in the command namespace?

Not really.  You can store a lot of things.  But ultimately, the values will be stored in the database and pickled, so anything that can't be pickled will generate an error.

The good news is, `pickle` can work with a lot of things: numbers, booleans, dates, even custom class instances or a lot of callables.

> Can I store other objects from the database?

You definitely can.  You might have noticed in the previous example when we stored a room inside of a command namespace.  You can store other characters, rooms, accounts or even sessions: they will be restored from the database itself.
