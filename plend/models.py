from typing import List, Dict, Any, Tuple

import pulp
from . import utils


class Item:
    item_type = None

    def __init__(self, name: str, code: str = None):
        """Create an Item

        Args:
            name (str): name of the item
            code (str): code of the item
        """
        self.name = name
        self.code = code or utils.clean_name(name)


class Nutrient(Item):
    item_type = 'nutrient'

    def __init__(self, name: str, code: str = None, unit: str = None):
        """Create a Nutrient

        Args:
            name (str): name of the nutrient
            unit (str, optional): unit of the nutrient. Defaults to None.
        """
        self.name = name
        self.code = code or utils.clean_name(name)
        self.unit = unit


class IngredientNutrient:
    def __init__(self, nutrient: Nutrient, amount: float = None):
        """Nutrient with amount for use in an ingredient
        One-to-one relationship with Ingredient

        Args:
            nutrient (Nutrient): nutrient to link
            amount (float, optional): amount of the nutrient. Defaults to None.
        """
        self.nutrient = nutrient
        self.amount = amount

    @property
    def name(self) -> str:
        return self.nutrient.name

    @property
    def code(self) -> str:
        return self.nutrient.code

    def __eq__(self, other: Nutrient) -> bool:
        return self.nutrient == other


class Ingredient(Item):
    item_type = 'ingredient'

    def __init__(self, name: str, code: str = None, cost: float = 0,
                 nutrients: Dict[Nutrient, float] = None):
        """Create an Ingredient

        Args:
            name (str): name of the ingredient
            code (str): code of the ingredient
            amount (float, optional): amount of the ingredient. 
                Defaults to None.
            cost (float, optional): cost of the ingredient. Defaults to None.
            nutrients (dict, optional): formatted {[Nutrient]: amount}. 
                Defaults to None.
        """
        self.name = name
        self.code = code or utils.clean_name(name)
        self.cost = cost
        self.nutrients = []
        if nutrients is not None:
            self.add_nutrients(nutrients)

    def add_nutrient(self, nutrient: Nutrient, amount: float):
        """Add a single nutrient

        Args:
            nutrient (Nutrient): nutrient to link
            amount (float): amount of the nutrient in the ingredient
        """
        self.nutrients.append(IngredientNutrient(nutrient, amount))

    def add_nutrients(self, nutrients: Dict[Nutrient, float]):
        """Add a dict of nutrients

        Args:
            nutrients (dict): formatted {[Nutrient]: amount}
        """
        for nutrient, amount in nutrients.items():
            self.add_nutrient(nutrient, amount)


class BoundItem:
    def __init__(self, item: Item, amount: float = None, minimum: float = 0,
                 maximum: float = None, formula: Any = None):
        self.item = item
        self.amount = amount
        self.minimum = minimum
        self.maximum = maximum
        self.formula = formula

    @property
    def name(self) -> str:
        return self.item.name

    @property
    def code(self) -> str:
        return self.item.code

    @property
    def item_type(self) -> str:
        return self.item.item_type

    def __eq__(self, other: object) -> bool:
        return self.item == other


class FormulaNutrient(BoundItem):
    def __init__(self, nutrient: Nutrient, amount: float = None,
                 minimum: float = 0,  maximum: float = None,
                 formula: Any = None):
        """Nutrient with constraints and amount
        One-to-one relationship with Nutrient

        Args:
            nutrient (Nutrient): nutrient
            amount (float, optional): amount of the nutrient. Defaults to None.
            minimum (float, optional): minimum amount to use in the formula.
                Defaults to 0.
            maximum (float, optional): maximum amount to use in the formula.
                Defaults to None.
        """
        self.item = nutrient
        self.amount = amount
        self.minimum = minimum
        self.maximum = maximum
        self.formula = formula

    @property
    def nutrient(self) -> Nutrient:
        return self.item


class FormulaIngredient(BoundItem):
    def __init__(self, ingredient: Ingredient, amount: float = None,
                 minimum: float = 0, maximum: float = None,
                 formula: Any = None):
        """Ingredient with constraints and amount
        One-to-one relationship with Ingredient

        Args:
            ingredient (Ingredient): ingredient
            amount (float, optional): amount of the ingredient.
                Defaults to None.
            minimum (float, optional): minimum amount to use in the formula.
                Defaults to 0.
            maximum (float, optional): maximum amount to use in the formula.
                Defaults to None.
        """
        self.item = ingredient
        self.amount = amount
        self.minimum = minimum
        self.maximum = maximum
        self.formula = formula

    @property
    def ingredient(self) -> Ingredient:
        return self.item

    @property
    def cost(self) -> float:
        return self.ingredient.cost

    @property
    def nutrients(self) -> List[IngredientNutrient]:
        return self.ingredient.nutrients

    @property
    def percent(self) -> float:
        if self.formula and self.formula.batch_size and self.amount:
            return float(self.amount) / float(self.formula.batch_size)
        else:
            return None

    @property
    def batch_size(self) -> float:
        if self.formula and self.formula.batch_size and self.amount:
            return self.formula.batch_size
        else:
            return None

    @property
    def unit(self) -> str:
        if self.formula:
            return self.formula.unit

    def get_contribution(self, nutrient: Nutrient) -> float:
        """Get the nutrient contribution of the Ingredient to its Formula

        Args:
            nutrient (Nutrient): nutrient to get contribution

        Returns:
            contribution (float)
        """
        if self.percent:
            nut = next((n for n in self.nutrients if n.nutrient == nutrient),
                       None)
            if nut:
                return self.percent * nut.amount
            else:
                return None
        else:
            return None

    def __hash__(self) -> int:
        return id(self)


class Formula:
    def __init__(self, name: str, code: str = None, batch_size: float = 1,
                 unit: str = None):
        """Create a Formula

        Args:
            name (str): name of the formula
            code (str): code of the formula
            batch_size (float, optional): size of the batch,
                used for optimization all ingredient constraints must apply.
                Defaults to 1.

        TODO:
            Write tests for overlapping ingredients/nutrients
        """
        self.name = name
        self.code = code or utils.clean_name(name)
        self.batch_size = batch_size
        self.unit = unit
        self.cost = 0
        self.ingredients = []
        self.nutrients = []
        self.variables = {}
        self.problem = None
        self.status = 'Unsolved'
        self.solver = FormulaSolver(self)

    @property
    def items(self) -> List[BoundItem]:
        return self.ingredients + self.nutrients

    def add_ingredient(self, ingredient: Ingredient, amount: float = None,
                       minimum: float = 0, maximum: float = None):
        """Add an ingredient with bounds to the formula, update if it exists

        Args:
            ingredient (FormulaIngredient): ingredient to add
            amount (float, optional): amount of the ingredient.
                Defaults to None.
            minimum (float, optional): minimum amount to use in the formula.
                Defaults to 0.
            maximum (float, optional): maximum amount to use in the formula.
                Defaults to None.
        """
        bi = next((i for i in self.ingredients if i.ingredient == ingredient),
                  None)
        # update the nutrient if it already exists
        if bi:
            bi.amount = amount
            bi.minimum = minimum
            bi.maximum = maximum
            bi.formula = self
        # add a new nutrient if it does not exist
        else:
            self.ingredients.append(FormulaIngredient(
                ingredient, amount, minimum, maximum, formula=self))

    def add_ingredients(self, ingredient_dict: Dict[Ingredient, Tuple[float]]):
        """Add a dict of ingredients

        Args:
            ingredient_dict (dict): formatted {Ingredient: (minimum, maximum)}
        """
        for ingredient, (minimum, maximum) in ingredient_dict.items():
            self.add_ingredient(ingredient, minimum=minimum,
                                maximum=maximum)

    def add_nutrient(self, nutrient: Nutrient, amount: float = None,
                     minimum: float = 0, maximum: float = None):
        """Add an nutrient with bounds to the formula, update if it exists

        Args:
            nutrient (FormulaNutrient): nutrient to add
            amount (float, optional): amount of the nutrient Defaults to None.
            minimum (float, optional): minimum amount to use in the formula.
                Defaults to 0.
            maximum (float, optional): maximum amount to use in the formula.
                Defaults to None.
        """
        # check if the nutrient exists for updating
        bn = next((n for n in self.nutrients if n.nutrient == nutrient), None)
        # update the nutrient if it already exists
        if bn:
            bn.amount = amount
            bn.minimum = minimum
            bn.maximum = maximum
            bn.formula = self
        # add a new nutrient if it does not exist
        else:
            self.nutrients.append(FormulaNutrient(
                nutrient, amount, minimum, maximum, formula=self))

    def add_nutrients(self, nutrient_dict: Dict[Nutrient, Tuple[float]]):
        """Add a dict of nutrient

        Args:
            nutrient (dict): formatted {Ingredient: (minimum, maximum)}
        """
        for nutrient, (minimum, maximum) in nutrient_dict.items():
            self.add_nutrient(nutrient, minimum=minimum, maximum=maximum)

    def derive_from(self, formula: Any):
        """Copy the ingredients and nutrients from another formula.
        Does NOT overwrite existing items.

        Args:
            formula (Formula): Formula to derive from.
        """
        for ing in formula.ingredients:
            self.add_ingredient(ingredient=ing.ingredient, amount=ing.amount,
                                minimum=ing.minimum, maximum=ing.maximum)
        for nut in formula.nutrients:
            self.add_nutrient(nutrient=nut.nutrient, amount=nut.amount,
                              minimum=nut.minimum, maximum=nut.maximum)

    def optimize(self):
        """Optimize the formula by creating and solving the formula problem
        """
        self.solver.optimize()


class FormulaSolver:
    def __init__(self, formula: Formula = None):
        self.formula = formula

    def create_problem(self, formula: Formula = None):
        """Create the PuLP problem to be solved
        """
        if formula is None:
            formula = self.formula
        # create problem variables with bounds associated to ingredients
        variables = {i: pulp.LpVariable(name=i.name,
                                        lowBound=i.minimum,
                                        upBound=i.maximum)
                     for i in formula.ingredients}

        prob = pulp.LpProblem(formula.name, pulp.LpMinimize)

        # minimize cost objective function
        prob += pulp.lpSum([variables[i] * i.cost
                            for i in formula.ingredients
                            if i.cost])
        # total function (uses ingredient bounds from variables)
        prob += pulp.lpSum([variables[i]
                            for i in formula.ingredients]) \
            == formula.batch_size, 'total'

        # nutrient bounds
        for nutrient in formula.nutrients:
            # minimum
            if nutrient.minimum:
                minimum = pulp.lpSum([n.amount * variables[i]
                                      for i in formula.ingredients
                                      for n in i.nutrients
                                      if n.name == nutrient.name])
                prob += minimum / formula.batch_size \
                    >= nutrient.minimum, f'min_{nutrient.name}'
            # maximum
            if nutrient.maximum:
                maximum = pulp.lpSum([n.amount * variables[i]
                                      for i in formula.ingredients
                                      for n in i.nutrients
                                      if n.name == nutrient.name])
                prob += maximum / formula.batch_size \
                    <= nutrient.maximum, f'max_{nutrient.name}'
        formula.variables = variables
        formula.problem = prob

    def solve_problem(self, formula: Formula = None):
        """Solve the problem
        """
        if formula is None:
            formula = self.formula
        if formula.problem is None:
            self.create_problem(formula)
        formula.problem.solve()
        formula.status = pulp.LpStatus[formula.problem.status]

        # set ingredient amounts from problem output
        for ingredient, variable in formula.variables.items():
            ingredient.amount = variable.varValue
            formula.cost += ingredient.cost * \
                (ingredient.amount / formula.batch_size)

        # set nutrient amounts from problem output
        for nutrient in formula.nutrients:
            nutrient.amount = sum([i.amount * n.amount
                                   for i in formula.ingredients
                                   for n in i.nutrients
                                   if n.name == nutrient.name]) \
                / formula.batch_size

    def optimize(self, formula: Formula = None):
        """Optimize the formula by creating and solving the formula problem
        """
        if formula is None:
            formula = self.formula
        self.create_problem(formula)
        self.solve_problem(formula)


class FormulaLibrary:
    """A library of nutrients, ingredients, and formulas
    """

    def __init__(self, name: str, formula_unit: str = None,
                 nutrients: List[Nutrient] = None,
                 ingredients: List[Ingredient] = None,
                 formulas: List[Formula] = None):
        """[summary]

        Args:
            name (str): name of the formula library
            units (list[unit], optional): Defaults to None.
            nutrients (list[nutrient], optional):  Defaults to None.
            ingredients (list[ingredient], optional): Defaults to None.
            formulas (list[formula], optional): Defaults to None.
        """
        self.name = name
        self.formula_unit = formula_unit
        self.nutrients = nutrients or []
        self.ingredients = ingredients or []
        self.formulas = formulas or []

    def add_nutrients(self, nutrients: List[Nutrient]):
        self.nutrients += nutrients

    def add_ingredients(self, ingredients: List[Ingredient]):
        self.ingredients += ingredients

    def add_formulas(self, formulas: List[Formula]):
        self.formulas += formulas

    def optimize(self):
        for formula in self.formulas:
            formula.optimize()
