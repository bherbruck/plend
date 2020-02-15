# plend documentation

## Main Classes
- [Formula](#Formula)
- [Nutrient](#Nutrient)
- [Ingredient](#Ingredient)
- [FormulaLibrary](#FormulaLibrary)

---


## Formula
---
### class plend.Formula(name, code=None, batch_size=1)

#### add_ingredient(ingredient, amount=None, minimum=0, maximum=None)
Add an ingredient with bounds to the formula

Args:

    ingredient (BoundIngredient): ingredient to add
    amount (float, optional): amount of the ingredient. Defaults to None.
    minimum (float, optional): minimum amount to use in the formula. Defaults to 0.
    maximum (float, optional): maximum amount to use in the formula. Defaults to None.


#### add_ingredients(ingredients)
Add a dict of ingredients

Args:

    ingredients (dict): formatted {[Ingredient]: amount}


#### add_nutrient(nutrient, amount=None, minimum=0, maximum=None)
Add an nutrient with bounds to the formula

Args:

    nutrient (BoundNutrient): nutrient to add
    amount (float, optional): amount of the nutrient Defaults to None.
    minimum (float, optional): minimum amount to use in the formula. Defaults to 0.
    maximum (float, optional): maximum amount to use in the formula. Defaults to None.

#### optimize()
Optimize the formula


#### save_csv(filename, library_name=None)
Save the Formula as a csv, overwrites any existing file with the same name

Args:

    filename (str): name of the file
    library_name (str, optional): name of the library. Defaults to None.


#### show_output()
Prints the problem’s output


#### show_problem()
Prints the problem’s function


#### to_csv(library_name=None, write_header=True)
Return a csv representation of the Formula

Args:

    library_name (str, optional): name of the library. Defaults to None.
    write_header (bool, optional): whether or not to write the header row. Defaults to True.

Returns:

    str: csv table representation


#### to_json(indent=None)

### class plend.FormulaLibrary(name, units=None, nutrients=None, ingredients=None, formulas=None)
Bases: `object`

A library of nutrients, ingredients, and formulas


#### optimize()

#### save_csv(filename)
Save the FormulaLibrary as a csv, overwrites any existing file with the same name

Args:

    filename (str): name of the file


#### to_csv()
Return a csv representation of the FormulaLibrary

Returns:

    str: csv table representation


#### to_json()

### class plend.Ingredient(name, code=None, amount=None, cost=None, nutrients=None)
Bases: `object`


#### add_nutrient(nutrient, amount)
Add a single nutrient

Args:

    nutrient (Nutrient): nutrient to link
    amount (float): amount of the nutrient in the ingredient


#### add_nutrients(nutrients)
Add a dict of nutrients

Args:

    nutrients (dict): formatted {[Nutrient]: amount}


### class plend.IngredientNutrient(nutrient, amount=None)

### class plend.Nutrient(name, code=None, unit=None)



### class plend.BoundIngredient(ingredient, amount=None, minimum=0, maximum=None)

 BoundIngredient is an internal class used to link an ingredient with amount, minimum, and maximum to a [Formula](#Formula)

### class plend.BoundNutrient(nutrient, amount=None, minimum=0, maximum=None)

BoundNutrient is an internal class used to link an nutrient with amount, minimum, and maximum to a [Formula](#Formula)