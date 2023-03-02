from uuid import uuid4

from behave import given, when, then
from hamcrest import assert_that, equal_to

from data.session import Session

@given("a session on the '{path}' context")
def step_impl(context, path):
    session = Session.create(
        uuid=uuid4(), context_path=path, ip_address="127.0.0.1", secured=False
    )
    context.session = session


@when("the user inputs '{user_input}'")
def step_impl(context, user_input):
    context.session.context.handle_input(user_input)


@then("the session is on the '{path}' context")
def step_impl(context, path):
    assert_that(context.session.context_path, equal_to(path))
