from distutils.core import setup

VERSION = '1.0.6'

setup(name='mininft',
      version=VERSION,
      description='Mini nft transfer helper',
      author='tenuki',
      author_email='dave@endlesstruction.com.ar',
      url='https://github.com/tenuki/mininft',
      py_modules=['mininft'],
      install_requires=[
          'Click',
          'web3'
      ],
      entry_points={
          'console_scripts': [
              'mininft = mininft:mininft',
          ],
      })
