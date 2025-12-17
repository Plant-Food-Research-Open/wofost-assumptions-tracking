"""Contains functions and utilities for performing model calibration.

Perform calibration and sensitivity analysis on the WOFOST 7.2 model.
"""

from collections.abc import Callable

import numpy as np
import pandas as pd
from calisim.data_model import (
	DistributionModel,
	ParameterDataType,
	ParameterSpecification,
)
from calisim.sensitivity import (
	SensitivityAnalysisMethod,
	SensitivityAnalysisMethodModel,
)
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
) -> tuple[SensitivityAnalysisMethod, list[pd.DataFrame]]:
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

	Returns:
	    tuple[SensitivityAnalysisMethod, list[pd.DataFrame]]: The sensitivity analysis
		workflow and sensitivity indices.
	"""
	specification = SensitivityAnalysisMethodModel(
		experiment_name=experiment_name,
		parameter_spec=parameter_spec,
		method="sobol",
		n_samples=n_samples,
		n_jobs=n_jobs,
		output_labels=state_vars,
		verbose=True,
		batched=False,
		method_kwargs=dict(calc_second_order=False, scramble=True),
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
		calibration_func=calibration_func, specification=specification, engine="salib"
	)

	calibrator.specify().execute()

	return calibrator, calibrator.implementation.sp.to_df()
