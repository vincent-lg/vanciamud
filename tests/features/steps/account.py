from behave import given, then
from hamcrest import assert_that, equal_to, none, not_none

from data.account import Account
from data.character import Character


@given(
    "an account with the username '{username}' "
    "and password '{password}' and {characters:d} characters"
)
def step_impl(context, username, password, characters):
    account = _create_account(username, password)

    for _ in range(characters):
        account.characters.append(Character.create(account=account))

    context.account = account


@given(
    "an account with the username '{username}' "
    "and password '{password}'"
)
def step_impl(context, username, password):
    account = _create_account(username, password)
    context.account = account


@given("an account with the username '{username}'")
def step_impl(context, username):
    account = _create_account(username, "")
    context.account = account


@then("no account is linked to this session")
def step_impl(context):
    account = context.session.db.get("account")
    assert_that(account, none())


@then("the account of username '{username}' is linked to this session")
def step_impl(context, username):
    account = context.session.db.get("account")
    assert_that(account.username, equal_to(username))


@then(
    "an account exists with username '{username}' "
    "and password '{password}' and email '{email}'"
)
def step_impl(context, username, password, email):
    _assert_account(username, password, email)


@then(
    "an account exists with username '{username}' "
    "and password '{password}' and no email"
)
def step_impl(context, username, password):
    _assert_account(username, password)


def _create_account(username: str, plain_password: str) -> Account:
    hashed = Account.hash_password(plain_password)
    account = Account.create(username=username, hashed_password=hashed)
    return account


def _assert_account(
    username: str,
    plain_password: str,
    email: str | None = None
) -> Account:
    account = Account.get(username=username.lower(), raise_not_found=False)
    assert_that(account, not_none())
    assert_that(
        Account.test_password(account.hashed_password, plain_password),
        equal_to(True)
    )

    if email is None:
        assert_that(account.email, none())
    else:
        assert_that(account.email, equal_to(email))
