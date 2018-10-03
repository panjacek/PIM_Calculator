from setuptools import setup, find_packages

setup(name='PIM_Calculator',
      version='0.2',
      description='Passive Intermodulation Calculator for RF antennas',
      url='http://github.com/panjacek/PIM_Calculator',
      author='Jacek Kreft',
      license='Unlincense',
      packages=find_packages(),
      scripts=[
          'bin/PIM_Calculator',
          'bin/PIM_GUI_Calculator'
      ],
      setup_requires=['pytest'],
      tests_require=['pytest', 'pytest-mock', 'pytest-cov', 'pytest-qt', 'pytest-xvfb'],
      entry_points = {
            'console_scripts': [
                'PIM_Calculator=PIM_Calculator.pim_calc:main',
                'PIM_GUI_Calculator=PIM_Calculator.pimQt:main [GUI]'
            ]
      },
      install_requires=[
            'numpy>=1.13.3',
      ],
      extras_require={
          'GUI': [
              'PySide2', 'scipy>=1.0', 'matplotlib>=2.0'
          ]
      },
      zip_safe=False)
