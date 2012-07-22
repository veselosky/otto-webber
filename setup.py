from setuptools import setup, find_packages
setup(
    name = "otto",
    version = "0.3.0",
    packages = find_packages(),
    author = "Vince Veselosky",
    author_email = "vince@control-escape.com",
    description = "Vince's personal tools that won't work for you",
    license = "MIT",
    url = "",
    # could also include long_description, download_url, classifiers, etc.

    # Project includes Sphinx documentation, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
        # 'argparse >= 1.2.1',
        # 'docutils >= 0.7',
        'fabric >= 1.2',
        # 'python-dateutil >= 1.5, <2.0', # 2.0 only for python3
        # 'sphinx >= 1.0',
        # 'unittest2 >= 0.5.1',
    ],

    include_package_data=True,
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the package, too:
        '': ['*.msg'],
    },


)
