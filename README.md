# plend

[license-image]: https://img.shields.io/npm/l/make-coverage-badge.svg
[license-url]: https://opensource.org/licenses/MIT

[ci-image]: https://github.com/bherbruck/plend/workflows/Python%20package/badge.svg
[ci-url]: https://github.com/bherbruck/plend/actions?query=workflow%3A%22Python+package%22

[![License][license-image]][license-url]
[![Python package][ci-image]][ci-url]

Plend is a library for performing least cost formulation with Python. Plend uses [PuLP](https://github.com/coin-or/pulp) to solve formula constraint problems.

## Installation

```text
$ pip install git+https://github.com/bherbruck/plend
```

or

```text
$ pip install plend
```

## Examples

```python
from plend import Formula, Ingredient, Nutrient
from plend.presets.poultry import *

# initialize formula
starter = Formula(name='Starter', batch_size=100)

# add ingredient constraints from poultry presets
starter.add_ingredient(corn, minimum=1)
starter.add_ingredient(soybean_meal)
starter.add_ingredient(oil, maximum=5)
starter.add_ingredient(limestone)
starter.add_ingredient(meat_meal, maximum=10)

# add nutrient constraints from poultry presets
starter.add_nutrient(energy, minimum=3000)
starter.add_nutrient(protein, minimum=20)
starter.add_nutrient(fiber)
starter.add_nutrient(calcium, minimum=4, maximum=5)

# optimize the formula
starter.optimize()

# output the formula to a csv
print(starter.to_csv())
```

### outputs:

| library_name | formula_name | formula_code | formula_cost | formula_status | item_type  | item_name    | item_code | item_amount  | item_minimum | item_maximum | 
|--------------|--------------|--------------|--------------|----------------|------------|--------------|-----------|--------------|--------------|--------------| 
| default      | Starter      |              | 67.16379819  | Optimal        | ingredient | Corn         |           | 54.882934    | 1            |              | 
| default      | Starter      |              | 67.16379819  | Optimal        | ingredient | Soybean Meal |           | 22.674542    | 0            |              | 
| default      | Starter      |              | 67.16379819  | Optimal        | ingredient | Oil          |           | 4.1552541    | 0            | 5            | 
| default      | Starter      |              | 67.16379819  | Optimal        | ingredient | Limestone    |           | 8.2872701    | 0            |              | 
| default      | Starter      |              | 67.16379819  | Optimal        | ingredient | Meat Meal    |           | 10.0         | 0            | 10           | 
| default      | Starter      |              | 67.16379819  | Optimal        | nutrient   | Energy       |           | 3000.0000038 | 3000         |              | 
| default      | Starter      |              | 67.16379819  | Optimal        | nutrient   | Protein      |           | 20.00000021  | 20           |              | 
| default      | Starter      |              | 67.16379819  | Optimal        | nutrient   | Fiber        |           | 2.05230961   | 0            |              | 
| default      | Starter      |              | 67.16379819  | Optimal        | nutrient   | Calcium      |           | 4.0000000154 | 4            | 5            | 
