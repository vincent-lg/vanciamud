# Branches in command arguments

This tutorial will expand on command arguments to show you how to handle different syntax effortlessly in your commands.

## When is it necessary?

The command argument system explain [in the command tutorial](command.md) is powerful and saves you time coding.  It has one problem though: what to do when your command has a more complex syntax?


You might want to have a more diverse syntax for your command.  You will probably notice it in the help you provide your users: it can have different arguments or even set of arguments, depending on action.

In this tutorial, we'll elaborate on the `roll` command created in the [command tutorial](command.md), but we'll add different ways to use it.  Let's look at the help first:

```python
from command import Command


class Roll(Command):

    """Roll a die.

    Usage:
        roll <side>
        roll <times>d<side>

    You can execute this command in two ways: if you provide a number,
    only one die will be rolled.  The number you specify is the number
    of sides on this die:
       roll 6

    But you can also run this die many times in one command.  For instance,
    to run 3 six-sided dice at once, you can enter:
        roll 3d6
    In this second example, a 6-sided die will be rolled three times
    and the numbers added to obtain the result.

    """
```

If you have played MUDs that were created from paper roleplaying games, this might sound familiar.

Notice, in passing, that we're coding fro the help and, particularly, from the syntax.  This is not a bad idea, as first imagining how your player should use your command helps to create a more intuitive syntax.  You might come up with the greatest command in the world, but if it's not intuitive, your players might not bother to learn it.

## Group and branches in arguments

So to summarize, we have a command that can be used in two ways:

    roll <number>
    roll <number>d<other number>

> It seems easy enough.  Can't we just create the second number as optional?

You could.  Along with the delimiter (`d` in our case).  But it causes a problem: your players could enter something like `roll 2d` which will be valid for the parser, but not so valid for your use case.

Better, in this context, to create two argument branches.

So far, we've used a sequence of arguments in our command argument parser.  They are parsed one after the other and must be present, if they're not mandatory.  So there's only one path to execute our command.

But we can ask our parser to handle multiple possible paths, and that's what we're going to do.

*Note*: the arguments aren't exactly parsed sequentially in order even in a single branch.  Arguments that have a definited limit (like symbols, words or numbers) are parsed first, because some of the other arguments will just use "whatever is left", so they need to proceed next.

Back to argument parser.  To split it into several branches, we first need to create a group with the `add_group` method on our pasrser:

```python
group = args.add_group()
```

And from this group, we'll create branches with the group's `add_branch` method.

> Sounds complicated.  Why couldn't we just add branches from our parser?

In our example, we have two possible branches that start from the beginning of our argument.  But that's not always the case, so better keep them separate.  Besides, groups have another way to process branches, but we'll see this later.

Here's the command code (shortened to include only what's really needed) to show you the first branch:

```python
from command import Command


class Roll(Command):

    """Roll a die.
    ...
    """

    args = Command.new_parser()
    group = args.add_group()
    one_die = group.add_branch("roll_one_die")
    one_die.add_argument("number")
```

As explained, we'll first create a group with the parser's `add_Group` method.  We'll need to keep it in a variable, because we'll call its `add_branch` method next to create branches.

We create the first branch here.  Again, we keep the branch in a variable, because we'll call its `add_argument` method.  The branch is like a limited parser of its own.

> What's the argument to `add_branch`?

When we call `add_branch`, we give it a string.  This string is the method name that will be executed when this branch matches the parsed argument.

In other words, every branch can define a specific method.  They don't have to use `run`, which is good, because they can have very different arguments in the end.  We'll see how it works next.

As for our branch parser itself, we just add one number.  Nothing that should surprise you at this point.  As usual, you can configure this number if you need to change its limit, customize its messages and so on.

You might not see a huge improvement... so let's add our second branch:

```python
from command import Command


class Roll(Command):

    """Roll a die.
    ...
    """

    args = Command.new_parser()
    group = args.add_group()

    # First branch: one single die.
    one_die = group.add_branch("roll_one_die")
    one_die.add_argument("number")

    # Second branch: several dice (two numbers separated by 'd').
    several_dice = group.add_branch("roll_several_dice")
    several_dice.add_argument("number", dest="times")
    several_dice.add_argument("symbols", "d")
    several_dice.add_argument("number", dest="size")
```

As you can see, we add another branch to the group.  If parsed, this one should execute the `roll_several_dice` method in the class.  It has a more elaborate sequence of arguments, but fortunately, you should understand it more easily now.

> Can I run this code?  I want to see it in action!

Well, not quite yet.  We've defined two methods in our branches but we haven't defined them in our code yet.  That's easy to do, of course.  So here is our full code:

```python
from random import randint

from command import Command


class Roll(Command):

    """Roll a die.

    Usage:
        roll <side>
        roll <times>d<side>

    You can execute this command in two ways: if you provide a number,
    only one die will be rolled.  The number you specify is the number
    of sides on this die:
       roll 6

    But you can also run this die many times in one command.  For instance,
    to run 3 six-sided dice at once, you can enter:
        roll 3d6
    In this second example, a 6-sided die will be rolled three times
    and the numbers added to obtain the result.

    """

    args = Command.new_parser()
    group = args.add_group()

    # First branch: one single die.
    one_die = group.add_branch("roll_one_die")
    one_die.add_argument("number")

    # Second branch: several dice (two numbers separated by 'd').
    several_dice = group.add_branch("roll_several_dice")
    several_dice.add_argument("number", dest="times")
    several_dice.add_argument("symbols", "d")
    several_dice.add_argument("number", dest="size")

    def roll_one_die(self, size=6):
        """Roll a single die."""
        self.msg("You want to roll a die a single time?")

    def roll_several_dice(self, times=2, size=6):
        """Roll several dice."""
        self.msg("You want to roll a die several times?")
```

Let's see it in action!  Copy the above code in your `roll.py` file, save it, reload your game and try it:

    > roll 6

    You want to roll a die a single time?

    > roll 3d4

    You want to roll a die several times?

It works!  Well... it selects the right method based on argument syntax, which was the point.  All we need now is to update our methods.  Shouldn't be too hard:

```python
from random import randint

from command import Command


class Roll(Command):

    """Roll a die.
    ...
    """

    args = Command.new_parser()
    group = args.add_group()

    # First branch: one single die.
    one_die = group.add_branch("roll_one_die")
    one_die.add_argument("number")

    # Second branch: several dice (two numbers separated by 'd').
    several_dice = group.add_branch("roll_several_dice")
    several_dice.add_argument("number", dest="times")
    several_dice.add_argument("symbols", "d")
    several_dice.add_argument("number", dest="size")

    def roll_one_die(self, size=6):
        """Roll a single die."""
        number = randint(1, size)
        self.msg(f"You roll a single {size}-sized die... and obtain {number}!")

    def roll_several_dice(self, times=2, size=6):
        """Roll several dice."""
        number = randint(1, times * size)
        self.msg(
            f"You roll a {size}-sized die {times} times... "
            f"and obtain {number}!"
        )
```

## Handling error messages in branches

Our previous example works... but how does it handle error messages?

Let's try to enter an invalid syntax:

    > roll that's not even a number

    Invalid syntax.

That's explicit but not very helpful.  Your players might not be enthusiastic about looking at the help file to see the proper syntax.  You can provide them with a more informative message, by replacing the group's `msg_error` attribute.  Sounds familiar?

```python
class Roll(Command):

    """Roll a die.
    ...
    """

    args = Command.new_parser()
    group = args.add_group()
    group.msg_error = (
        "Specify a number to roll one die or two numbers separated by 'd'."
    )
    # ...
```

You can try it and that's a bit better.  What if you enter roll with no argument?

    > roll

    You have to specify something.

Again, not very informative.  And again, you can change the `msg_mandatory` attribute of our group to make it more explicit.

> Why are the default messages so unhelpful?

Providing "good" error messages on groups is a tricky business.  It would be possible, for instance, to present a quick view of the possible syntax, but it's not necessarily great for players, it might be hard to understand and not very helpful in their context.  Better to have these "generally unehlpful" message that can easily be overridden.

Notice that the `msg_error` will also be displayed if no syntax matches anything:

    > roll -2

    Specify a number to roll one die or two numbers separated by 'd'.

In this case, you might have preferred to have an informative message telling your player the number isn't valid (it should be at least 1).  Again, that's not easy for the parser to determine automatically and it does what it can to provide a helpful error message, but it just cannot always guess.

The same would apply, of course, if you try to add more arguments than necessary:

    > roll 5d10x130

    Specify a number to roll one die or two numbers separated by 'd'.

This time, it makes some sense: the second branch might be chosen (the beginning of the arguments are valid, after all) but the second branch reports to the group that it can't parse the rest of the command, so the group tries another branch.

> What if two branches can match some output?

When the parser encounters two (or more) branches that can parse the given command arguments, it makes a decision on which branch to execute: it selects the "longest", that is, the one with the longer list of arguments.  This might sound arbitrary, but if you examine the cases in which this situation happens, you would see that this decision is actually good:

Let's imagine we have a command with two groups:

1. The only only contains text without any specifics.
2. The second one contains text, the ykeyword "to" and some additional text.

If you try to parse `"what's for dinner ?"`, only the first branch would be valid, because this text doesn't contain `" to"`.  But if you try to parse `"it's time to go"`, then both branches will be valid: the first one would consume the entire text (it's valid), the second one would place `" its time"`  in the first argument and `"go"` in the second.

So the group has to deicde: which to execute?  Both branches are valid.  The group looks at the length of each branch: the first os only 1, the second is 3.  So it chooses the second branch because it can parse more arguments.

## Alternative or cumulative branches

