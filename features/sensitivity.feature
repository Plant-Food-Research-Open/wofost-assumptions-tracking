Feature: Sobol sensitivity analysis for WOFOST potato
    Because parameter uncertainty drives crop development and growth
    We want to quantify global sensitivities using Sobol indices
    So we can identify influential parameters for potato LAI and TWSO

    Background:
        Given we are using WOFOST site data with a WAV of "50.0"
        And we are using default soil parameter values
        And we are using crop data stored in the "data" directory
        And our state variables are "LAI and TWSO"
        And the following parameter specification is used for calibration:
            | name      | description                                                   | range       | distribution | type       |
            | TSUM1     | Temperature sum from emergence to anthesis                    | 150, 280    | uniform      | continuous |
            | TSUM2     | Temperature sum from anthesis to maturity                     | 1550, 2100  | uniform      | continuous |
            | TBASEM    | Base temperature for emergence                                | 2, 4        | uniform      | continuous |
            | TSUMEM    | Temperature sum required for crop emergence                   | 170, 255    | uniform      | continuous |
            | TEFFMX    | Maximum effective temperature for emergence                   | 18, 32      | uniform      | continuous |
            | SPAN      | Life span of leaves                                           | 20, 50      | uniform      | continuous |
            | TDWI      | Initial total dry weight of the crop                          | 75, 700     | uniform      | continuous |
            | RGRLAI    | Relative growth rate of leaf area index                       | 0.008, 0.02 | uniform      | continuous |
            | Q10       | Temperature response factor for respiration (Q10 coefficient) | 2, 3        | uniform      | continuous |
        And the following specification is used for the calibration procedure:
            | name              | description                                   | value                             |
            | experiment_name   | The name of the current experiment            | WOFOST sensitivity analysis       |
            | n_jobs            | The number of simulations to run in parallel  | 10                                |

    @netherlands @sensitivity
    Scenario: Sobol sensitivity analysis for LAI and TWSO in Limburg, Netherlands
        Given we are using NASA weather data with a latitude of "51" and a longitude of "5"
        And we are using agronomy management data in the "data/potato_netherlands_2021.agro" file
        When we execute a sensitivity analysis using the "Sobol" method and the "SALib" library with "4" samples
        Then behave will test it for us!

    @india @sensitivity
    Scenario: Sobol sensitivity analysis for LAI and TWSO in Gujarat, India
        Given we are using NASA weather data with a latitude of "23" and a longitude of "73"
        And we are using agronomy management data in the "data/potato_india_2021.agro" file
        When we execute a sensitivity analysis using the "Sobol" method and the "SALib" library with "4" samples
        Then behave will test it for us!
