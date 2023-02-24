from command.args import CommandArgs


def test_alternative_branch_with_different_syntax_valid():
    """Create an argument parser with two alternative branches."""
    args = CommandArgs()
    group = args.add_group()
    branch1 = group.add_branch("1")
    branch1.add_argument("number", dest="unique")
    branch2 = group.add_branch("2")
    branch2.add_argument("number", dest="first")
    branch2.add_argument("symbols", "|")
    branch2.add_argument("number", dest="second")

    # Try branch1 (valid).
    result = args.parse(None, "152")
    assert bool(result)
    assert result._run_in == "1"
    assert result.unique == 152

    # Try branch2 (valid).
    result = args.parse(None, "15|12")
    assert bool(result)
    assert result._run_in == "2"
    assert result.first == 15
    assert result.second == 12


def test_alternative_branch_with_different_syntax_error():
    """Create an argument parser with two alternative branches."""
    args = CommandArgs()
    group = args.add_group()
    branch1 = group.add_branch("1")
    branch1.add_argument("number", dest="unique")
    branch2 = group.add_branch("2")
    branch2.add_argument("number", dest="first")
    branch2.add_argument("keyword", "for")
    branch2.add_argument("number", dest="second")

    # Try to parse one invalid argument.
    result = args.parse(None, "nt any number")
    assert not bool(result)

    # Try to parse branch2 with additional info.
    result = args.parse(None, "1 for 2p")
    assert not bool(result)
