import regex

def find_nested(string):
    pattern = r'(?:or|and)\((?:[^()]|\((?:[^()]|(?R))*\))*\)'
    matches = regex.findall(pattern, string)
    return matches

def find_root(string):
    pattern = r'(and|or)\(.*\)'
    matches = regex.findall(pattern, string)
    return matches[0]

def find_in_comparison(string):
    in_pattern = r'(in\([^)]+\))'
    matches = regex.findall(in_pattern, string)
    return matches

def transform_in_comparison(comparison):
    valid_comparisons = []

    comparison = regex.sub('in\(', '(', comparison)
    comparison_tuple = eval(comparison)
    attribute, values = comparison_tuple

    for value in values:
        # print(type(value))
        if type(value) == str:
            valid_comparisons.append(f'eq(\"{attribute}\", \"{value}\")')
        else:
            valid_comparisons.append(f"eq(\"{attribute}\", {value})")

    return valid_comparisons

def find_comparisons(string):
    pattern = r"(eq\([^)]+\)|lte\([^)]+\)|gte\([^)]+\)|lt\([^)]+\)|gt\([^)]+\)|in\([^)]+\))"
    matches = regex.findall(pattern, string)
    return matches