from __future__ import print_function

from distutils.core import setup
from distutils.core import Command

class BuildDustCommand(Command):
    
    user_options = []
    
    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass

    def run(self):
        
        import os
        import glob

        import numpy as np

        import matplotlib as mpl
        mpl.use('Agg')

        from hyperion.dust import TTsreDust, BHDust


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


        def process_bhmie_format(directory):
            print('-' * 72)
            print("Processing {0}".format(directory))
            print('-' * 72)
            d = BHDust(directory)
            d.optical_properties.extrapolate_wav(1.e-3, 1.e7)
            d.write(os.path.join('dust_files', os.path.basename(directory) + '.hdf5'))
            d.plot(os.path.join('dust_files', os.path.basename(directory) + '.png'))

        process_whitney_format('input/kmh94_hg/kmh94_3.1_hg')
        process_bhmie_format('input/kmh94_full/kmh94_3.1_full/kmh94_3.1_full')
        process_bhmie_format('input/d03/d03_3.1_6.0_A/d03_3.1_6.0_A')
        process_bhmie_format('input/d03/d03_4.0_4.0_A/d03_4.0_4.0_A')
        process_bhmie_format('input/d03/d03_5.5_3.0_A/d03_5.5_3.0_A')
        

setup(name='hyperion-dust',
      version="0.1.0",
      url='http://www.hyperion-rt.org',
      author='Thomas Robitaille',
      author_email='thomas.robitaille@gmail.com',
      description='Library of dust files for the Hyperion radiative transfer code',
      cmdclass={'build_dust':BuildDustCommand},
      packages=[],
      license='BSD'
      )
