import glob
import os

import numpy as np


def convert(file_in, file_out):

    data = np.loadtxt(file_in, skiprows=5)

    wav = data[:, 0]
    real = data[:, 3] + 1.
    imag = data[:, 4]

    np.savetxt(file_out, np.vstack([wav, real, imag]).transpose(), fmt="%.6e")

convert('callindex.out_silD03', 'silicate_d03')
convert('callindex.out_CpaD03_0.01', 'graphite_par_d03_0.01')
convert('callindex.out_CpaD03_0.10', 'graphite_par_d03_0.10')
convert('callindex.out_CpeD03_0.01', 'graphite_per_d03_0.01')
convert('callindex.out_CpeD03_0.10', 'graphite_per_d03_0.10')
