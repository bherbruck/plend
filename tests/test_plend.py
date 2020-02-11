import unittest

from plend import Formula, FormulaLibrary, Ingredient, Nutrient
from plend.presets.poultry import *


class TestFormulaLibrary(unittest.TestCase):

    def setUp(self):
        self.flib_csv = """library_name,formula_name,formula_code,formula_cost,formula_status,item_type,item_name,item_code,item_amount,item_minimum,item_maximum
Poultry,Starter,,0,Unoptimized,ingredient,Corn,,,1,
Poultry,Starter,,0,Unoptimized,ingredient,Soybean Meal,,,0,
Poultry,Starter,,0,Unoptimized,ingredient,Oil,,,0,5
Poultry,Starter,,0,Unoptimized,ingredient,Limestone,,,0,
Poultry,Starter,,0,Unoptimized,ingredient,Meat Meal,,,0,10
Poultry,Starter,,0,Unoptimized,nutrient,Energy,,,3000,
Poultry,Starter,,0,Unoptimized,nutrient,Protein,,,20,
Poultry,Starter,,0,Unoptimized,nutrient,Fiber,,,0,
Poultry,Starter,,0,Unoptimized,nutrient,Calcium,,,4,5
Poultry,Finisher,,0,Unoptimized,ingredient,Corn,,,1,
Poultry,Finisher,,0,Unoptimized,ingredient,Soybean Meal,,,0,
Poultry,Finisher,,0,Unoptimized,ingredient,Oil,,,0,5
Poultry,Finisher,,0,Unoptimized,ingredient,Limestone,,,0,
Poultry,Finisher,,0,Unoptimized,ingredient,Meat Meal,,,0,10
Poultry,Finisher,,0,Unoptimized,nutrient,Energy,,,3000,
Poultry,Finisher,,0,Unoptimized,nutrient,Protein,,,20,
Poultry,Finisher,,0,Unoptimized,nutrient,Fiber,,,0,
Poultry,Finisher,,0,Unoptimized,nutrient,Calcium,,,4,5"""

        self.starter_csv = """library_name,formula_name,formula_code,formula_cost,formula_status,item_type,item_name,item_code,item_amount,item_minimum,item_maximum
default,Starter,,0,Unoptimized,ingredient,Corn,,,1,
default,Starter,,0,Unoptimized,ingredient,Soybean Meal,,,0,
default,Starter,,0,Unoptimized,ingredient,Oil,,,0,5
default,Starter,,0,Unoptimized,ingredient,Limestone,,,0,
default,Starter,,0,Unoptimized,ingredient,Meat Meal,,,0,10
default,Starter,,0,Unoptimized,nutrient,Energy,,,3000,
default,Starter,,0,Unoptimized,nutrient,Protein,,,20,
default,Starter,,0,Unoptimized,nutrient,Fiber,,,0,
default,Starter,,0,Unoptimized,nutrient,Calcium,,,4,5"""

        self.starter = Formula(name='Starter', batch_size=100)
        self.starter.add_ingredient(corn, minimum=1)
        self.starter.add_ingredient(soybean_meal)
        self.starter.add_ingredient(oil, maximum=5)
        self.starter.add_ingredient(limestone)
        self.starter.add_ingredient(meat_meal, maximum=10)
        self.starter.add_nutrient(energy, minimum=3000)
        self.starter.add_nutrient(protein, minimum=20)
        self.starter.add_nutrient(fiber)
        self.starter.add_nutrient(calcium, minimum=4, maximum=5)

        self.finisher = Formula(name='Finisher', batch_size=100)
        self.finisher.add_ingredient(corn, minimum=1)
        self.finisher.add_ingredient(soybean_meal)
        self.finisher.add_ingredient(oil, maximum=5)
        self.finisher.add_ingredient(limestone)
        self.finisher.add_ingredient(meat_meal, maximum=10)
        self.finisher.add_nutrient(energy, minimum=3000)
        self.finisher.add_nutrient(protein, minimum=20)
        self.finisher.add_nutrient(fiber)
        self.finisher.add_nutrient(calcium, minimum=4, maximum=5)

        self.flib = FormulaLibrary(name='Poultry')
        self.flib.add_formulas(self.starter, self.finisher)

        self.starter_out = self.starter.to_csv()
        self.finisher_out = self.finisher.to_csv()
        self.flib_out = self.flib.to_csv()

    def test_FormulaLibrary_to_csv(self):
        self.compare_csv(self.flib_out.splitlines(),
                         self.flib_csv.splitlines())

    def test_Formula_to_csv(self):
        self.compare_csv(self.starter_out.splitlines(),
                         self.starter_csv.splitlines())

    def compare_csv(self, csv1, csv2):
        for line in [(x, y) for x, y in zip(csv1, csv2)]:
            self.assertEqual(line[0], line[1])


if __name__ == '__main__':
    unittest.main()
