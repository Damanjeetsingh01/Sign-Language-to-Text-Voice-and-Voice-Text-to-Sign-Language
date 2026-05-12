import setuptools

setuptools.setup(
    name='text-to-sign-language-converter',
    version='0.1.0',
    description='Python project',
    author='Delta 4',
    author_email='Damanjeet.9719@gmail.com',
    packages=setuptools.find_packages(),
    setup_requires=['nltk', 'joblib','click','regex','sqlparse','setuptools'],
)