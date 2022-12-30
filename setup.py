from setuptools import setup, find_packages

setup(
	name='imgdiff',
	version='1.0',
	url='https://github.com/trnciii/imgdiff',
	license='MIT',
	packages={'imgdiff':['imgdiff']},
	install_requires=[
		'numpy',
		'libsixel-python',
		'Pillow',
	],
	entry_points={
		'console_scripts': [
			'imgdiff = imgdiff.__main__:main'
		]
	}
)