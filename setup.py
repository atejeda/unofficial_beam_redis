from distutils.core import setup

setup(
    name = 'unofficial_beam_redis',
    packages = ['unofficial_beam_redis', 'unofficial_beam_redis.io'],
    version = '0.5',
    license='Aapache 2.0',
    description = 'An unofficial apache beam sink for redis',
    author = 'unofficial_beam_redis',
    author_email = 'unofficial_beam_redis@github.com',
    url = 'https://github.com/atejeda/unofficial_beam_redis',
    download_url = 'https://github.com/atejeda/unofficial_beam_redis/archive/v_01.tar.gz',
    keywords = ['Apache', 'Beam', 'Redis', 'Sink'],
    install_requires=[
        'apache-beam',
        'redis',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License', # 2.0
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
