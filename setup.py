from setuptools import find_packages, setup

setup(
    name='netbox-phonebox',
    version='1.1.2',
    description='Phone number management for NetBox with E.164 validation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/MikeloVV/netbox-phonebox',
    author='Mikhail Voronov',
    author_email='mikhail.voronov@gmail.com',
    license='Apache 2.0',
    install_requires=[
        'phonenumbers>=8.13.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)