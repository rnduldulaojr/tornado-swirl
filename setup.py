try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README') as file:
    long_description = file.read()

setup(name='tornado-swirl',
      python_requires='>=3.6.0',
      version='0.1.13',
      url='https://github.com/rduldulao/tornado-swirl',
      zip_safe=False,
      packages=['tornado_swirl'],
      package_data={
        'tornado_swirl': [
          'openapi/*.*',
          'static/*.*',
        ]
      },
      description='Extract swagger specs from your tornado project',
      author='Rodolfo Duldulao',
      license='MIT',
      long_description=long_description,
      install_requires=[
        'tornado>=5.1.1'
      ],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6'
      ],
      keywords=['SWAGGER', 'OPENAPI', 'TORNADO'],
      download_url='https://github.com/rduldulao/tornado-swirl/archive/v_0.1.13.tar.gz',
)
