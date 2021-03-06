from astropy.io import fits
import pandas as pd
import numpy as np
import glob
import os


class ExternalFile:
    """ Read in external files and turn them into numpy arrays to work with pyRT_DISORT functions"""
    def __init__(self, file_path, header_lines=0, text1d=True):
        """
        Parameters
        ----------
        file_path: str
            The absolute path to the file
        header_lines: int, optional
            The number of header lines to skip. Only used for plain text input
        text1d: bool, optional
            Denote if the data are 1D or 2D. Only used for plain text input
        """
        self.file_path = file_path
        self.header_lines = header_lines
        self.text1d = text1d
        self.__check_inputs()
        self.__trim_file_path()
        self.filename = self.__get_filename()
        self.extension = self.__get_extension()
        self.array = self.__read_in_file()

    def __check_inputs(self):
        assert isinstance(self.file_path, str), 'file_path must be a string'
        assert isinstance(self.header_lines, int), 'header_lines must be an int'
        assert isinstance(self.text1d, bool), 'text1d needs to be a boolean'

    def __trim_file_path(self):
        self.file_path = self.file_path.strip()

    def __get_filename(self):
        return self.file_path.split('.')[0]

    def __get_extension(self):
        return self.file_path.split('.')[-1]

    def __read_in_file(self):
        if self.extension == 'npy':
            return self.__read_npy_file()
        elif self.extension == 'csv':
            return self.__csv_to_npy()
        elif self.extension == 'fits':
            return self.__read_fits_file()
        elif self.extension in ['txt', 'dat', 'coef', 'phsfn']:
            if self.text1d:
                return self.__1dtext_to_npy()
            else:
                return self.__2dtext_to_npy()
        else:
            print('Unsure how to handle that extension... please use .npy, .csv, .fits, .txt, .dat, .coef, .phsfn')
            return None

    def __read_npy_file(self):
        return np.load(self.file_path)

    def __csv_to_npy(self):
        return pd.read_csv(self.file_path).to_numpy()

    def __read_fits_file(self):
        return fits.open(self.file_path)

    def __get_absolute_path(self, new_filename):
        if new_filename.strip()[-1] == '/':
            raise SystemExit('You provided a path but not a filename...')

        # assume it's a relative path
        if '/' not in new_filename:
            stripped_filename = self.__strip_extensions(new_filename)
            split_paths = self.file_path.split('/')
            split_paths[-1] = stripped_filename
            return '/'.join(split_paths)
        # assume it's an absolute path
        else:
            return new_filename

    @staticmethod
    def __strip_extensions(filename):
        return filename.split('.')[0]

    def __1dtext_to_npy(self):
        coeff = []
        f = open(self.file_path)
        lines = f.readlines()[self.header_lines:]
        for line in lines:
            a = np.fromstring(line.strip(), sep=' ')
            coeff.append(a)

        # This unravels a list and stores it as an array
        return np.array([co for all_coeff in coeff for co in all_coeff])

    def __2dtext_to_npy(self):
        return np.genfromtxt(self.file_path, skip_header=self.header_lines, filling_values=np.nan)

    def save_as_npy(self, new_filename=''):
        """ Save the input file as a numpy array

        Parameters
        ----------
        new_filename: str
            The filename for the newly created file. Can be an absolute path; otherwise makes a file in the same
            location as the data file.

        Returns
        -------
        None

        Examples
        --------
        >>> folder = '/path/to/my/data/'
        >>> file = 'folder' + 'myDataFile.csv'
        >>> f = ExternalFiles(file)
        >>> f.save_as_npy(new_filename='myBetterNamedDataFile')

        >>> folder = '/path/to/my/data/'
        >>> file = 'folder' + 'myDataFile.txt'
        >>> f = ExternalFiles(file)
        >>> f.save_as_npy(new_filename='/absolute/path/to/my/new/file/fileName')

        """
        assert isinstance(new_filename, str), 'new_filename must be a string'
        absolute_path = self.__get_absolute_path(new_filename)
        np.save(absolute_path, self.array)

    def save_as_csv(self, new_filename, headers):
        """ Save the input file in .csv format

        Parameters
        ----------
        new_filename: str
            The filename for the newly created file. Can be an absolute path; otherwise makes a file in the same
            location as the data file.
        headers: list
            A list of strings of each of the column names

        Returns
        -------
        None
        """
        if (dims := np.ndim(self.array)) > 2:
            print('You\'re trying to save a {}D array in 2D format... consult a string theorist.'.format(dims))
            return
        absolute_path = self.__get_absolute_path(new_filename)
        pd.DataFrame(self.array).to_csv('{}.csv'.format(absolute_path), header=headers, index=False)


class MultipleExternalFiles:
    """ Get the absolute paths of files matching a given pattern"""
    def __init__(self, pattern, path):
        """
        Parameters
        ----------
        pattern: str
            A regex pattern to match
        path: str
            The location of files to match the pattern to
        """
        self.pattern = pattern
        self.path = path
        self.files = self.__get_files()

    def __check_inputs(self):
        assert isinstance(self.pattern, str), 'pattern must a string'
        assert isinstance(self.path, str), 'path must be a string'

    def __get_files(self):
        absolute_path = os.path.join(self.path, self.pattern)
        return sorted(glob.glob(absolute_path))
