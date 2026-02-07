"""Utilities and static methods for running a WOFOST simulation.

Makes use of the WOFOST 7.2 model with potential production scenarios.
"""

import copy
import datetime as dt

import pandas as pd
import requests  # type: ignore[import-untyped]
from pcse.base import ParameterProvider
from pcse.exceptions import PCSEError
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


def _query_NASAPower_server(
	self: NASAPowerWeatherDataProvider, latitude: float, longitude: float
) -> dict:
	"""Query the NASA Power server for data on given latitude/longitude"""

	start_date = dt.date(1983, 7, 1)
	end_date = dt.date.today()

	# build URL for retrieving data, using new NASA POWER api
	server = "https://power.larc.nasa.gov/api/temporal/daily/point"
	payload = {
		"request": "execute",
		"parameters": ",".join(self.power_variables),
		"latitude": latitude,
		"longitude": longitude,
		"start": start_date.strftime("%Y%m%d"),
		"end": end_date.strftime("%Y%m%d"),
		"community": "AG",
		"format": "JSON",
		"user": "pcse",
	}

	msg = "Starting retrieval from NASA Power"
	self.logger.debug(msg)
	req = requests.get(server, params=payload)

	if req.status_code != self.HTTP_OK:
		msg = (
			"Failed retrieving POWER data, server returned HTTP "
			+ "code: %i on following URL %s"
		) % (req.status_code, req.url)
		raise PCSEError(msg)

	msg = "Successfully retrieved data from NASA Power"
	self.logger.debug(msg)
	return req.json()


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
	def get_sited(WAV: float) -> WOFOST72SiteDataProvider:
		"""Get WOFOST site data provider.

		Args:
			WAV (float): Initial available water in total rootable zone.

		Returns:
			WOFOST72SiteDataProvider: The WOFOST site data provider.
		"""
		sited = WOFOST72SiteDataProvider(WAV=WAV)
		return sited

	@staticmethod
	def get_soild() -> DummySoilDataProvider:
		"""Get soil data provider.

		Returns:
			DummySoilDataProvider: The soil data provider.
		"""
		soild = DummySoilDataProvider()
		return soild

	@staticmethod
	def get_wdp(latitude: float, longitude: float) -> NASAPowerWeatherDataProvider:
		"""Get NASA weather data provider.

		Args:
			latitude (float): The weather data latitude.
			longitude (float): The weather data longitude.

		Returns:
			NASAPowerWeatherDataProvider: The NASA weather data provider.
		"""
		NASAPowerWeatherDataProvider._query_NASAPower_server = _query_NASAPower_server
		wdp = NASAPowerWeatherDataProvider(latitude=latitude, longitude=longitude)
		return wdp

	@staticmethod
	def get_cropd(fpath: str) -> YAMLCropDataProvider:
		"""Get the crop data provider.

		Args:
			fpath (str): The data file path.

		Returns:
			YAMLCropDataProvider: The crop data provider.
		"""
		cropd = YAMLCropDataProvider(fpath=fpath, force_reload=True)
		return cropd

	@staticmethod
	def get_agro(fpath: str) -> YAMLAgroManagementReader:
		"""Get the agronomy management reader.

		Args:
			fpath (str): The data file path.

		Returns:
			YAMLAgroManagementReader: The agronomy management reader.
		"""
		agro = YAMLAgroManagementReader(fpath)
		return agro

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
