from distutils.core import setup

setup(name='micro.py',
      version='0.0.1',
      packages=['micro', 'micro.sdl2'],
      include_package_data=True,
      package_dir={'micro': 'src/micro'},
      package_data={'micro': ['native/windows/*/*.dll', 'builtin/*.*']},
      )