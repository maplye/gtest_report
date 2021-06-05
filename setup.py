from setuptools import setup


def readme():
  with open('README.md') as readme_file:
    return readme_file.read()


setup(
    name='gtest-report',
    version='0.0.2',
    description='Generate test report for gtest.',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License'
    ],
    url='https://github.com/maplye/gtest-report',
    author='Yao Guorong',
    author_email='maplye@gmail.com',
    license='MIT',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=['gtest_report'],
    install_requires=['comment-parser==1.2.3', 'Jinja2==3.0.1'],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False)
