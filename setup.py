from setuptools import setup

# Get version without importing, which avoids dependency issues
exec(compile(open("pylox/version.py").read(),
             "pylox/version.py", "exec"))

setup(name='pylox',
      description='Python Lox interpreter.',
      version=__version__,
      author='Matt Mulholland',
      author_email='mulhodm@gmail.com',
      packages=["pylox", "pylox"],
      package_dir={"pylox": "pylox"},
      include_package_data=True,
      #entry_points={'console_scripts': ['htmlify = src.htmlify:main']},
      zip_safe=False)
