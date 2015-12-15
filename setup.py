import os
import sys

try:
    from setuptools import find_packages
    from setuptools import setup
    packages = find_packages(exclude='tests')
except ImportError:
    from distutils.core import setup
    packages = ['txnats']

from pip.req import parse_requirements
try:
        from pip.download import PipSession
except ImportError as e:
        raise ImportError("cannot import name PipSession, "
                          "Please update pip to >= 1.5")

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


def read(fname):
    """
    Open and read a filename in this directory.
    :param fname: `str` file name in this directory

    Returns contents of file fname
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version():
    import imp

    with open('txnats/_meta.py', 'rb') as fp:
        mod = imp.load_source('_meta', 'txnats', fp)

    return mod.version


def get_requirement_items(filename):
    """
    Get install requirements from a file.
    :param filename: A file path to a requirements file.
    :return: A list of requirement items.
    :rtype: A `list` of :class:`pip.req.InstallRequirement`
    """
    with PipSession() as session:
        return list(parse_requirements(filename, session=session))


def get_requirements(filename):
    """
    Get requirements from a file and
    convert to a list of strings.
    :param filename:
    :return:
    """
    reqs = get_requirement_items(filename)

    return [str(r.req) for r in reqs]


def get_install_requires():
    return get_requirements('requirements.txt')


def get_test_requires():
    return get_requirements('requirements_dev.txt')


try:
    license_info = open('LICENSE').read()
except:
    license_info = 'APACHE 2.0'

setup_args = dict(
    name="txnats",
    version=get_version(),
    author="John W Lockwood IV",
    author_email="john.lockwood@workiva.com",
    description="@nats.io client protocol",
    license=license_info,
    keywords="data",
    url="https://github.com/johnwlockwood/txnats",
    package_dir={'txnats': 'txnats'},
    packages=packages,
    install_requires=get_install_requires(),
    tests_require=get_test_requires(),
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)

if __name__ == '__main__':
    setup(**setup_args)
