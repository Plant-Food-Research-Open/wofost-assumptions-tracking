from behave import given, register_type, when
from behave.runner import Context
from pcse.base import ParameterProvider

from wofostat import (
	end_of_season_sensitivity_func,
	get_parameter_spec,
	run_sensitivity_analysis,
	snake_case_string,
)
from wofostat.wofost import WOFOST

register_type(SnakeCaseString=snake_case_string)


@given("the following parameter specification is used for calibration:")
def specify_parameters(context: Context) -> None:
	context.parameter_spec = get_parameter_spec(context.table)


@given("the following specification is used for the calibration procedure:")
def specify_calibration(context: Context) -> None:
	context.calibration_spec = {row["name"]: row["value"] for row in context.table}


def _get_params(context: Context) -> ParameterProvider:
	params = WOFOST.get_params(
		cropd=context.cropd, sited=context.sited, soild=context.soild
	)
	WOFOST(params, context.wdp, context.agro)
	return params


@when(
	'we execute a sensitivity analysis using the "{method:SnakeCaseString}" method and '
	'the "{engine:SnakeCaseString}" library with "{n_samples:d}" samples'
)
def execute_sensitivity(
	context: Context, method: str, engine: str, n_samples: int
) -> None:
	params = _get_params(context)

	context.calibrator, context.sp_df = run_sensitivity_analysis(
		parameter_spec=context.parameter_spec,
		n_samples=n_samples,
		wdp=context.wdp,
		agro=context.agro,
		state_vars=context.state_vars,
		calibration_func=end_of_season_sensitivity_func,
		params=params,
		method=method,
		engine=engine,
		**context.calibration_spec,
	)
