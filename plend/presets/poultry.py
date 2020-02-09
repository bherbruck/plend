from plend import Nutrient, Ingredient, Formula


calorie = 'kcal/kg'
percent = '%'
kilogram = 'kg'

energy = Nutrient('Energy', unit=calorie)
protein = Nutrient('Protein')
fiber = Nutrient('Fiber')
calcium = Nutrient('Calcium')
phosphorous = Nutrient('Phosphorous')
sodium = Nutrient('Sodium')
chloride = Nutrient('Chloride')
methionine = Nutrient('Methionine')
lysine = Nutrient('Lysine')

corn = Ingredient('Corn', cost=50, nutrients={
    energy: 3300,
    protein: 7.5,
    fiber: 2.5,
    calcium: 0.01,
    phosphorous: 0.13,
    sodium: 0.05,
    chloride: 0.05,
    methionine: 0.2,
    lysine: 0.2,
})

wheat = Ingredient('Wheat', cost=50, nutrients={
    energy: 3150,
    protein: 12,
    fiber: 2.7,
    calcium: 0.05,
    phosphorous: 0.2,
    sodium: 0.09,
    chloride: 0.08,
    methionine: 0.2,
    lysine: 0.49,
})

soybean_meal = Ingredient('Soybean Meal', cost=100, nutrients={
    energy: 2550,
    protein: 48,
    fiber: 3,
    calcium: 0.2,
    phosphorous: 0.37,
    sodium: 0.05,
    chloride: 0.05,
    methionine: 0.72,
    lysine: 3.22,
})

meat_meal = Ingredient('Meat Meal', cost=75, nutrients={
    energy: 2450,
    protein: 50,
    calcium: 8,
    phosphorous: 4,
    sodium: 0.5,
    chloride: 0.9,
    methionine: 0.71,
    lysine: 2.68,
})

oil = Ingredient('Oil', cost=150, nutrients={
    energy: 8800,
})

limestone = Ingredient('Limestone', cost=40, nutrients={
    calcium: 38
})
