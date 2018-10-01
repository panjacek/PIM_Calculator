from setuptools import setup, find_packages

setup(name='PIM_Calculator',
      version='0.1',
      description='Passive Intermodulation Calculator for RF antennas',
      url='http://github.com/panjacek/PIM_Calculator',
      author='Jacek Kreft',
      license='Unlincense',
      packages=find_packages(),
      # packages=['PIM_Calculator'],
      scripts=[
          'bin/PIM_Calculator',
          'bin/PIM_GUI_Calculator'
      ],
      setup_requires=['pytest'],
      tests_require=['pytest', 'pytest-mock', 'pytest-cov'],
      entry_points = {
            'console_scripts': [
                'PIM_Calculator=PIM_Calculator.pim_calc:main',
                'PIM_GUI_Calculator=PIM_Calculator.pimQt:main'
            ]
      },
      install_requires=[
          'numpy>=1.13.3',
      ],
      zip_safe=False)
