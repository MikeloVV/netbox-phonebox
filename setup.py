from setuptools import find_packages, setup

setup(
    name='netbox-phonebox',
    version='1.1.2',
    description='Phone number management for NetBox',
    url='https://github.com/MikeloVV/netbox-phonebox',
    author='Mikhail Voronov',
    license='Apache 2.0',
    install_requires=[
        'phonenumbers>=8.13.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)