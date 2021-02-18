from setuptools import setup

setup(
    name="coop1",
    version="0.1",
    packages=["coop1"],
    include_package_data=True,
    # TODO requirements
    # install_requires=["Click", "pytest", "toml", "spidev", "colorlog"],
    entry_points="""
        [console_scripts]
        coop1=coop1.home:main
    """,
)