import setuptools

with open("requirements.txt") as f:
    requirements = [each.strip() for each in f.readlines()]

setuptools.setup(
    name="diff2HtmlCompare",
    version="0.1.0",
    url="https://github.com/wagoodman/diff2HtmlCompare",
    license="MIT",
    author="wagoodman",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": ["diff2HtmlCompare = diff2HtmlCompare:cmd"]
    },
)
