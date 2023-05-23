"""Helper functions to parse.

Functions:
    parse_all: parse a full sequence of arguments.
    parse_strict_arguments: parse only arguments with a strict space.
    parse_word_arguments: parse only arguments with a word space.
    parse_unknown_arguments: parse all arguments not parsed yet.
    parse_arguments: helper functions to parse any argument.
    create_namespace: create a namespace from a list of results.

"""

from typing import Optional, Sequence, Union, TYPE_CHECKING

from command.args.base import ArgSpace, Argument
from command.args.error import ArgumentError
from command.args.namespace import Namespace
from command.args.result import DefaultResult, Result

if TYPE_CHECKING:
    from data.character import Character


def parse_possibilities(
    possibilities: list[list[Argument]],
    character: "Character",
    string: str,
    begin: int = 0,
    end: Optional[int] = None,
    syntax_error: str = "Invalid syntax.",
) -> ArgumentError | Namespace:
    """Try several possibilities.

    Each possibility is a list of arguments.  This allows to sequencially
    test branches.

    Args:
        possibilities (list lof list of arguments): the arguments to test.
        character (Character): the character parsing the arguments.
        string (str): the string to parse.
        begin (int): the beginning of the string to parse.
        end (int, optional): the end of the string to parse.
        syntax_error (str): message to display if no match occurs.

    Returns:
        result (Namespace or ArgumentError): the parsed result.

    """
    results = [
        parse_all(arguments, character, string, begin, end)
        for arguments in possibilities
    ]
    successes = [result for result in results if isinstance(result, Namespace)]
    if successes:
        lines = zip(results, possibilities)
        lines = [tup for tup in lines if tup[0]]
        result, _ = max(
            lines, key=lambda tup: len([a for a in tup[1] if not a.optional])
        )
    else:
        result = ArgumentError(syntax_error)

    return result


def parse_all(
    arguments: Sequence[Argument],
    character: "Character",
    string: str,
    begin: int = 0,
    end: Optional[int] = None,
    syntax_error: str = "Invalid syntax.",
) -> Union[ArgumentError, Namespace]:
    """Parse a string, returning a namespace or error.

    Args:
        arguments (Sequence of Argument): the list of arguments to parse.
        string (str): the string to parse.
        begin (int): the beginning of the string to parse.
        end (int, optional): the end of the string to parse.
        syntax_error (str): message to display if no match occurs.

    Returns:
        result (Namespace or ArgumentError): the parsed result.

    """
    results = [None] * len(arguments)

    # Parse arguments with definite size.
    results = parse_strict_arguments(
        arguments, results, character, string, begin, end
    )
    results = parse_word_arguments(
        arguments, results, character, string, begin, end
    )

    # Now parse the remiaining ones.
    results = parse_unknown_arguments(
        arguments, results, character, string, begin, end
    )

    # If an error has occurred, return the first
    # mandatory argument error.
    errors = [result for result in results if not result]
    if errors:
        mandatory = [
            result
            for result in errors
            if not arguments[results.index(result)].optional
        ]
        if mandatory:
            return mandatory[0]

    # Check that the string has been entirely parsed.
    if not has_entirely_parsed(results, string, begin, end):
        return ArgumentError(syntax_error)

    # Create the namespace.
    namespace = create_namespace(arguments, results)
    return namespace


def parse_strict_arguments(
    arguments: Sequence[Argument],
    results: Sequence[Result],
    character: "Character",
    string: str,
    begin: int,
    end: Optional[int] = None,
) -> Sequence[Result]:
    """Parse the arguments with a space of strict.

    Args:
        arguments (sequence of Argument): the arguments.
        results (Sequence of Result): the already-parsed results.
        character (Character): the character parsing these arguments.
        string (str): the string to parse.
        begin (int): the beginning of the string to parse.
        end (int, optional): the end of the string to parse.

    Returns:
        results (sequence of Result): the parsed results (same length).

    Warning: the length of arguments and results should be equal.

    """
    arguments = [
        arg if arg.space is ArgSpace.STRICT else None for arg in arguments
    ]
    return parse_arguments(arguments, results, character, string, begin, end)


def parse_word_arguments(
    arguments: Sequence[Argument],
    results: Sequence[Result],
    character: "Character",
    string: str,
    begin: int,
    end: Optional[int] = None,
) -> Sequence[Result]:
    """Parse the arguments with a space of word.

    Args:
        arguments (sequence of Argument): the arguments.
        results (Sequence of Result): the already-parsed results.
        character (Character): the character parsing these arguments.
        string (str): the string to parse.
        begin (int): the beginning of the string to parse.
        end (int, optional): the end of the string to parse.

    Returns:
        results (sequence of Result): the parsed results (same length).

    Warning: the length of arguments and results should be equal.

    """
    arguments = [
        arg if arg.space is ArgSpace.WORD else None for arg in arguments
    ]
    return parse_arguments(arguments, results, character, string, begin, end)


def parse_unknown_arguments(
    arguments: Sequence[Argument],
    results: Sequence[Result],
    character: "Character",
    string: str,
    begin: int,
    end: Optional[int] = None,
) -> Sequence[Result]:
    """Parse the arguments with no clear limit.

    Args:
        arguments (sequence of Argument): the arguments.
        results (Sequence of Result): the already-parsed results.
        character (Character): the character parsing these arguments.
        string (str): the string to parse.
        begin (int): the beginning of the string to parse.
        end (int, optional): the end of the string to parse.

    Returns:
        results (sequence of Result): the parsed results (same length).

    Warning: the length of arguments and results should be equal.

    """
    return parse_arguments(arguments, results, character, string, begin, end)


def parse_arguments(
    arguments: Sequence[Optional[Argument]],
    results: Sequence[Result],
    character: "Character",
    string: str,
    begin: int,
    end: Optional[int] = None,
) -> Sequence[Result]:
    """Only parse the provided arguments.

    Args:
        arguments (sequence of Argument and None): the arguments.
        results (Sequence of Result): the already-parsed results.
        character (Character): the character parsing these arguments.
        string (str): the string to parse.
        begin (int): the beginning of the string to parse.
        end (int, optional): the end of the string to parse.

    Returns:
        results (Sequence of Result): the parsed results (same length).

    Warning: the length of arguments and results should be equal.

    """
    results = list(results)
    end = len(string) if end is None else end
    for i, arg in enumerate(arguments):
        if arg is None:
            continue

        if results[i] is not None:
            continue

        # If there's a previous result, parse after it.
        t_begin = begin
        if i > 0:
            prev_results = [result for result in results[:i] if result]
            if prev_results:
                prev_result = prev_results[-1]
                t_begin = prev_result.end

        # Skip over spaces.
        while t_begin < len(string):
            if string[t_begin].isspace():
                t_begin += 1
            else:
                break

        # If there's a following result, parse before it.
        t_end = end
        if i < len(arguments) - 1:
            next_results = [result for result in results[i + 1 :] if result]
            if next_results:
                next_result = next_results[0]
                t_end = next_result.begin

        # Skip over spaces.
        while t_end - 1 > t_begin:
            if string[t_end - 1].isspace():
                t_end -= 1
            else:
                break

        if t_begin >= t_end and not arg.optional:
            results[i] = ArgumentError(
                arg.msg_mandatory.format(argument=arg.name)
            )
            break

        result = arg.parse(character, string, t_begin, t_end)
        if not result:
            if arg.optional and arg.has_default:
                result = DefaultResult(arg.default)

        results[i] = result

    return results


def has_entirely_parsed(
    results: Sequence[Result],
    string: str,
    begin: int,
    end: Optional[int] = None,
) -> bool:
    """Return whether the string has been entirely parsed.

    Args:
        results (sequence): the list of parsed results.
        string (str): the parsed string.
        begin (int): the beginnning of the parsed string.
        end (int, optional): the end of the parsed string.

    Returns:
        parsed (bool): whether the string has entirely been parsed ot not.

    """
    if begin is None:
        begin = 0
    if end is None:
        end = len(string)

    indices = list(range(begin, end))
    for result in results:
        if not result:
            continue

        r_begin = result.begin
        r_end = result.end
        r_begin = 0 if r_begin is None else r_begin
        r_end = len(string) if r_end is None else r_end
        for i in range(r_begin, r_end):
            if i in indices:
                indices.remove(i)

    # Remove spaces in unprocessed indices.
    for i in tuple(indices):
        if string[i].isspace():
            indices.remove(i)

    if indices:
        return False

    return True


def create_namespace(
    arguments: Sequence[Argument], results: Sequence[Result]
) -> Namespace:
    """Create a namespace according to the given results and arguments.

    Args:
        arguments (sequence of Argument: the arguments.
        results (sequence of Result): the parsed results.

    WARNING: both sequences should have the same length.

    Returns:
        namespace (amespace): the parsed namespace.

    """
    namespace = Namespace()
    methods = set()
    for arg, result in zip(arguments, results):
        methods.add(getattr(arg, "run_in", "run"))
        if isinstance(result, DefaultResult):
            value = result.value
        elif not isinstance(result, Result):
            continue
        else:
            value = result.portion

        custom = getattr(arg, "add_to_namespace", None)
        if custom:
            custom(result, namespace)
        else:
            setattr(namespace, arg.dest, value)

    methods.discard("run")
    if len(methods) > 1:
        raise ValueError(
            f"ambiguous method to execute: possibilities are {methods}"
        )
    elif methods:
        setattr(namespace, "_run_in", methods.pop())

    return namespace
