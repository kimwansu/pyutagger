from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_desc = f.read()

setup(
    name='pyutagger',
    version='0.9.1.578',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    description='Python wrapper for UTagger',
    author='Kim Wansu',
    author_email='wantalia@gmail',
    url='http://klplab.ulsan.ac.kr',
    license='MIT',
    python_requires='>=3.7',
    install_requires=['requests', 'tqdm'],
    packages=['pyutagger']
)