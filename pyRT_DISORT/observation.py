"""observation.py contains data structures to hold quantities commonly found in
an observation.
"""
from warnings import warn
import numpy as np
from pyRT_DISORT.utilities.array_checks import ArrayChecker


# TODO: I'm not sure that all combination of angles are physically realistic. If
#  so, raise a warning
# TODO: It'd probably be better to catch different shape errors when making phi
class Angles:
    """Create a data structure that contains angles required by DISORT.

    Angles accepts ``observation'' angles and computes mu, mu0, phi, and phi0
    from these angles.

    """

    def __init__(self, incidence_angles: np.ndarray,
                 emission_angles: np.ndarray, phase_angles: np.ndarray) -> None:
        """
        Parameters
        ----------
        incidence_angles: np.ndarray
            Pixel incidence angles [degrees].
        emission_angles: np.ndarray
            Pixel emission angles [degrees].
        phase_angles: np.ndarray
            Pixel phase angles [degrees].

        Raises
        ------
        ValueError
            Raised if any of the input arrays contain non-numeric values, if
            any of the angles contain values outside of their mathematically
            valid range, or if the input arrays do not have the same shape.

        Notes
        -----
        pyRT_DISORT computes all angular quantities across multiple pixels at
        once to save computation time, but each DISORT run can only be done on a
        per-pixel basis. Therefore, each element in mu, mu0, phi, and phi0 are
        the expected DISORT inputs.

        """
        self.__incidence = self.__make_incidence_angles(incidence_angles)
        self.__emission = self.__make_emission_angles(emission_angles)
        self.__phase = self.__make_phase_angles(phase_angles)

        self.__mu0 = self.__compute_mu0()
        self.__mu = self.__compute_mu()
        self.__phi0 = self.__make_phi0()
        self.__phi = self.__compute_phi()

    def __make_incidence_angles(self, incidence: np.ndarray) -> np.ndarray:
        incidence = self.__cast_to_ndarray(incidence)
        self.__raise_value_error_if_angles_are_not_in_range(
            incidence, 0, 180, 'incidence_angles')
        return incidence

    def __make_emission_angles(self, emission: np.ndarray) -> np.ndarray:
        emission = self.__cast_to_ndarray(emission)
        self.__raise_value_error_if_angles_are_not_in_range(
            emission, 0, 90, 'emission_angles')
        return emission

    def __make_phase_angles(self, phase: np.ndarray) -> np.ndarray:
        phase = self.__cast_to_ndarray(phase)
        self.__raise_value_error_if_angles_are_not_in_range(
            phase, 0, 180, 'phase_angles')
        return phase

    def __compute_mu0(self) -> np.ndarray:
        return self.__compute_angle_cosine(self.__incidence)

    def __compute_mu(self) -> np.ndarray:
        return self.__compute_angle_cosine(self.__emission)

    def __make_phi0(self) -> np.ndarray:
        return np.zeros(self.__phase.shape)

    # TODO: is there a less messy way to make this variable?
    def __compute_phi(self) -> np.ndarray:
        try:
            with np.errstate(invalid='raise'):
                sin_emission_angle = np.sin(np.radians(self.__emission))
                sin_solar_zenith_angle = np.sin(np.radians(self.__incidence))
                cos_phase_angle = self.__compute_angle_cosine(self.__phase)
                try:
                    tmp_arg = (cos_phase_angle - self.mu * self.mu0) / \
                              (sin_emission_angle * sin_solar_zenith_angle)
                    d_phi = np.arccos(np.clip(tmp_arg, -1, 1))
                except FloatingPointError:
                    d_phi = np.pi
                return self.phi0 + 180 - np.degrees(d_phi)
        except ValueError as ve:
            raise ValueError('The input angles must be the same shape.') from ve

    @staticmethod
    def __cast_to_ndarray(angles: np.ndarray) -> np.ndarray:
        return np.array(angles)

    @staticmethod
    def __raise_value_error_if_angles_are_not_in_range(
            angles: np.ndarray, low: float, high: float, name: str) -> None:
        try:
            if np.any(angles < low) or np.any(angles > high):
                raise ValueError(f'{name} must be between {low} and {high}.')
        except TypeError as te:
            raise ValueError(f'{name} is non-numeric') from te

    @staticmethod
    def __compute_angle_cosine(angle: np.ndarray) -> np.ndarray:
        return np.cos(np.radians(angle))

    @property
    def incidence(self) -> np.ndarray:
        """Get the input incidence (solar zenith) angles [degrees].

        Returns
        -------
        np.ndarray
            The input incidence angles.

        """
        return self.__incidence

    @property
    def emission(self) -> np.ndarray:
        """Get the input emission angles [degrees].

        Returns
        -------
        np.ndarray
            The input emission angles.

        """
        return self.__emission

    @property
    def phase(self) -> np.ndarray:
        """Get the input phase angles [degrees].

        Returns
        -------
        np.ndarray
            The input phase angles.

        """
        return self.__phase

    @property
    def mu0(self) -> np.ndarray:
        """Get mu0 where mu0 is the cosine of the input incidence angles.

        Returns
        -------
        np.ndarray
            The cosine of the input incidence angles.

        Notes
        -----
        Each element in this variable is named "UMU0" in DISORT.

        """
        return self.__mu0

    @property
    def mu(self) -> np.ndarray:
        """Get mu where mu is the cosine of the input emission angles.

        Returns
        -------
        np.ndarray
            The cosine of the input emission angles.

        Notes
        -----
        Each element in this variable is named "UMU" in DISORT.

        """
        return self.__mu

    @property
    def phi0(self) -> np.ndarray:
        """Get phi0. I assume this is always 0.

        Returns
        -------
        np.ndarray
            All 0s.

        Notes
        -----
        Each element in this variable is named "PHI0" in DISORT.

        """
        return self.__phi0

    @property
    def phi(self) -> np.ndarray:
        """Get phi where phi is the azimuth angle [degrees].

        Returns
        -------
        np.ndarray
            The azimuth angles.

        Notes
        -----
        Each element in this variable is named "PHI" in DISORT.

        """
        return self.__phi


class Wavelengths:
    """Create a data structure that contains spectral info for DISORT.

    Wavelengths accepts ``observation'' wavelengths and computes their
    corresponding wavenumbers.

    """

    def __init__(self, short_wavelengths: np.ndarray,
                 long_wavelengths: np.ndarray) -> None:
        """
        Parameters
        ----------
        short_wavelengths: np.ndarray
            The short wavelengths [microns] for each spectral bin.
        long_wavelengths: np.ndarray
            The long wavelengths [microns] for each spectral bin.

        Raises
        ------
        IndexError
            Raised if the input wavelengths are not the same shape.
        TypeError
            Raised if any of the inputs are not np.ndarrays.
        ValueError
            Raised if any of the input spectral arrays are not 1D arrays,
            contain non-numeric values, contain non positive finite values, if
            they are not both the same shape, or if any value in
            long_wavelengths is not larger than the corresponding value in
            short_wavelengths.

        Warnings
        --------
        UserWarning
            Raised if any of the input wavelengths are not between 0.1 and 50
            microns

        Notes
        -----
        DISORT does not require either short_wavelengths or long_wavelengths,
        but these quantities are useful to use in pyRT_DISORT in order to obtain
        the spectral dependence of aerosol radiative properties. The
        corresponding wavenumbers are only sometimes used by DISORT. See the
        instance variable docstrings for more details.

        """
        self.__short_wavelengths = short_wavelengths
        self.__long_wavelengths = long_wavelengths

        #self.__raise_error_if_input_wavelengths_are_bad()
        self.__warn_if_wavelengths_are_outside_expected_range()

        self.__high_wavenumber = self.__calculate_high_wavenumber()
        self.__low_wavenumber = self.__calculate_low_wavenumber()

    def __raise_error_if_input_wavelengths_are_bad(self) -> None:
        self.__raise_error_if_short_wavelengths_are_bad()
        self.__raise_error_if_long_wavelengths_are_bad()
        self.__raise_index_error_if_wavelengths_are_not_same_shape()
        self.__raise_value_error_if_long_wavelength_is_not_larger()

    def __raise_error_if_short_wavelengths_are_bad(self) -> None:
        self.__raise_error_if_wavelengths_are_bad(
            self.__short_wavelengths, 'short_wavelengths')

    def __raise_error_if_long_wavelengths_are_bad(self) -> None:
        self.__raise_error_if_wavelengths_are_bad(
            self.__long_wavelengths, 'long_wavelengths')

    def __raise_error_if_wavelengths_are_bad(self, wavelengths, name) -> None:
        try:
            checks = self.__perform_wavelength_checks(wavelengths)
        except TypeError:
            raise TypeError(f'{name} must be a np.ndarray.') from None
        if not all(checks):
            raise ValueError(f'{name} must be a 1D array of positive, finite '
                             f'values.')

    @staticmethod
    def __perform_wavelength_checks(wavelengths) -> list[bool]:
        wavelength_checker = ArrayChecker(wavelengths)
        checks = [wavelength_checker.determine_if_array_is_positive_finite(),
                  wavelength_checker.determine_if_array_is_1d()]
        return checks

    def __raise_index_error_if_wavelengths_are_not_same_shape(self) -> None:
        if self.__short_wavelengths.shape != self.__long_wavelengths.shape:
            raise IndexError('short_wavelengths and long_wavelengths must '
                             'have the same shape.')

    def __raise_value_error_if_long_wavelength_is_not_larger(self) -> None:
        if not np.all(self.__long_wavelengths > self.__short_wavelengths):
            raise ValueError('long_wavelengths must always be larger than '
                             'the corresponding short_wavelengths.')

    def __warn_if_wavelengths_are_outside_expected_range(self) -> None:
        if np.any(self.__short_wavelengths < 0.1) or np.any(
                self.__long_wavelengths > 50):
            warn('The input wavelengths are outside the expected range of 0.1 '
                 'to 50 microns.')

    def __calculate_high_wavenumber(self) -> np.ndarray:
        return self.__convert_wavelength_to_wavenumber(
            self.__short_wavelengths, 'short_wavelengths')

    def __calculate_low_wavenumber(self) -> np.ndarray:
        return self.__convert_wavelength_to_wavenumber(
            self.__long_wavelengths, 'long_wavelengths')

    @staticmethod
    def __convert_wavelength_to_wavenumber(wavelength: np.ndarray,
                                           wavelength_name: str) -> np.ndarray:
        with np.errstate(divide='raise'):
            try:
                return 1 / (wavelength * 10 ** -4)
            except FloatingPointError:
                raise ValueError(f'At least one value in {wavelength_name} '
                                 f'is too small to perform calculations!') \
                    from None

    @property
    def short_wavelengths(self) -> np.ndarray:
        """Get the input short wavelengths [microns].

        Returns
        -------
        np.ndarray
            The short wavelengths.

        """
        return self.__short_wavelengths

    @property
    def long_wavelengths(self) -> np.ndarray:
        """Get the input long wavelengths [microns].

        Returns
        -------
        np.ndarray
            The long wavelengths.

        """
        return self.__long_wavelengths

    @property
    def high_wavenumber(self) -> np.ndarray:
        """Get the high wavenumbers [1/cm]---the wavenumbers corresponding to
        short_wavelength.

        Returns
        -------
        np.ndarray
            The high wavenumbers.

        Notes
        -----
        In DISORT, this variable is named "WVNMHI". It is only needed by DISORT
        if thermal_emission (defined in ThermalEmission) == True, or if
        DISORT is run multiple times and BDREF is spectrally dependent.

        """
        return self.__high_wavenumber

    @property
    def low_wavenumber(self) -> np.ndarray:
        """Get the low wavenumbers [1/cm]---the wavenumbers associated with
        long_wavelength.

        Returns
        -------
        np.ndarray
            The low wavenumbers.

        Notes
        -----
        In DISORT, this variable is named "WVNMLO". It is only needed by DISORT
        if thermal_emission (defined in ThermalEmission) == True, or if
        DISORT is run multiple times and BDREF is spectrally dependent.

        """
        return self.__low_wavenumber