import numpy as np
from utils.constants import Constants

CONSTANTS_PARAMS = Constants()


def compute_session_cumulative_consumption(
    data: np.array, x_unit_measurement: str, y_unit_measurement: str
) -> float:
    """
    Takes a numpy array as a series of input data with the references on x and y units of measurement
    and returns the cumulative consumption of that session.
    """

    seconds_relative_data = (
        data
        / CONSTANTS_PARAMS.time_unit_measures_in_seconds[y_unit_measurement]
        * CONSTANTS_PARAMS.time_unit_measures_in_seconds[x_unit_measurement]
    )

    return seconds_relative_data.sum()


# Test the function with fake data
if __name__ == "__main__":
    prova = np.array([5, 4, 5, 1, 5])

    result = compute_session_cumulative_consumption(prova, "m", "h")
    print(result)
