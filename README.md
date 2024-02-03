# optionslib module


This is an options pricing library written completely in python. 
The **optionslib** library provides implementations of 
various mathematical finance algorithms, models and methodologies. 

In the **optionslib** world, a product can be priced using a model and market data. 

    Valuation = Product + Model + Market

It supports:

- **Analytical formulae**.
  - Models : Black-Scholes


## Setting up the env:


Project uses poetry to set up the virtual env and run development tools.
To create the virtual env use:

    poetry install --with dev

To install precommit tool: 
    
    poetry run pre-commit install
    
Hooks run the development tools on commit attempt:
- docformatter - nice formatting and wrapping of docstrings (edits files)
- isort - organizes import statements (edits files)
- black - code formatter (edits files)
- pylint - code quality checker (prints errors, need to resolve manually)

If (edits files) checks fail, the code should already be updated. Review and try to recommit. 
To run the checks manually use the following commands:

    poetry run docformatter --in-place -r .
    poetry run isort .
    poetry run black .
    poetry run pylint --rcfile=pylintrc .
    
Configuration of environment and dev tools lives in pyproject.pytoml file. 
Definitions of precommit hooks in .pre-commit-config.yaml.
