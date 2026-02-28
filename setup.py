from setuptools import setup, find_packages

setup(
    name='uplink',
    version='0.1.0',
    description='Terminal public chat room with authentication',
    author='Josh Clark',
    author_email='josh@wsgpolar.me',
    packages=find_packages(),
    install_requires=[
        'prompt_toolkit',
        'pyrebase4',
    ],
    entry_points={
        'console_scripts': [
            'uplink = uplink_pkg.client:main',
        ],
    },
    python_requires='>=3.8',
)