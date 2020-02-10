import csv
import io
import json

import pulp


COLUMN_HEADERS = ['library',
                  'formula',
                  'cost',
                  'status',
                  'type',
                  'item',
                  'amount',
                  'minimum',
                  'maximum']


class Nutrient():
    def __init__(self, name, unit=None):
        """Create a Nutrient
        
        Args:
            name (str): name of the nutrient
            unit (str, optional): unit of the nutrient, not yet implemented. Defaults to None.
        """
        self.name = name
        self.unit = unit

    def encode(self):
        return self.__dict__

    def decode(self):
        pass


class IngredientNutrient():
    def __init__(self, nutrient, amount=None):
        """Nutrient with amount for use in an ingredient
        
        Args:
            nutrient (Nutrient): nutrient to link
            amount (float, optional): amount of the nutrient. Defaults to None.
        """
        self.nutrient = nutrient
        self.amount = amount

    @property
    def name(self):
        return self.nutrient.name

    def encode(self):
        return {'name': self.name,
                'amount': self.amount}

    def decode(self):
        pass


class Ingredient():
    def __init__(self, name, amount=None, cost=None, nutrients=None):
        """Create an Ingredient
        
        Args:
            name (str): name of the ingredient
            amount (float, optional): amount of th eingredient, not yet implemented. Defaults to None.
            cost (float, optional): cost of the ingredient. Defaults to None.
            nutrients (dict, optional): formatted {[Nutrient]: amount}. Defaults to None.
        """
        self.name = name
        self.amount = amount
        self.cost = cost
        self.nutrients = []
        if nutrients:
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


class BoundNutrient():
    def __init__(self, nutrient, amount=None, minimum=0, maximum=None):
        """Nutrient with constraints and amount
        
        Args:
            nutrient (Nutrient): nutrient
            amount (float, optional): amount of the nutrient. Defaults to None.
            minimum (float, optional): minimum amount to use in the formula. Defaults to 0.
            maximum (float, optional): maximum amount to use in the formula. Defaults to None.
        """
        self.nutrient = nutrient
        self.amount = amount
        self.minimum = minimum
        self.maximum = maximum

    @property
    def name(self):
        return self.nutrient.name

    def encode(self):
        return {'name': self.name,
                'amount': self.amount,
                'minimum': self.minimum,
                'maximum': self.maximum}

    def decode(self):
        pass


class BoundIngredient():
    def __init__(self, ingredient, amount=None, minimum=0, maximum=None):
        """Ingredient with constraints and amount
        
        Args:
            ingredient (Ingredient): ingredient
            amount (float, optional): amount of the ingredient. Defaults to None.
            minimum (float, optional): minimum amount to use in the formula. Defaults to 0.
            maximum (float, optional): maximum amount to use in the formula. Defaults to None.
        """
        self.ingredient = ingredient
        self.amount = amount
        self.minimum = minimum
        self.maximum = maximum

    @property
    def name(self):
        return self.ingredient.name

    @property
    def cost(self):
        return self.ingredient.cost

    @property
    def nutrients(self):
        return self.ingredient.nutrients

    def encode(self):
        return {'name': self.name,
                'amount': self.amount,
                'minimum': self.minimum,
                'maximum': self.maximum}

    def decode(self):
        pass


class Formula():
    def __init__(self, name, batch_size=1):
        """Crate a Formula

        Args:
            name (str): name of the formula
            batch_size (float, optional): size of the batch, used for optimization
                                          all ingredient constraints must apply. Defaults to 1.
        """
        self.name = name
        self.batch_size = batch_size
        self.cost = 0
        self.ingredients = []
        self.nutrients = []
        self.problem = None
        self.status = 'Unoptimized'

    def add_ingredient(self, ingredient, amount=None, minimum=0, maximum=None):
        """Add an ingredient with bounds to the formula

        Args:
            ingredient (BoundIngredient): ingredient to add
            amount (float, optional): amount of the ingredient. Defaults to None.
            minimum (float, optional): minimum amount to use in the formula. Defaults to 0.
            maximum (float, optional): maximum amount to use in the formula. Defaults to None.
        """
        self.ingredients.append(BoundIngredient(
            ingredient, amount, minimum, maximum))

    def add_ingredients(self, ingredients):
        """Add a dict of ingredients

        Args:
            ingredients (dict): formatted {[Ingredient]: amount}
        """
        for ingredient, (minimum, maximum) in ingredients.items():
            self.add_ingredient(ingredient, minimum=minimum, maximum=maximum)

    def add_nutrient(self, nutrient, amount=None, minimum=0, maximum=None):
        """Add an nutrient with bounds to the formula

        Args:
            nutrient (BoundNutrient): nutrient to add
            amount (float, optional): amount of the nutrient Defaults to None.
            minimum (float, optional): minimum amount to use in the formula. Defaults to 0.
            maximum (float, optional): maximum amount to use in the formula. Defaults to None.
        """
        self.nutrients.append(BoundNutrient(
            nutrient, amount, minimum, maximum))

    def optimize(self):
        """Optimize the formula

        TODO:
            add exact ingredient amount constraints
        """

        # create problem varialbes with bounds associated to ingredients
        variables = {i: pulp.LpVariable(name=i.name,
                                        lowBound=i.minimum,
                                        upBound=i.maximum)
                     for i in self.ingredients}

        prob = pulp.LpProblem(self.name, pulp.LpMinimize)

        # minimize cost objective function
        prob += pulp.lpSum([variables[i] * i.cost
                            for i in self.ingredients
                            if i.cost])
        # total function (uses ingredient bounds from variables)
        prob += pulp.lpSum([variables[i]
                            for i in self.ingredients]) == self.batch_size, 'total'

        # nutrient bounds
        for nutrient in self.nutrients:
            # minimum
            if nutrient.minimum:
                minimum = pulp.lpSum([n.amount * variables[i]
                                      for i in self.ingredients
                                      for n in i.nutrients
                                      if n.name == nutrient.name])
                prob += minimum / \
                    self.batch_size >= nutrient.minimum, f'min_{nutrient.name}'
            # maximum
            if nutrient.maximum:
                maximum = pulp.lpSum([n.amount * variables[i]
                                      for i in self.ingredients
                                      for n in i.nutrients
                                      if n.name == nutrient.name])
                prob += maximum / \
                    self.batch_size <= nutrient.maximum, f'max_{nutrient.name}'

        prob.solve()
        self.status = pulp.LpStatus[prob.status]
        self.problem = prob

        # set ingredient amounts from problem output
        for ingredient, variable in variables.items():
            ingredient.amount = variable.varValue
            self.cost += ingredient.cost * \
                (ingredient.amount / self.batch_size)

        # set nutrient amounts from problem output
        for nutrient in self.nutrients:
            nutrient.amount = sum([i.amount * n.amount
                                   for i in self.ingredients
                                   for n in i.nutrients
                                   if n.name == nutrient.name]) / self.batch_size

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
        exclude = ['problem']
        return {k: v for k, v in self.__dict__.items() if k not in exclude}

    def decode(self):
        pass

    def to_json(self, indent=None):
        return json.dumps(self, default=lambda o: o.encode(), indent=indent)

    def to_csv(self, library_name=None, write_header=True):
        """Return a csv representation of the Formula

        Args:
            library_name (str, optional): name of the library. Defaults to None.
            write_header (bool, optional): whether or not to write the header row. Defaults to True.

        Returns:
            str: csv table representation
        """
        output = io.StringIO()
        writer = csv.writer(output)
        if write_header:
            writer.writerow(COLUMN_HEADERS)
        writer.writerows([[library_name if library_name else 'default',
                           self.name,
                           self.cost,
                           self.status,
                           'ingredient',
                           i.name,
                           i.amount,
                           i.minimum,
                           i.maximum]
                          for i in self.ingredients])
        writer.writerows([[library_name if library_name else 'default',
                           self.name,
                           self.cost,
                           self.status,
                           'nutrient',
                           n.name,
                           n.amount,
                           n.minimum,
                           n.maximum]
                          for n in self.nutrients])
        return output.getvalue()

    def save_csv(self, filename, library_name=None):
        """Save the Formula as a csv, overwrites any existing file with the same name

        Args:
            filename (str): name of the file
            library_name (str, optional): name of the library. Defaults to None.
        """
        with open(filename, 'w', newline='') as file:
            file.write(self.to_csv(library_name=library_name, write_header=True))


class FormulaLibrary():
    """A library of nutrients, ingredients, and formulas
    """

    def __init__(self, name, units=None, nutrients=None, ingredients=None, formulas=None):
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
        # TODO maybe
        pass

    def to_json(self):
        return json.dumps(self, default=lambda o: o.encode(), indent=4)

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
            csv_string += formula.to_csv(library_name=self.name, write_header=False)
        return csv_string

    def save_csv(self, filename):
        """Save the FormulaLibrary as a csv, overwrites any existing file with the same name

        Args:
            filename (str): name of the file
        """
        with open(filename, 'w', newline='') as file:
            file.write(self.to_csv())
