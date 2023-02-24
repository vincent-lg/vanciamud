from behave import given, then
from hamcrest import assert_that, equal_to

from data.account import Account


@given("an exiting account with the '{username}' username")
def step_impl(context, username):
    account = Account.create(username=username, hashed_password=b"")
    context.account = account


@then("no account is linked to this session")
def step_impl(context):
    account = context.session.db.get("account")
    assert_that(account, equal_to(None))


@then("the account of username '{username}' is linked to this session")
def step_impl(context, username):
    account = context.session.db.get("account")
    assert_that(account.username, equal_to(username))
