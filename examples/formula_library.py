"""
This example shows how to statically define formulas,
add them to a formula library, optimize them, and
output the results.

"Statically in this context means we are manually
setting the attribures (min and max) for each
ingredient and nutrient rather defining them
dynamically (which is where plend really shines)

TODO: make an example with dynamic formulas
"""


from plend import Nutrient, Ingredient, Formula, FormulaLibrary
from plend.presets.poultry import *

# initialize the starter formula
starter = Formula(name='Starter', code='B1', batch_size=100)
# add ingredients to starter from presets
starter.add_ingredient(corn)
starter.add_ingredient(soybean_meal)
starter.add_ingredient(oil, maximum=10)
# add nutrients to grower from presets
starter.add_ingredient(limestone)
starter.add_ingredient(meat_meal, maximum=10)
starter.add_nutrient(energy, minimum=3010)
starter.add_nutrient(protein, minimum=24)
starter.add_nutrient(fiber)
starter.add_nutrient(calcium, minimum=1)


# initialize the grower formula
grower = Formula(name='Grower', code='B2', batch_size=100)
# add ingredients to grower from presets
grower.add_ingredient(corn)
grower.add_ingredient(soybean_meal)
grower.add_ingredient(oil, maximum=10)
# add nutrients to grower from presets
grower.add_ingredient(limestone)
grower.add_ingredient(meat_meal, maximum=10)
grower.add_nutrient(energy, minimum=3175)
grower.add_nutrient(protein, minimum=22)
grower.add_nutrient(fiber)
grower.add_nutrient(calcium, minimum=0.9)


# initialize the finisher formula
finisher = Formula(name='Finisher', code='B3', batch_size=100)
# add ingredients to finisher from presets
finisher.add_ingredient(corn)
finisher.add_ingredient(soybean_meal)
finisher.add_ingredient(oil, maximum=10)
finisher.add_ingredient(limestone)
finisher.add_ingredient(meat_meal, maximum=10)
# add nutrients to finisher from presets
finisher.add_nutrient(energy, minimum=3225)
finisher.add_nutrient(protein, minimum=20)
finisher.add_nutrient(fiber)
finisher.add_nutrient(calcium, minimum=0.85)


formulas = FormulaLibrary(name='Broiler')
formulas.add_formulas(starter, grower, finisher)

formulas.optimize()

print(formulas.to_csv())
formulas.save_csv('examples/formulas.csv')

"""
this will have the output (this output has been aligned for readability):

library_name ,formula_name ,formula_code ,formula_cost   ,formula_status ,item_type  ,item_name    ,item_code ,item_amount        ,item_minimum ,item_maximum

Broiler      ,Starter      ,B1           ,68.312016841   ,Optimal        ,ingredient ,Corn         ,          ,58.587658          ,0            ,
Broiler      ,Starter      ,B1           ,68.312016841   ,Optimal        ,ingredient ,Soybean Meal ,          ,30.429012          ,0            ,
Broiler      ,Starter      ,B1           ,68.312016841   ,Optimal        ,ingredient ,Oil          ,          ,0.63258515         ,0            ,10
Broiler      ,Starter      ,B1           ,68.312016841   ,Optimal        ,ingredient ,Limestone    ,          ,0.35074529         ,0            ,
Broiler      ,Starter      ,B1           ,68.312016841   ,Optimal        ,ingredient ,Meat Meal    ,          ,10.0               ,0            ,10
Broiler      ,Starter      ,B1           ,68.312016841   ,Optimal        ,nutrient   ,Energy       ,          ,3010.0000132       ,3010         ,
Broiler      ,Starter      ,B1           ,68.312016841   ,Optimal        ,nutrient   ,Protein      ,          ,24.000000110000002 ,24           ,
Broiler      ,Starter      ,B1           ,68.312016841   ,Optimal        ,nutrient   ,Fiber        ,          ,2.37756181         ,0            ,
Broiler      ,Starter      ,B1           ,68.312016841   ,Optimal        ,nutrient   ,Calcium      ,          ,1.0                ,1            ,

Broiler      ,Grower       ,B2           ,68.284483722   ,Optimal        ,ingredient ,Corn         ,          ,61.16353           ,0            ,
Broiler      ,Grower       ,B2           ,68.284483722   ,Optimal        ,ingredient ,Soybean Meal ,          ,25.859865          ,0            ,
Broiler      ,Grower       ,B2           ,68.284483722   ,Optimal        ,ingredient ,Oil          ,          ,2.8656471          ,0            ,10
Broiler      ,Grower       ,B2           ,68.284483722   ,Optimal        ,ingredient ,Limestone    ,          ,0.11095768         ,0            ,
Broiler      ,Grower       ,B2           ,68.284483722   ,Optimal        ,ingredient ,Meat Meal    ,          ,10.0               ,0            ,10
Broiler      ,Grower       ,B2           ,68.284483722   ,Optimal        ,nutrient   ,Energy       ,          ,3174.9999923       ,3175         ,
Broiler      ,Grower       ,B2           ,68.284483722   ,Optimal        ,nutrient   ,Protein      ,          ,21.999999950000003 ,22           ,
Broiler      ,Grower       ,B2           ,68.284483722   ,Optimal        ,nutrient   ,Fiber        ,          ,2.3048842          ,0            ,
Broiler      ,Grower       ,B2           ,68.284483722   ,Optimal        ,nutrient   ,Calcium      ,          ,0.9000000014       ,0.9          ,

Broiler      ,Finisher     ,B3           ,66.00538196504 ,Optimal        ,ingredient ,Corn         ,          ,66.023255          ,0            ,
Broiler      ,Finisher     ,B3           ,66.00538196504 ,Optimal        ,ingredient ,Soybean Meal ,          ,20.933866          ,0            ,
Broiler      ,Finisher     ,B3           ,66.00538196504 ,Optimal        ,ingredient ,Oil          ,          ,3.038852           ,0            ,10
Broiler      ,Finisher     ,B3           ,66.00538196504 ,Optimal        ,ingredient ,Limestone    ,          ,0.0040261626       ,0            ,
Broiler      ,Finisher     ,B3           ,66.00538196504 ,Optimal        ,ingredient ,Meat Meal    ,          ,10.0               ,0            ,10
Broiler      ,Finisher     ,B3           ,66.00538196504 ,Optimal        ,nutrient   ,Energy       ,          ,3224.9999740000003 ,3225         ,
Broiler      ,Finisher     ,B3           ,66.00538196504 ,Optimal        ,nutrient   ,Protein      ,          ,19.999999805       ,20           ,
Broiler      ,Finisher     ,B3           ,66.00538196504 ,Optimal        ,nutrient   ,Fiber        ,          ,2.278597355        ,0            ,
Broiler      ,Finisher     ,B3           ,66.00538196504 ,Optimal        ,nutrient   ,Calcium      ,          ,0.849999999288     ,0.85         ,

"""