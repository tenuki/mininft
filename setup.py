from distutils.core import setup

VERSION = '1.0.2'

setup(name='mininft',
      version=VERSION,
      description='Mini nft transfer helper',
      author='dave',
      author_email='dave@endlesstruction.com.ar',
      url='https://example.com/mininft',
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
