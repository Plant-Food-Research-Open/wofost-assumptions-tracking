from behave import given, then, when
from behave.runner import Context


@given("we have behave installed")
def behave_installed(context: Context) -> None:
	pass


@when("we implement a test")
def implement_test(context: Context) -> None:
	assert True is not False


@then("behave will test it for us!")
def test_for_us(context: Context) -> None:
	assert context.failed is False
