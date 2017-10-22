from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-report',
	version=version,
	description='CKAN Extension providing report / Feedback form',
	classifiers=[],
	keywords='',
	author='Ben Scott',
	author_email='ben@benscott.co.uk',
	url='',
	license='',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.report'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[],
	entry_points="""
    [ckan.plugins]
    	report=ckanext.report.plugin:reportPlugin
        [babel.extractors]
        ckan = ckan.lib.extract:extract_ckan
        """,
    # If you are changing from the default layout of your extension, you may
    # have to change the message extractors, you can read more about babel
    # message extraction at
    # http://babel.pocoo.org/docs/messages/#extraction-method-mapping-and-configuration
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
      ],
    }
)