Feature: Calibration of WOFOST potato using black-box optimisation
    Because potato crop model parameters are uncertain
    We want to calibrate WOFOST by exploring the parameter space with black-box optimisation
    And minimising the discrepancy for end-of-season LAI and TWSO
    So potato crop development and growth is both accurate and well-constrained

    Background:
        Given we are using WOFOST site data with a WAV of "50.0"
        And we are using default soil parameter values
        And we are using crop data stored in the "data" directory
        And our state variables are "LAI and TWSO"
        And we are using "mean squared error" as our error metric
        And we are using observed data from the "data/synthetic_test_data.csv" file
        And we are using ground truth data from the "data/ground_truth.json" file
        And the following parameter specification is used for calibration:
            | name   | description                                                   | range       | distribution | type       |
            | TSUM1  | Temperature sum from emergence to anthesis                    | 150, 280    | uniform      | continuous |
            | TSUM2  | Temperature sum from anthesis to maturity                     | 1550, 2100  | uniform      | continuous |
            | TBASEM | Base temperature for emergence                                | 2, 4        | uniform      | continuous |
            | TSUMEM | Temperature sum required for crop emergence                   | 170, 255    | uniform      | continuous |
            | TEFFMX | Maximum effective temperature for emergence                   | 18, 32      | uniform      | continuous |
            | SPAN   | Life span of leaves                                           | 20, 50      | uniform      | continuous |
            | TDWI   | Initial total dry weight of the crop                          | 75, 700     | uniform      | continuous |
            | RGRLAI | Relative growth rate of leaf area index                       | 0.008, 0.02 | uniform      | continuous |
            | Q10    | Temperature response factor for respiration (Q10 coefficient) | 2, 3        | uniform      | continuous |
        And the following specification is used for the calibration procedure:
            | name            | description                                  | value                |
            | experiment_name | The name of the current experiment           | WOFOST optimisation  |
            | n_jobs          | The number of simulations to run in parallel | -1                   |
            | random_seed     | The random seed for replicability            | 100                  |

    @netherlands @optimisation
    Scenario: Black-box optimisation of WOFOST potato for end-of-season LAI and TWSO in Limburg, Netherlands
        Given we are using NASA weather data with a latitude of "51" and a longitude of "5"
        And we are using agronomy management data in the "data/potato_netherlands_2021.agro" file
        When we execute an optimisation procedure using the "TPES" method and the "Optuna" library with "5" iterations

    @india @optimisation
    Scenario: Black-box optimisation of WOFOST potato for end-of-season LAI and TWSO in Gujarat, India
        Given we are using NASA weather data with a latitude of "23" and a longitude of "73"
        And we are using agronomy management data in the "data/potato_india_2021.agro" file
        When we execute an optimisation procedure using the "TPES" method and the "Optuna" library with "5" iterations
