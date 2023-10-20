from setuptools import setup, find_packages

install_requires=[
   'rdflib>=6.3.2,<=6.3.2',
   'owlrl>=6.0.2,<=6.0.2',
   'pyrml @ git+https://github.com/anuzzolese/pyrml',
   'iPOPO>=1.0.1,<=1.0.1',
   'shortuuid>=1.0.9,<=1.0.9',
   'Jinja2>=3.1.2,<=3.1.2',
   'Werkzeug>=2.2.2,<=2.2.2',
   'Flask>=2.2.2,<=2.2.2',
   'apache-airflow>=2.4.2,<=2.4.2',
   'pyodbc>=4.0.34,<=4.0.34',
   'owlready2>=0.43,<=0.43',
   'oxrdflib>=0.3.4,<=0.3.4',
   'chardet>=5.1.0,<=5.1.0'
   'Cython>=0.29.35,<=0.29.35',
   'requests>=2.31.0,<=2.31.0',
   'pyshacl>=0.23.0,<=0.23.0'
]

setup(name='WHOWToolkit', version='0.0.1',
    packages=find_packages(), install_requires=install_requires)
