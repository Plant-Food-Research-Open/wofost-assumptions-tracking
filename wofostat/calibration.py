"""Contains functions and utilities for performing model calibration.

Perform calibration and sensitivity analysis on the WOFOST 7.2 model.
"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
from calisim.data_model import (
	DistributionModel,
	ParameterDataType,
	ParameterSpecification,
)
from calisim.optimisation import OptimisationMethod, OptimisationMethodModel
from calisim.sensitivity import (
	SensitivityAnalysisMethod,
	SensitivityAnalysisMethodModel,
)
from calisim.statistics import get_distance_metric_func
from optuna.importance import get_param_importances
from pcse.base import ParameterProvider
from pcse.input import NASAPowerWeatherDataProvider, YAMLAgroManagementReader

from .wofost import WOFOST


def get_parameter_spec(data_table: list[dict]) -> ParameterSpecification:
	"""Get the calibration parameter specification.

	Args:
	    data_table (list[dict]): The table of the parameter specification.

	Returns:
	    ParameterSpecification: The calibration parameter specification.
	"""
	parameters = []
	for row in data_table:
		parameters.append(
			DistributionModel(
				name=row["name"],
				distribution_name=row["distribution"],
				distribution_args=[float(x.strip()) for x in row["range"].split(",")],
				data_type=ParameterDataType(row["type"]),
			)
		)

	parameter_spec = ParameterSpecification(parameters=parameters)
	return parameter_spec


def table_to_dict(data_table: list[dict]) -> dict[str, float]:
	"""Convert a data table to a dictionary object.

	Args:
	    data_table (list[dict]): The data table.

	Returns:
	    dict[str, float]: The dictionary object.
	"""
	parameters = {}
	for row in data_table:
		parameters[row["name"]] = row["value"]

	return parameters


def end_of_season_sensitivity_func(
	parameters: dict,
	simulation_id: str,
	observed_data: np.ndarray | None,
	wdp: NASAPowerWeatherDataProvider,
	agro: YAMLAgroManagementReader,
	params: ParameterProvider,
	state_vars: list[str],
) -> float | list[float]:
	"""The end of season sensitivity analysis function.

	Args:
	    parameters (dict): The dictionary of parameter names and values.
	    simulation_id (str): The individual simulation ID.
	    observed_data (np.ndarray | None): The observed data for calibration.
	    wdp (NASAPowerWeatherDataProvider): The weather data provider.
	    agro (YAMLAgroManagementReader): The agro management reader.
	    params (ParameterProvider): The simulation parameter provider.
	    state_vars (list[str]): The list of state variable names.

	Returns:
	    float | list[float]: The simulation results.
	"""
	p = WOFOST.copy(params)
	p = WOFOST.override(parameters, p)
	wofost = WOFOST(p, wdp, agro)

	simulated_data = wofost.run()
	end_of_season = simulated_data.tail(1)
	return end_of_season[state_vars].values.flatten()


def run_sensitivity_analysis(
	experiment_name: str,
	parameter_spec: ParameterSpecification,
	n_samples: int,
	wdp: NASAPowerWeatherDataProvider,
	agro: YAMLAgroManagementReader,
	state_vars: list[str],
	calibration_func: Callable,
	params: ParameterProvider,
	n_jobs: int = 1,
	method: str = "sobol",
	engine: str = "salib",
	random_seed: int | None = None,
) -> tuple[SensitivityAnalysisMethod, dict[str, dict[str, pd.DataFrame]]]:
	"""Run a sensitivity analysis.

	Args:
	    experiment_name (str): The experiment name.
	    parameter_spec (ParameterSpecification): The calibration specification.
	    n_samples (int): The number of Sobol samples.
	    wdp (NASAPowerWeatherDataProvider): The weather data provider.
	    agro (YAMLAgroManagementReader): The agro management reader.
	    state_vars (list[str]): The list of state variable names.
	    calibration_func (Callable): The calibration function.
	    params (ParameterProvider): The simulation parameter provider.
	    n_jobs (int, optional): Number of simulations to run in parallel. Defaults to 1.
		method (str, optional): The calibration method.
		engine (str, optional): The underlying calibration library.
		random_seed (int, optional): The random seed for replicability.

	Returns:
	    tuple[SensitivityAnalysisMethod, dict[str, dict[str, pd.DataFrame]]]]: The
		sensitivity analysis workflow and sensitivity indices.
	"""
	specification = SensitivityAnalysisMethodModel(
		experiment_name=experiment_name,
		parameter_spec=parameter_spec,
		method=method,
		n_samples=n_samples,
		n_jobs=n_jobs,
		output_labels=state_vars,
		verbose=True,
		batched=False,
		method_kwargs=dict(calc_second_order=False, scramble=True),
		random_seed=random_seed,
		analyze_kwargs=dict(
			calc_second_order=False,
			num_resamples=200,
			conf_level=0.95,
		),
		calibration_func_kwargs=dict(
			wdp=wdp, agro=agro, state_vars=state_vars, params=params
		),
	)

	calibrator = SensitivityAnalysisMethod(
		calibration_func=calibration_func, specification=specification, engine=engine
	)

	calibrator.specify().execute()

	sp_df = calibrator.implementation.sp.to_df()
	sp = {}
	for i, state_var in enumerate(state_vars):
		sp[state_var] = {
			"ST": sp_df[i][0].sort_values("ST", ascending=False),
			"S1": sp_df[i][1].sort_values("S1", ascending=False),
		}

	return calibrator, sp


def objective_func(
	parameters: dict,
	simulation_id: str,
	observed_data: pd.DataFrame | np.ndarray | None,
	wdp: NASAPowerWeatherDataProvider,
	agro: list[dict],
	params: ParameterProvider,
	distance_metric: str,
	state_vars: list[str],
) -> float | list[float]:
	"""The optimisation objective function for calibration.

	Args:
	    parameters (dict): The dictionary of parameter names and values.
	    simulation_id (str): The individual simulation ID.
	    observed_data (pd.DataFrame | np.ndarray | None): Observed data for calibration.
	    wdp (NASAPowerWeatherDataProvider): The weather data provider.
	    agro (YAMLAgroManagementReader): The agro management reader.
	    params (ParameterProvider): The simulation parameter provider.
	    distance_metric (str): The distance metric to derive the discrepancy.
	    state_vars (list[str]): The list of state variable names.

	Returns:
	    float | list[float]: The objective.
	"""
	p = WOFOST.copy(params)
	p = WOFOST.override(parameters, p)
	wofost = WOFOST(p, wdp, agro)
	simulated_data: pd.DataFrame = wofost.run()

	metric = get_distance_metric_func(distance_metric)()
	discrepancy = []
	for state_var in state_vars:
		simulated = simulated_data[state_var].values
		observed = observed_data[state_var].values  # type: ignore[index]

		if len(simulated) < len(observed):
			simulated = np.pad(
				simulated, (0, len(observed) - len(simulated)), mode="constant"
			)

		discrepancy.append(metric.calculate(observed, simulated))

	return discrepancy


def run_optimisation(
	experiment_name: str,
	parameter_spec: ParameterSpecification,
	n_iterations: int,
	wdp: NASAPowerWeatherDataProvider,
	agro: YAMLAgroManagementReader,
	state_vars: list[str],
	calibration_func: Callable,
	params: ParameterProvider,
	ground_truth: dict[str, float],
	observed_data: np.ndarray | None,
	distance_metric: str = "mean squared error",
	n_jobs: int = 1,
	method: str = "tpes",
	engine: str = "optuna",
	random_seed: int | None = None,
) -> tuple[OptimisationMethod, dict[str, dict[Any, Any]], pd.DataFrame, pd.DataFrame]:
	"""Run an optimisation procedure.

	Args:
	    experiment_name (str): The experiment name.
	    parameter_spec (ParameterSpecification): The calibration specification.
	    n_iterations (int): The number of optimisation trials.
	    wdp (NASAPowerWeatherDataProvider): The weather data provider.
	    agro (YAMLAgroManagementReader): The agro management reader.
	    state_vars (list[str]): The list of state variable names.
	    calibration_func (Callable): The calibration function.
	    params (ParameterProvider): The simulation parameter provider.
	    ground_truth (dict[str, float]): The simulation study ground truth.
	    observed_data (np.ndarray | None): The observed data for calibration.
	    distance_metric (str, optional): The distance metric function
	    for the discrepancy. Defaults to "mean squared error".
	    n_jobs (int, optional): Number of simulations to run in parallel. Defaults to 1.
		method (str, optional): The calibration method.
		engine (str, optional): The underlying calibration library.
		random_seed (int, optional): The random seed for replicability.

	Returns:
	    tuple[OptimisationMethod, dict[str, dict[Any, Any]],
		pd.DataFrame, pd.DataFrame]: The optimisation workflow,
		parameter importances, trial history, and parameter estimates.
	"""
	directions = ["minimize" for _ in state_vars]

	specification = OptimisationMethodModel(
		experiment_name=experiment_name,
		parameter_spec=parameter_spec,
		observed_data=observed_data,
		method=method,
		output_labels=state_vars,
		directions=directions,
		n_jobs=n_jobs,
		n_iterations=n_iterations,
		random_seed=random_seed,
		calibration_func_kwargs=dict(
			wdp=wdp,
			agro=agro,
			distance_metric=distance_metric,
			state_vars=state_vars,
			params=params,
		),
	)

	calibrator = OptimisationMethod(
		calibration_func=calibration_func, specification=specification, engine=engine
	)

	calibrator.specify().execute()

	param_importances = {}
	for i, state_var in enumerate(state_vars):
		importances = get_param_importances(
			calibrator.implementation.study, target=lambda t: t.values[i]
		)
		param_importances[state_var] = dict(
			sorted(importances.items(), key=lambda x: x[1], reverse=True)
		)

	renamed_columns = {}
	for i, state_var in enumerate(state_vars):
		renamed_columns[f"values_{i}"] = state_var
	trials_df = (
		calibrator.implementation.study.trials_dataframe()
		.rename(columns=renamed_columns)
		.sort_values(state_vars)
	)

	ground_truth_df = pd.DataFrame(
		dict(name=list(ground_truth.keys()), true=list(ground_truth.values()))
	)
	top_estimate = trials_df.head(1).to_dict("records")[0]
	estimates = []
	for k in ground_truth.keys():
		estimates.append({"name": k, "estimate": top_estimate[f"params_{k}"]})
	parameter_estimates: pd.DataFrame = ground_truth_df.merge(pd.DataFrame(estimates))

	return calibrator, param_importances, trials_df, parameter_estimates
