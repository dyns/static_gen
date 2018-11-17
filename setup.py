from setuptools import setup

setup (
    name='my_gen',
    version='0.1',
    packages=['py_gen'],

    # add entry point to main cli module
    entry_points={
        'console_scripts': [
            'my_gen = py_gen.main:main']
    },

    install_requires=['click',
                       'pyyaml',
                       'Jinja2',
                       'markdown',
                        ]

)

