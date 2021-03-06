from setuptools import setup, find_packages

# Get version without importing, which avoids dependency issues
exec(compile(open("pylox/version.py").read(),
             "pylox/version.py", "exec"))

setup(name="pylox",
      description="Python Lox interpreter.",
      version=eval("__version__"),
      author="Matt Mulholland",
      author_email="mulhodm@gmail.com",
      packages=find_packages(exclude=["tool", "tests"]),
      include_package_data=True,
      entry_points={"console_scripts":
                        ["plox = pylox.pylox_interpreter:main",
                         "pylox_generate_ast = tool.generate_ast:main"]},
      zip_safe=False)
