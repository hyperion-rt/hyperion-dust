from __future__ import print_function

import os
import glob

import numpy as np

import matplotlib as mpl
mpl.use('Agg')

from hyperion.dust import TTsreDust


if not os.path.exists('dust_files'):
    os.mkdir('dust_files')


def process_whitney_format(filename):
    print('-' * 72)
    print("Processing {0}".format(filename))
    print('-' * 72)
    d = TTsreDust(filename)
    d.optical_properties.extrapolate_wav(1.e-3, 1.e7)
    d.write(os.path.join('dust_files', os.path.basename(filename) + '.hdf5'))
    d.plot(os.path.join('dust_files', os.path.basename(filename) + '.png'))

process_whitney_format('input/kmh94')
