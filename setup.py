from setuptools import setup, find_packages

setup(name='docker-utils',
      version='0.1a',
      description='Utilities for working with docker',
      author='Brent Baude',
      author_email='bbaude@redhat.com',
      url='https://github.com/baude/docker-utils/',
      license='LGPLv2+',
      packages=find_packages(),
      scripts=['docker-utils/docker-dash', 'docker-utils/container-template']
)
