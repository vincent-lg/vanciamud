from command.args import CommandArgs


def test_one_correct_number():
    """Test to parse a command with one number."""
    args = CommandArgs()
    args.add_argument("number")
    result = args.parse(None, "52")
    assert bool(result)
    assert result.number == 52


def test_one_incorrect_number():
    """Test to parse a command with one number."""
    args = CommandArgs()
    args.add_argument("number")
    result = args.parse(None, "not a number")
    assert not bool(result)


def test_one_invalid_number():
    """Test to parse a command with one number."""
    args = CommandArgs()
    args.add_argument("number")
    result = args.parse(None, "-3")
    assert not bool(result)


def test_one_min_limited_correct_number():
    """Parse a limited number."""
    args = CommandArgs()
    number = args.add_argument("number")
    number.min_limit = -5
    result = args.parse(None, "-3")
    assert bool(result)
    assert result.number == -3


def test_one_min_limited_incorrect_number():
    """Parse a limited number."""
    args = CommandArgs()
    number = args.add_argument("number")
    number.min_limit = -5
    result = args.parse(None, "-6")
    assert not bool(result)


def test_one_no_min_limit_correct_number():
    """Parse a limited number."""
    args = CommandArgs()
    number = args.add_argument("number")
    number.min_limit = None
    result = args.parse(None, "-120")
    assert bool(result)
    assert result.number == -120


def test_one_max_limited_correct_number():
    """Parse a limited number."""
    args = CommandArgs()
    number = args.add_argument("number")
    number.max_limit = 5
    result = args.parse(None, "4")
    assert bool(result)
    assert result.number == 4


def test_one_max_limited_incorrect_number():
    """Parse a limited number."""
    args = CommandArgs()
    number = args.add_argument("number")
    number.max_limit = 5
    result = args.parse(None, "6")
    assert not bool(result)


def test_one_no_min_limit_correct_number():
    """Parse a limited number."""
    args = CommandArgs()
    number = args.add_argument("number")
    number.max_limit = None
    result = args.parse(None, "120")
    assert bool(result)
    assert result.number == 120


def test_two_mandatory_numbers_valid():
    """Parse a command with two numbers separated by space."""
    args = CommandArgs()
    args.add_argument("number", dest="first")
    args.add_argument("number", dest="second")
    result = args.parse(None, "5 2")
    assert bool(result)
    assert result.first == 5
    assert result.second == 2


def test_two_mandatory_numbers_error():
    """Parse a command with one number, but expect two."""
    # Parse one number but expect two.
    args = CommandArgs()
    args.add_argument("number", dest="first")
    args.add_argument("number", dest="second")
    result = args.parse(None, "5")
    assert not bool(result)

    # Parse three numbers but expect two.
    result = args.parse(None, "1 2 3")
    assert not bool(result)


def test_two_mandatory_numbers_separated_by_symbol_valid():
    """Parse a command with two numbers separated by a symbol."""
    args = CommandArgs()
    args.add_argument("number", dest="first")
    args.add_argument("symbols", "|")
    args.add_argument("number", dest="second")
    result = args.parse(None, "5|2")
    assert bool(result)
    assert result.first == 5
    assert result.second == 2

    # Put spaces before/after the separator.
    result = args.parse(None, "5 | 2")
    assert bool(result)
    assert result.first == 5
    assert result.second == 2


def test_two_mandatory_numbers_separated_by_symbols_error():
    """Parse a command with one number, but expect two."""
    # Parse one number but expect two.
    args = CommandArgs()
    args.add_argument("number", dest="first")
    args.add_argument("symbols", "|")
    args.add_argument("number", dest="second")
    result = args.parse(None, "5")
    assert not bool(result)

    # Parse three numbers but expect two.
    result = args.parse(None, "1|2|3")
    assert not bool(result)
