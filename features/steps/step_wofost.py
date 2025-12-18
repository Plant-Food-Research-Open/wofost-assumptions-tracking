from behave import given, then, when
from behave.runner import Context

from wofostat.wofost import WOFOST


@given('we are using WOFOST site data with a WAV of "{WAV:f}"')
def get_sited(context: Context, WAV: float) -> None:
	context.sited = WOFOST.get_sited(WAV)


@given("we are using default soil parameter values")
def get_soild(context: Context) -> None:
	context.soild = WOFOST.get_soild()


@given('we are using crop data stored in the "{fpath}" directory')
def get_cropd(context: Context, fpath: str) -> None:
	context.cropd = WOFOST.get_cropd(fpath)


@given('we are using agronomy management data in the "{fpath}" file')
def get_agro(context: Context, fpath: str) -> None:
	context.agro = WOFOST.get_agro(fpath)


@given('our state variables are "{state_vars}"')
def set_state_variables(context: Context, state_vars: str) -> None:
	context.state_vars = (
		state_vars.replace(", and", ",")
		.replace(" and ", ",")
		.replace(" ", "")
		.split(",")
	)


@given(
	'we are using NASA weather data with a latitude of "{latitude:d}" '
	'and a longitude of "{longitude:d}"'
)
def get_wdp(context: Context, latitude: float, longitude: float) -> None:
	context.wdp = WOFOST.get_wdp(latitude, longitude)


@given("we have behave installed")
def behave_installed(context: Context) -> None:
	pass


@when("we implement a test")
def implement_test(context: Context) -> None:
	assert True is not False


@then("behave will test it for us!")
def test_for_us(context: Context) -> None:
	assert context.failed is False
