import os
from unittest import TestCase
import numpy as np
from pyRT_DISORT.eos import ModelEquationOfState, eos_from_array


class TestModelEquationOfState(TestCase):
    def setUp(self) -> None:
        self.eos = ModelEquationOfState


class TestInit(TestModelEquationOfState):
    def test_2d_altitude_grid_raises_value_error(self):
        with self.assertRaises(ValueError):
            a = np.ones((10, 5))
            junk = np.linspace(1, 10)
            ModelEquationOfState(a, junk, junk, junk, junk)

    def test_mono_increasing_altitude_model_raises_value_error(self):
        a = np.linspace(1, 50)
        ModelEquationOfState(a, a, a, a, np.flip(a))
        with self.assertRaises(ValueError):
            ModelEquationOfState(a, a, a, a, a)

    def test_list_altitude_grid_raises_type_error(self):
        altitude_grid = [0, 10, 20]
        junk = np.linspace(20, 10)
        with self.assertRaises(TypeError):
            ModelEquationOfState(altitude_grid, junk, junk, junk, junk)

    def test_index_error_raised_if_grids_do_not_have_same_shape(self):
        a = np.linspace(10, 20)
        with self.assertRaises(IndexError):
            ModelEquationOfState(a, a, a[:-1], a, np.flip(a))


class TestAltitudeBoundaries(TestModelEquationOfState):
    def test_altitude_boundaries_is_unchanged(self):
        junk = np.linspace(50, 10)
        ab = junk - 5
        eos = ModelEquationOfState(junk, junk + 1, junk + 2, junk + 3, ab)
        self.assertTrue(np.array_equal(ab, eos.altitude_boundaries))


class TestNLayers(TestModelEquationOfState):
    def test_n_layers_is_defined_by_altitude_model(self):
        junk = np.linspace(50, 10, num=10)
        ab = np.linspace(60, 20, num=30)
        eos = ModelEquationOfState(junk, junk, junk, junk, ab)
        self.assertEqual(29, eos.n_layers)


class TestNumberDensityBoundaries(TestModelEquationOfState):
    pass


class TestPressureBoundaries(TestModelEquationOfState):
    def test_pressure_is_linearly_interpolated(self):
        alts = np.array([10, 20, 30])
        pressure = np.array([50, 30, 10])
        temperatures = np.array([200, 170, 140])
        # for some reason it gives me an error if I use realistic values
        num_den = np.array([100, 50, 25])
        malts = np.array([25, 15])
        eos = ModelEquationOfState(alts, pressure, temperatures, num_den, malts)
        expected_pressure = np.array([20, 40])
        self.assertTrue(np.array_equal(expected_pressure,
                                       eos.pressure_boundaries))


class TestTemperatureBoundaries(TestModelEquationOfState):
    def test_temperature_is_linearly_interpolated(self):
        alts = np.array([10, 20, 30])
        pressure = np.array([50, 30, 10])
        temperatures = np.array([200, 170, 140])
        # for some reason it gives me an error if I use realistic values
        num_den = np.array([100, 50, 25])
        malts = np.array([25, 15])
        eos = ModelEquationOfState(alts, pressure, temperatures, num_den, malts)
        expected_temperatures = np.array([155, 185])
        self.assertTrue(np.array_equal(expected_temperatures,
                                       eos.temperature_boundaries))


class TestColumnDensityLayers(TestModelEquationOfState):
    def test_column_density_calculated_reliably(self):
        filepath = os.path.dirname(os.path.realpath(__file__))
        f = np.load(os.path.join(filepath, 'mars_atm.npy'))
        z = f[:, 0]
        P = f[:, 1]
        T = f[:, 2]
        n = f[:, 3]
        eos = ModelEquationOfState(z, P, T, n, z)
        answer = np.load(os.path.join(filepath, 'colden.npy'))
        self.assertTrue(np.array_equal(answer, eos.column_density_layers))


class TestEOSFromArray(TestModelEquationOfState):
    def test_column_density_calculated_reliably(self):
        filepath = os.path.dirname(os.path.realpath(__file__))
        f = np.load(os.path.join(filepath, 'mars_atm.npy'))
        eos = eos_from_array(f, f[:, 0])
        answer = np.load(os.path.join(filepath, 'colden.npy'))
        self.assertTrue(np.array_equal(answer, eos.column_density_layers))