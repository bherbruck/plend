import copy
import csv
import io
import json

import pulp


COLUMN_HEADERS = ['library_name',
                  'formula_name',
                  'formula_code',
                  'formula_cost',
                  'formula_status',
                  'item_type',
                  'item_name',
                  'item_code',
                  'item_amount',
                  'item_minimum',
                  'item_maximum']


class Nutrient:
    def __init__(self, name, code=None, unit=None):
        """Create a Nutrient

        Args:
            name (str): name of the nutrient
            unit (str, optional): unit of the nutrient. Defaults to None.
        """
        self.name = name
        self.code = code
        self.unit = unit

    def encode(self):
        return self.__dict__

    def decode(self):
        pass


class IngredientNutrient:
    def __init__(self, nutrient, amount=None):
        """Nutrient with amount for use in an ingredient
        One-to-one relationship with Ingredient

        Args:
            nutrient (Nutrient): nutrient to link
            amount (float, optional): amount of the nutrient. Defaults to None.
        """
        self.nutrient = nutrient
        self.amount = amount

    @property
    def name(self):
        return self.nutrient.name

    @property
    def code(self):
        return self.nutrient.code

    def encode(self):
        return {'name': self.name,
                'amount': self.amount}

    def decode(self):
        pass

    def __eq__(self, other):
        return self.nutrient == other

    def __hash__(self):
        return id(self)


class Ingredient:
    def __init__(self, name, code=None, amount=None,
                 cost=0, nutrients=None):
        """Create an Ingredient

        Args:
            name (str): name of the ingredient
            amount (float, optional): amount of the ingredient. 
                Defaults to None.
            cost (float, optional): cost of the ingredient. Defaults to None.
            nutrients (dict, optional): formatted {[Nutrient]: amount}. 
                Defaults to None.
        """
        self.name = name
        self.code = code
        self.amount = amount
        self.cost = cost
        self.nutrients = []
        if nutrients is not None:
            self.add_nutrients(nutrients)

    def add_nutrient(self, nutrient, amount):
        """Add a single nutrient

        Args:
            nutrient (Nutrient): nutrient to link
            amount (float): amount of the nutrient in the ingredient
        """
        self.nutrients.append(IngredientNutrient(nutrient, amount))

    def add_nutrients(self, nutrients):
        """Add a dict of nutrients

        Args:
            nutrients (dict): formatted {[Nutrient]: amount}
        """
        for nutrient, amount in nutrients.items():
            self.add_nutrient(nutrient, amount)

    def encode(self):
        return self.__dict__

    def decode(self):
        pass


class FormulaNutrient:
    def __init__(self, nutrient, amount=None, minimum=0,
                 maximum=None, formula=None):
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
        self.nutrient = nutrient
        self.amount = amount
        self.minimum = minimum
        self.maximum = maximum
        self.formula = formula

    @property
    def name(self):
        return self.nutrient.name

    @property
    def code(self):
        return self.nutrient.code

    def encode(self):
        return {'name': self.name,
                'code': self.code,
                'amount': self.amount,
                'minimum': self.minimum,
                'maximum': self.maximum}

    def decode(self):
        pass

    def __eq__(self, other):
        return self.nutrient == other

    def __hash__(self):
        return id(self)


class FormulaIngredient:
    def __init__(self, ingredient, amount=None, minimum=0,
                 maximum=None, formula=None):
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
        self.ingredient = ingredient
        self.amount = amount
        self.minimum = minimum
        self.maximum = maximum
        self.formula = formula

    @property
    def name(self):
        return self.ingredient.name

    @property
    def code(self):
        return self.ingredient.code

    @property
    def cost(self):
        return self.ingredient.cost

    @property
    def nutrients(self):
        return self.ingredient.nutrients

    @property
    def percent(self):
        if self.formula and self.formula.batch_size and self.amount:
            return float(self.amount) / float(self.formula.batch_size)
        else:
            return None

    @property
    def batch_size(self):
        if self.formula and self.formula.batch_size and self.amount:
            return self.formula.batch_size
        else:
            return None

    @property
    def cost_per_batch(self):
        if self.percent and self.cost:
            return self.percent * self.cost
        else:
            return None

    @property
    def unit(self):
        if self.formula:
            return self.formula.unit

    def get_contribution(self, nutrient):
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

    def encode(self):
        return {'name': self.name,
                'code': self.code,
                'amount': self.amount,
                'minimum': self.minimum,
                'maximum': self.maximum}

    def decode(self):
        pass

    def __eq__(self, other):
        return self.ingredient == other

    def __hash__(self):
        return id(self)


class Formula:
    def __init__(self, name, code=None, batch_size=1, unit=None):
        """Create a Formula

        Args:
            name (str): name of the formula
            code (str): code of the formula
            batch_size (float, optional): size of the batch,
                used for optimization all ingredient constraints must apply.
                Defaults to 1.

        TODO:
            Refactor optimization process
            Add unit to csv output
            Add items property (ingredients and nutrients in one list)
            Write tests for overlapping ingredients/nutrients
        """
        self.name = name
        self.code = code
        self.batch_size = batch_size
        self.unit = unit
        self.cost = 0
        self.ingredients = []
        self.nutrients = []
        self.variables = {}
        self.problem = None
        self.status = 'Unsolved'
        self.solver = FormulaSolver(self)

    def add_ingredient(self, ingredient, amount=None, minimum=0, maximum=None):
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

    def add_ingredients(self, ingredient_dict):
        """Add a dict of ingredients

        Args:
            ingredient_dict (dict): formatted {Ingredient: (minimum, maximum)}
        """
        for ingredient, (minimum, maximum) in ingredient_dict.items():
            self.add_ingredient(ingredient, minimum=minimum,
                                maximum=maximum)

    def add_nutrient(self, nutrient, amount=None, minimum=0, maximum=None):
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

    def add_nutrients(self, nutrient_dict):
        """Add a dict of nutrient

        Args:
            nutrient (dict): formatted {Ingredient: (minimum, maximum)}
        """
        for nutrient, (minimum, maximum) in nutrient_dict.items():
            self.add_nutrient(nutrient, minimum=minimum, maximum=maximum)

    def derive_from(self, formula):
        """Copy the ingredients and nutrients from another formula.
        Does NOT overwrite existing items.

        Args:
            formula (Formula): Formla to derive from.
        """
        for ing in formula.ingredients:
            self.add_ingredient(ingredient=ing.ingredient, amount=ing.amount,
                                minimum=ing.minimum, maximum=ing.maximum)
        for nut in formula.nutrients:
            self.add_nutrient(nutrient=nut.nutrient, amount=nut.amount,
                              minimum=nut.minimum, maximum=nut.maximum)

    def create_problem(self):
        """Create the PuLP problem to be solved
        """
        self.solver.create_problem()

    def solve_problem(self):
        """Solve the problem
        """
        self.solver.solve_problem()

    def optimize(self):
        """Optimize the formula by creating and solving the formula problem
        """
        self.solver.optimize()

    def show_problem(self):
        """Prints the problem's function
        """
        if self.problem:
            print(self.problem)

    def show_output(self):
        """Prints the problem's output
        """
        print(f'Formula: {self.name}')
        print(f'Status: {self.status}')
        if self.problem:
            for variable in self.problem.variables():
                print(f'{variable.name}: {variable.varValue}')

    def encode(self):
        """Encode for json

        Returns:
            dict: json dict representation
        """
        encoded_items = ['name', 'code', 'batch_size', 'cost',
                         'unit', 'ingredients', 'nutrients']
        return {k: v for k, v in self.__dict__.items() if k in encoded_items}

    def decode(self):
        pass

    def to_json(self, indent=None):
        return json.dumps(self, default=lambda o: o.encode(), indent=indent)

    def to_csv(self, library_name=None, write_header=True):
        """Return a csv representation of the Formula

        Args:
            library_name (str, optional): name of the library.
                Defaults to None.
            write_header (bool, optional): whether or not to write the header.
                Defaults to True.

        Returns:
            str: csv table representation
        """
        output = io.StringIO()
        writer = csv.writer(output)
        if write_header:
            writer.writerow(COLUMN_HEADERS)
        writer.writerows([[library_name if library_name else 'default',
                           self.name,
                           self.code,
                           self.cost,
                           self.status,
                           'ingredient',
                           i.name,
                           i.code,
                           i.amount,
                           i.minimum,
                           i.maximum]
                          for i in self.ingredients])
        writer.writerows([[library_name if library_name else 'default',
                           self.name,
                           self.code,
                           self.cost,
                           self.status,
                           'nutrient',
                           n.name,
                           n.code,
                           n.amount,
                           n.minimum,
                           n.maximum]
                          for n in self.nutrients])
        return output.getvalue()

    def save_csv(self, filename, library_name=None):
        """Save the Formula as a csv,
        overwrites any existing file with the same name

        Args:
            filename (str): name of the file
            library_name (str, optional): name of the library.
                Defaults to None.
        """
        with open(filename, 'w', newline='') as file:
            file.write(self.to_csv(
                library_name=library_name, write_header=True))


class FormulaSolver:
    def __init__(self, formula=None):
        self.formula = formula

    def create_problem(self, formula=None):
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

    def solve_problem(self, formula=None):
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

    def optimize(self, formula=None):
        """Optimize the formula by creating and solving the formula problem
        """
        if formula is None:
            formula = self.formula
        self.create_problem(formula)
        self.solve_problem(formula)


class FormulaLibrary:
    """A library of nutrients, ingredients, and formulas
    """

    def __init__(self, name, units=None, nutrients=None,
                 ingredients=None, formulas=None):
        """[summary]

        Args:
            name (str): name of the formula library
            units (list[unit], optional): Defaults to None.
            nutrients (list[nutrient], optional):  Defaults to None.
            ingredients (list[ingredient], optional): Defaults to None.
            formulas (list[formula], optional): Defaults to None.
        """
        self.name = name
        self.units = []
        self.nutrients = []
        self.ingredients = []
        self.formulas = []

    def add_nutrients(self, *nutrients):
        for nutrient in nutrients:
            self.nutrients.append(nutrient)

    def add_ingredients(self, *ingredients):
        for ingredient in ingredients:
            self.ingredients.append(ingredient)

    def add_formulas(self, *formulas):
        for formula in formulas:
            self.formulas.append(formula)

    def optimize(self):
        for formula in self.formulas:
            formula.optimize()

    def encode(self):
        """Encode for json

        Returns:
            dict: json dict representation
        """
        return self.__dict__

    def decode(self):
        pass

    def to_json(self):
        return json.dumps(self, default=lambda o: o.encode(), indent=4)

    def save_json(self, path):
        with open(path, 'r') as file:
            file.write(self.to_json())

    @staticmethod
    def from_json(self, path):
        # TODO
        raise NotImplementedError
        with open(path, 'r') as file:
            data = json.load(file)

    def to_csv(self):
        """Return a csv representation of the FormulaLibrary

        Returns:
            str: csv table representation
        """
        csv_string = ''
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(COLUMN_HEADERS)
        csv_string += output.getvalue()
        for formula in self.formulas:
            csv_string += formula.to_csv(library_name=self.name,
                                         write_header=False)
        return csv_string

    def save_csv(self, path):
        """Save the FormulaLibrary as a csv,
        overwrites any existing file with the same name

        Args:
            filename (str): name of the file
        """
        with open(path, 'w', newline='') as file:
            file.write(self.to_csv())
