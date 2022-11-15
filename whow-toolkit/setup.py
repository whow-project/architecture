from setuptools import setup, find_packages

install_requires=[
   'rdflib>=6.2.0,<=6.2.0',
   'pyrml @ git+https://github.com/anuzzolese/pyrml',
   'iPOPO>=1.0.1,<=1.0.1',
   'shortuuid>=1.0.9,<=1.0.9',
   'Jinja2>=3.1.2,<=3.1.2',
   'Flask>=2.2.2,<=2.2.2',
   'apache-airflow>=2.4.2,<=2.4.2'
]

setup(name='WHOWToolkit', version='0.0.1',
    packages=find_packages(), install_requires=install_requires)
