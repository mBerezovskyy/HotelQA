from langchain.chains.query_constructor.ir import (
    Comparator,
    Comparison,
    Operation,
    Operator,
    StructuredQuery,
)

from langchain.retrievers.self_query.chroma import ChromaTranslator
from langchain.retrievers.self_query.elasticsearch import ElasticsearchTranslator

DEFAULT_TRANSLATOR = ChromaTranslator()
# DEFAULT_TRANSLATOR = ElasticsearchTranslator()

comp = Comparison(comparator=Comparator.LT, attribute="foo", value=["1", "2"])


actual = DEFAULT_TRANSLATOR.visit_comparison(comp)

# print(actual)


"""
"and(or(eq(\"country\", \"United Kingdom\"), eq(\"country\", \"Germany\")), eq(\"maxoccupancy\", 2), eq(\"mealsincluded\", false))"

"""

import regex

# sample_string = "and(or(eq(\"country\", \"Austria\"), eq(\"country\", \"Germany\")), and(eq(\"starrating\", 5), eq(\"mealsincluded\", True)), leq(\"aboba\", 20) limit = 5)"
sample_string = "and(or(eq(\"country\", \"United Kingdom\"), eq(\"country\", \"Germany\")), eq(\"maxoccupancy\", 2), eq(\"mealsincluded\", False), limit=None)"



def find_nested(string):
    pattern = r'(?:or|and)\((?:[^()]|\((?:[^()]|(?R))*\))*\)'
    matches = regex.findall(pattern, string)
    return matches

def find_root(string):
    pattern = r'(and|or)\(.*\)'
    matches = regex.findall(pattern, string)
    return matches[0]

def find_comparisons(string):
    pattern = r"(eq\([^)]+\)|lte\([^)]+\)|gte\([^)]+\)|lt\([^)]+\)|gt\([^)]+\))"
    matches = regex.findall(pattern, string)
    return matches


def gather_components(string):

    operators = []

    root_operator = find_root(string)
    nested_operations = find_nested(string)

    for nested_operator in nested_operations:
        sub_root = find_root(nested_operator)
        comparisons = find_comparisons(nested_operator)
        operators.append((sub_root, comparisons))

        string = string.replace(nested_operator, '')

    remaining_comparisons = find_comparisons(string)

    limit = regex.findall('limit.?=.?.*\)', string)[0].split('=')[1].strip()[:-1]

    return root_operator, operators, remaining_comparisons, limit


# ('and', [('or', ['eq("country", "Austria")', 'eq("country", "Germany")']), ('and', ['eq("starrating", 5)', 'eq("mealsincluded", true)'])], ['eq("aboba", 20)'], '5')


mapping = {
    'or': Operator.OR,
    'and': Operator.AND,
    'eq': Comparator.EQ
}

def construct_filter(string):
    root_operator, operators, remaining_comparisons, limit = gather_components(sample_string)
    
    root_operation_arguments = []

    for operation_pair in operators:
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
    
    for comparison in remaining_comparisons:
        comparator = regex.findall(r'(eq|contain|lte|gte|lt|gt)', comparison)[0]
        comparison = regex.sub(comparator, '', comparison)
        comparison_tuple = eval(comparison)
        attribute, value = comparison_tuple

        root_operation_arguments.append(Comparison(comparator=mapping[comparator], attribute=attribute, value=value))


        # print(attribute, value)


    # for oper in root_operation_arguments:
    #     print(oper, '\n')


    final_operation = Operation(
        operator=mapping[root_operator],
        arguments=root_operation_arguments
    )

    return final_operation

filter_for_structured_query = construct_filter(sample_string)

query = "Room"
structured_query = StructuredQuery(
        query=query,
        filter=filter_for_structured_query,
    )

query, search_kwargs = ChromaTranslator().visit_structured_query(structured_query)

print(query, search_kwargs)

# op1 = Operation(
#         operator=Operator.OR,
#         arguments=[
#             Comparison(comparator=Comparator.EQ, attribute="country", value="United Kingdom"),
#             Comparison(comparator=Comparator.EQ, attribute="country", value="Germany"),
#         ],
#     )

# op2 = Operation(
#         operator=Operator.AND,
#         arguments=[
#             op1,
#             Comparison(comparator=Comparator.EQ, attribute="maxoccupancy", value=2),
#             Comparison(comparator=Comparator.EQ, attribute="mealsincluded", value=False),
#         ],
#     )

# actual = DEFAULT_TRANSLATOR.visit_operation(op2)



op2 = Operation(
        operator=Operator.AND,
        arguments=[
            Comparison(comparator=Comparator.EQ, attribute="country", value=['a', 'b', 'c', 'd', 'e']),
        ],
    )

actual = DEFAULT_TRANSLATOR.visit_operation(op2)

print(actual)

# query = "Room"
# structured_query = StructuredQuery(
#         query=query,
#         filter=filter_for_structured_query,
#     )
















# for operation in nested_operations:
    # sub_root = find_root(operation)


# print(root_operator)
# print(nested_operations)


# nested = find_nested(sample_string)
# print(find_components(nested[0]))


# print(re.findall(r'(?:or|and)\((?:[^()]|\((?:[^()]|(?R))*\))*\)', input_string))




# root = re.findall('(eq|contain|gte|lte|gt|lt|or)\(.*\)', string)
# print(root)
# op1 = Operation(
#         operator=Operator.OR,
#         arguments=[
#             Comparison(comparator=Comparator.EQ, attribute="country", value="United Kingdom"),
#             Comparison(comparator=Comparator.EQ, attribute="country", value="Germany"),
#         ],
#     )

# op2 = Operation(
#         operator=Operator.AND,
#         arguments=[
#             op1,
#             Comparison(comparator=Comparator.EQ, attribute="maxoccupancy", value=2),
#         ],
#     )

# actual = DEFAULT_TRANSLATOR.visit_operation(op2)

# print(actual)

# query = "Room"
# structured_query = StructuredQuery(
#         query=query,
#         filter=op2,
#     )
# actual = DEFAULT_TRANSLATOR.visit_structured_query(structured_query)

# print(actual)
