import json

import pandas as pd
from behave import given, register_type, then, when
from behave.runner import Context
from pcse.base import ParameterProvider

from wofostat import (
	end_of_season_sensitivity_func,
	get_parameter_spec,
	objective_func,
	run_optimisation,
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


@given('we are using "{distance_metric}" as our error metric')
def set_distance_metric(context: Context, distance_metric: str) -> None:
	context.distance_metric = distance_metric


@given('we are using observed data from the "{fpath}" file')
def get_observed_data(context: Context, fpath: str) -> None:
	context.observed_data = pd.read_csv(fpath)


@given('we are using ground truth data from the "{fpath}" file')
def get_ground_truth(context: Context, fpath: str) -> None:
	with open(fpath) as f:
		context.ground_truth = json.load(f)


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


@then(
	'the "{position}" highest "{order}" sensitivity index for "{state_var}" '
	'should be "{param_name}"'
)
def check_sensitivity_index(
	context: Context, position: str, order: str, state_var: str, param_name: str
) -> None:
	index = "".join(c for c in position if c.isdigit())
	index = int(index) - 1

	if order == "total order":
		order = "ST"
	else:
		order = "S1"

	sensitivity_param = context.sp_df[state_var][order].iloc[index].name
	if sensitivity_param != param_name:
		raise RuntimeWarning(f"Parameter is {sensitivity_param}")

	assert sensitivity_param == param_name


@when(
	'we execute an optimisation procedure using the "{method:SnakeCaseString}" method '
	'and the "{engine:SnakeCaseString}" library with "{n_iterations:d}" iterations'
)
def execute_optimisation(
	context: Context, method: str, engine: str, n_iterations: int
) -> None:
	params = _get_params(context)

	(
		context.calibrator,
		context.param_importances,
		context.trials_df,
		context.parameter_estimates,
	) = run_optimisation(
		parameter_spec=context.parameter_spec,
		n_iterations=n_iterations,
		wdp=context.wdp,
		agro=context.agro,
		state_vars=context.state_vars,
		calibration_func=objective_func,
		params=params,
		method=method,
		engine=engine,
		ground_truth=context.ground_truth,
		observed_data=context.observed_data,
		distance_metric=context.distance_metric,
		**context.calibration_spec,
	)
