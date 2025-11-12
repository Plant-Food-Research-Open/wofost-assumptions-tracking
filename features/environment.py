from behave.model import Feature, Scenario
from behave.runner import Context

def before_feature(context: Context, feature: Feature) -> None:
    pass

def after_feature(context: Context, feature: Feature) -> None:
    pass

def before_scenario(context: Context, scenario: Scenario) -> None:
    pass

def after_scenario(context: Context, scenario: Scenario) -> None:
    pass
