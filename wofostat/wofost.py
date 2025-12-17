"""Utilities and static methods for running a WOFOST simulation.

Makes use of the WOFOST 7.2 model with potential production scenarios.
"""

import copy

import pandas as pd
from pcse.base import ParameterProvider
from pcse.input import (
	DummySoilDataProvider,
	NASAPowerWeatherDataProvider,
	WOFOST72SiteDataProvider,
	YAMLAgroManagementReader,
	YAMLCropDataProvider,
)
from pcse.models import Wofost72_PP

DEFAULT_PARAMETER_VALUES = dict(
	TSUM1=255,
	TSUM2=1400,
	TBASEM=3.0,
	TSUMEM=170.0,
	TEFFMX=18.0,
	SPAN=37,
	TDWI=75,
	RGRLAI=0.016,
	Q10=2.0,
)


class WOFOST:
	"""WOFOST 7.2 simulation model."""

	def __init__(
		self,
		params: ParameterProvider,
		wdp: NASAPowerWeatherDataProvider,
		agro: YAMLAgroManagementReader,
	) -> None:
		self.instance = Wofost72_PP(params, wdp, agro)
		self.results: pd.DataFrame | None = None

	@staticmethod
	def get_params(
		cropd: YAMLCropDataProvider,
		sited: WOFOST72SiteDataProvider,
		soild: DummySoilDataProvider | None = None,
	) -> ParameterProvider:
		"""Instantiate a new simulation parameter provider.

		Args:
			cropd (YAMLCropDataProvider): The crop data provider.
			sited (WOFOST72SiteDataProvider): The side data provider.
			soild (DummySoilDataProvider | None, optional): The soil data provider.
			Defaults to None.

		Returns:
			ParameterProvider: The simulation parameter provider.
		"""
		if soild is None:
			soild = DummySoilDataProvider()

		params = ParameterProvider(cropdata=cropd, sitedata=sited, soildata=soild)
		return params

	@staticmethod
	def copy(params: ParameterProvider) -> ParameterProvider:
		"""Deep copy the simulation parameters.

		Args:
			params (ParameterProvider): The simulation parameter provider.

		Returns:
			ParameterProvider: The copied simulation parameters.
		"""
		p = copy.deepcopy(params)
		return p

	@staticmethod
	def override(parameters: dict, params: ParameterProvider) -> ParameterProvider:
		"""Override the simulation parameters.

		Args:
			parameters (dict): The parameter names and values.
			params (ParameterProvider): The simulation parameter provider.

		Returns:
			ParameterProvider: The overridden simulation parameter provider.
		"""
		for k in parameters:
			params.set_override(k, parameters[k])
		return params

	def run(self) -> pd.DataFrame:
		"""Run the simulation until completion.

		Returns:
			pd.DataFrame: The simulation results.
		"""
		self.instance.run_till_terminate()
		self.results = pd.DataFrame(self.instance.get_output())
		return self.results
