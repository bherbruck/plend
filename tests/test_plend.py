from plend import Item, Formula, FormulaLibrary, Ingredient, Nutrient
from plend.presets.poultry import *
from plend.utils import clean_name


test_data = {
    'nutrients': [
        {'name': 'moisture'},
        {'name': 'carbon', 'code': 'cbn'}
    ],
    'ingredients': [
        {'name': 'water', 'nutrients': [
            {'name': 'moisture', 'amount': 100},
        ]},
        {'name': 'dirt', 'code': '123456', 'nutrients': [
            {'name': 'moisture', 'amount': 0.75},
            {'name': 'carbon', 'amount': 0.15}
        ]},
    ],
    'formulas': [
        {
            'name': 'mud pie',
            'nutrients': [

            ],
            'ingredients': []
        }
    ]
}


def test_Item_init():
    item = Item('item 1')
    assert item.name == 'item 1'
    assert item.code == 'item_1'


def test_Nutrient_init():
    for i in test_data['nutrients']:
        name = i.get('name')
        code = i.get('code')
        item = Nutrient(name, code)
        assert item.name == name
        assert item.code == code or clean_name(name)


def test_Ingredient():
    for i in test_data['ingredients']:
        name = i.get('name')
        code = i.get('code')
        item = Ingredient(name, code)
        assert item.name == name
        assert item.code == code or clean_name(name)


def test_solve_formula():
    carbon = Nutrient('Carbon')
    moisture = Nutrient('Moisture', code='wetness')

    dirt = Ingredient('Dirt', cost=10, nutrients={
        carbon: 0.85,
        moisture: 0.1
    })
    water = Ingredient('Water', cost=15, nutrients={
        moisture: 1
    })

    mud = Formula('Mud', batch_size=2000)
    mud.add_ingredients({
        dirt:  (0, None),
        water: (0, None)
    })
    mud.add_nutrients({
        carbon:   (0.5, None),
        moisture: (0.2, None)
    })

    mud.optimize()

    print(mud.problem)

    print(mud.status)
    for ingredient in mud.ingredients:
        assert ingredient.amount >= ingredient.minimum
        assert ingredient.amount <= ingredient.maximum
        print(ingredient.maximum)

    for nutrient in mud.nutrients:
        total_nutrient = sum([i.amount * n.amount / mud.batch_size
                              for i in mud.ingredients
                              for n in i.nutrients
                              if n.name == nutrient.name])
        assert total_nutrient >= nutrient.minimum
        assert total_nutrient <= (nutrient.maximum or total_nutrient)
