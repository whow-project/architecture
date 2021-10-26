from distutils.core import setup

install_requires=[
	'chardet<=3.0.4,>=3.0.4',
	'clevercsv<=0.6.3,>=0.6.3',
	'Cython<=0.29.19,>=0.29.19',
	'isodate<=0.6.0,>=0.6.0',
	'Jinja2<=2.11.2,>=2.11.2',
	'MarkupSafe<=1.1.1,>=1.1.1',
	'pyparsing<=2.4.7,>=2.4.7',
	'pyshp<=2.1.0,>=2.1.0',
	'rdflib<=5.0.0,>=5.0.0',
	'regex<=2020.5.14,>=2020.5.14',
	'six<=1.15.0,>=1.15.0',
	'SPARQLWrapper<=1.8.5,>=1.8.5',
	'pyproj<=2.4.1,>=2.4.1',
	'Shapely<=1.6.4.post2,>=1.6.4.post2',
	'pandas<=0.25.3,>=0.25.3',
	'requests<=2.21.0,>=2.21.0'
]

setup(name='triplification', version='1.0.0', install_requires=install_requires)

