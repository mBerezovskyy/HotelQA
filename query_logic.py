import regex

from utils import find_root, find_in_comparison, transform_in_comparison, find_comparisons, find_nested

from langchain.chains.query_constructor.ir import (
    Comparator,
    Comparison,
    Operation,
    Operator,
    StructuredQuery,
)

mapping = {
    'or': Operator.OR,
    'and': Operator.AND,
    'eq': Comparator.EQ,
    'lt': Comparator.LT,
    'gt': Comparator.GT,
    'lte': Comparator.LTE,
    'gte': Comparator.GTE
}

def gather_components(string):

    operators = []

    root_operator = find_root(string)
    string = string[:5].replace(root_operator, '') + string[5:]

    in_comparison = find_in_comparison(string)
    if in_comparison:
        
        for comp in in_comparison:
            valid_comparisons = transform_in_comparison(comp)
            valid_comparisons = ", ".join(valid_comparisons)
            
            string = string.replace(comp, f'or({valid_comparisons})')

    nested_operations = find_nested(string)

    for nested_operator in nested_operations:
        sub_root = find_root(nested_operator)
        comparisons = find_comparisons(nested_operator)
        operators.append((sub_root, comparisons))

        string = string.replace(nested_operator, '')

    remaining_comparisons = find_comparisons(string)
    

    if nested_operations == []:
        return root_operator, remaining_comparisons, []

    return root_operator, operators, remaining_comparisons


def is_list_of_tuples(obj):
    if not isinstance(obj, list):
        return False

    if all(isinstance(item, tuple) for item in obj):
        return True
    else:
        return False

def construct_filter(string):
    root_operator, operators, remaining_comparisons = gather_components(string)
    
    root_operation_arguments = []

    # print(root_operator, operators, remaining_comparisons)

    if is_list_of_tuples(operators):
        for operation_pair in operators:
            # print(f'boba: {operation_pair}')
            operator, comparisons_list = operation_pair

            arguments = []
            for comparison in comparisons_list:
                comparator = regex.findall(r'(eq|contain|lte|gte|lt|gt)', comparison)[0]
                comparison = regex.sub(comparator, '', comparison)
                comparison_tuple = eval(comparison)
                attribute, value = comparison_tuple
                arguments.append(Comparison(comparator=mapping[comparator], attribute=attribute, value=value))

            op = Operation(
                    operator=mapping[operator],
                    arguments=arguments
            )
            root_operation_arguments.append(op)
    else:
        remaining_comparisons = operators    
    
    for comparison in remaining_comparisons:
        comparator = regex.findall(r'(eq|contain|lte|gte|lt|gt)', comparison)[0]
        comparison = regex.sub(comparator, '', comparison)
        comparison_tuple = eval(comparison)
        attribute, value = comparison_tuple

        root_operation_arguments.append(Comparison(comparator=mapping[comparator], attribute=attribute, value=value))

    final_operation = Operation(
        operator=mapping[root_operator],
        arguments=root_operation_arguments
    )

    return final_operation

# q = """and(in("country", ["United Kingdom", "Germany", "Poland"]), in("starrating", [2, 3, 5]), gte("onsiterate", 200), lte("onsiterate", 500))"""
# print(construct_filter(q))

# def construct_filter(string):
#     root_operator, operators, remaining_comparisons = gather_components(string)
    
#     root_operation_arguments = []

#     if type(operators) != tuple:
#         operators = [(root_operator, operators)]

#     print(operators)

#     for operation_pair in operators:
#         # print(f'boba: {operation_pair}')
#         operator, comparisons_list = operation_pair

#         arguments = []
#         for comparison in comparisons_list:
#             comparator = regex.findall(r'(eq|contain|lte|gte|lt|gt)', comparison)[0]
#             comparison = regex.sub(comparator, '', comparison)
#             comparison_tuple = eval(comparison)
#             attribute, value = comparison_tuple
#             arguments.append(Comparison(comparator=mapping[comparator], attribute=attribute, value=value))

#         op = Operation(
#                 operator=mapping[operator],
#                 arguments=arguments
#         )
#         root_operation_arguments.append(op)
    
#     for comparison in remaining_comparisons:
#         comparator = regex.findall(r'(eq|contain|lte|gte|lt|gt)', comparison)[0]
#         comparison = regex.sub(comparator, '', comparison)
#         comparison_tuple = eval(comparison)
#         attribute, value = comparison_tuple

#         root_operation_arguments.append(Comparison(comparator=mapping[comparator], attribute=attribute, value=value))

#     final_operation = Operation(
#         operator=mapping[root_operator],
#         arguments=root_operation_arguments
#     )

#     return final_operation


# q = """and(eq("starrating", 3), gt("onsiterate", 10), eq("mealsincluded", True))"""
# # print(gather_components(q))
# print(construct_filter(q))