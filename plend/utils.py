import csv

from plend import Formula, Ingredient, Nutrient


def read_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        return [row for row in reader]


def csv_to_dict(csv_file, headers=None):
    csv_rows = read_csv(csv_file)
    if not headers:
        headers = csv_rows.pop(0)
    csv_dict = [{header: row[h_idx]
                 for h_idx, header in enumerate(headers)}
                for row in csv_rows]
    return(csv_dict)


def clean_name(name, replacement='_'):
    cleaned_name = ''
    for char in name:
        if char == name[0] and not char.isidentifier():
            cleaned_name += '_' + char
        elif not char.isalnum():
            cleaned_name += '_'
        else:
            cleaned_name += char
    cleaned_name = cleaned_name.lower().replace('__', '_').replace('__', '_')
    if not cleaned_name.isidentifier:
        raise ValueError()
    return cleaned_name


def csv_to_nurtients_py(csv_file, output_file=None, headers=None, nut_pre=''):
    nutrient_dict = csv_to_dict(csv_file, headers)
    lines = [f"{nut_pre}{clean_name(row['Name'])} = Nutrient('{row['Name']}', code='{row['Code']}', unit='{row['Unit']}')"
             for row in nutrient_dict]
    if output_file:
        lines.insert(0, 'from plend import Nutrient')
    output = "\n".join(lines)
    if output_file:
        with open(output_file, 'w') as file:
            file.write(output)
    return output


def csv_to_ingredients_py(csv_file, output_file=None, headers=None, ing_pre=''):
    nutrient_dict = csv_to_dict(csv_file, headers)
    lines = [f"{ing_pre}{clean_name(row['Name'])} = Ingredient('{row['Name']}', code='{row['Code']}', cost={float(row['Cost'])})"
             for row in nutrient_dict]
    if output_file:
        lines.insert(0, 'from plend import Ingredient')
    output = "\n".join(lines)
    if output_file:
        with open(output_file, 'w') as file:
            file.write(output)
    return output


def csv_to_ing_nut_py(csv_file, output_file=None, headers=None, ing_pre='', nut_pre=''):
    nutrient_dict = csv_to_dict(csv_file, headers)
    lines = [f"{ing_pre}{clean_name(row['Name'])}.add_nutrient({nut_pre}{clean_name(row['Nutrient'])}, amount={float(row['Amount'])})"
             for row in nutrient_dict]
    if output_file:
        lines.insert(0, 'from plend import Nutrient, Ingredient')
    output = "\n".join(lines)
    if output_file:
        with open(output_file, 'w') as file:
            file.write(output)
    return output


def write_text(filename, text):
    with open(filename, 'w') as file:
        file.write(text)


def generate_file(filename, *lines):
    text = ''
    for line in lines:
        text += line + '\n'
    if len(text) > 0:
        write_text(filename, text)
        
