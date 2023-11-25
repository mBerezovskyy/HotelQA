# import pandas as pd
# from langchain.chat_models import ChatOpenAI

# import os
# import openai

# os.environ['OPENAI_API_KEY'] = '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'
# openai.api_key = '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'

# details = (
#     pd.read_csv("Hotel_details.csv")
#     .drop_duplicates(subset="hotelid")
#     .set_index("hotelid")
# )
# attributes = pd.read_csv(
#     "Hotel_Room_attributes.csv", index_col="id"
# )
# price = pd.read_csv("hotels_RoomPrice.csv", index_col="id")

# latest_price = price.drop_duplicates(subset="refid", keep="last")[
#     [
#         "hotelcode",
#         "roomtype",
#         "onsiterate",
#         "roomamenities",
#         "maxoccupancy",
#         "mealinclusiontype",
#     ]
# ]
# latest_price["ratedescription"] = attributes.loc[latest_price.index]["ratedescription"]
# latest_price = latest_price.join(
#     details[["hotelname", "city", "country", "starrating"]], on="hotelcode"
# )
# latest_price = latest_price.rename({"ratedescription": "roomdescription"}, axis=1)
# latest_price["mealsincluded"] = ~latest_price["mealinclusiontype"].isnull()
# latest_price.pop("hotelcode")
# latest_price.pop("mealinclusiontype")
# latest_price = latest_price.reset_index(drop=True)
# latest_price.head()

# latest_price.nunique()[latest_price.nunique() < 40]

# from langchain.chains.query_constructor.base import (
#     get_query_constructor_prompt,
#     load_query_constructor_runnable,
# )

# attribute_info = [
#  {'name': 'roomtype', 'description': 'The type of the room', 'type': 'string'},
#  {'name': 'onsiterate', 'description': 'The rate of the room', 'type': 'float'},
#  {'name': 'roomamenities', 'description': 'Amenities available in the room', 'type': 'string'},
#  {'name': 'maxoccupancy', 'description': 'Maximum number of people that can occupy the room. Valid values are [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 24]', 'type': 'integer'},
#  {'name': 'roomdescription', 'description': 'Description of the room', 'type': 'string'},
#  {'name': 'hotelname', 'description': 'Name of the hotel', 'type': 'string'},
#  {'name': 'city', 'description': 'City where the hotel is located', 'type': 'string'},
#  {'name': 'country', 'description': "Country where the hotel is located. Valid values are ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']", 'type': 'string'},
#  {'name': 'starrating', 'description': 'Star rating of the hotel. Valid values are [2, 3, 4]', 'type': 'integer'},
#  {'name': 'mealsincluded', 'description': 'Whether meals are included or not', 'type': 'boolean'}
# ]

# attribute_info[-3][
#     "description"
# ] += ". NOTE: Only use the 'eq' operator if a specific country is mentioned. If a region is mentioned, include all relevant countries from this list ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom'] in filter."


# doc_contents = "Detailed description of a hotel room"
# prompt = get_query_constructor_prompt(doc_contents, attribute_info)

# # print(prompt.format(query="{query}"))

# chain = load_query_constructor_runnable(
#     ChatOpenAI(model="gpt-3.5-turbo", 
#     temperature=0),
#     doc_contents,
#     attribute_info
# )

# print(chain)

# # print(chain.invoke({"query": "I want a hotel which is located in Austria or Sweden. My budget is 400 bucks."}))



# from langchain.retrievers.self_query.chroma import ChromaTranslator
# from langchain.retrievers.self_query.elasticsearch import ElasticsearchTranslator


# from langchain.chains.query_constructor.ir import (
#     Comparator,
#     Comparison,
#     Operation,
#     Operator,
#     StructuredQuery,
#     Visitor,
# )


# prompt2 = """
# Your goal is to structure the user's query to match the request schema provided below.

# << Structured Request Schema >>
# When responding use a markdown code snippet with a JSON object formatted in the following schema:

# ```json
# {
#     "query": string \ text string to compare to document contents
#     "filter": string \ logical condition statement for filtering documents
# }
# ```

# The query string should contain only text that is expected to match the contents of documents. Any conditions in the filter should not be mentioned in the query as well.

# A logical condition statement is composed of one or more comparison and logical operation statements.

# A comparison statement takes the form: `comp(attr, val)`:
# - `comp` (eq | ne | gt | gte | lt | lte | contain | like | in | nin): comparator
# - `attr` (string):  name of attribute to apply the comparison to
# - `val` (string): is the comparison value

# A logical operation statement takes the form `op(statement1, statement2, ...)`:
# - `op` (and | or | not): logical operator
# - `statement1`, `statement2`, ... (comparison statements or logical operation statements): one or more statements to apply the operation to

# Make sure that you only use the comparators and logical operators listed above and no others.
# Make sure that filters only refer to attributes that exist in the data source.
# Make sure that filters only use the attributed names with its function names if there are functions applied on them.
# Make sure that filters only use format `YYYY-MM-DD` when handling timestamp data typed values.
# Make sure that filters take into account the descriptions of attributes and only make comparisons that are feasible given the type of data being stored.
# Make sure that filters are only used as needed. If there are no filters that should be applied return "NO_FILTER" for the filter value.

# << Data Source >>
# ```json
# {
#     "content": "A detailed description of a hotel room, including information about the room type and room amenities.",
#     "attributes": {
#     "onsiterate": {
#         "description": "The rate of the room",
#         "type": "float"
#     },
#     "maxoccupancy": {
#         "description": "Maximum number of people that can occupy the room. Valid values are [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 24]",
#         "type": "integer"
#     },
#     "city": {
#         "description": "City where the hotel is located",
#         "type": "string"
#     },
#     "country": {
#         "description": "Country where the hotel is located. Valid values are ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']. NOTE: Only use the 'eq' operator if a specific country is mentioned. If a region is mentioned, include all relevant countries in filter.",
#         "type": "string"
#     },
#     "starrating": {
#         "description": "Star rating of the hotel. Valid values are [2, 3, 4]",
#         "type": "integer"
#     },
#     "mealsincluded": {
#         "description": "Whether meals are included or not",
#         "type": "boolean"
#     }
# }
# }
# ```


# << Example 1. >>
# User Query:
# I want a hotel in the Balkans with a king sized bed and a hot tub. Budget is $300 a night

# Structured Request:
# ```json
# {
#     "query": "king-sized bed, hot tub",
#     "filter": "and(in(\"country\", [\"Bulgaria\", \"Greece\", \"Croatia\", \"Serbia\"]), lte(\"onsiterate\", 300))"
# }
# ```


# << Example 2. >>
# User Query:
# A room with breakfast included for 3 people, at a Hilton

# Structured Request:
# ```json
# {
#     "query": "Hilton",
#     "filter": "and(eq(\"mealsincluded\", true), gte(\"maxoccupancy\", 3))"
# }
# ```


# << Example 3. >>
# User Query:
# I want a hotel in Italy with 4 stars

# Structured Request:
# ```json
# {
#     "query": "Hilton",
#     "filter": "and(eq(\"country\", \"Italy\"), eq(\"starrating\", 4))"
# }
# ```


# << Example 4. >>
# User Query:
# I want a hotel in the Central Europe. My budget is 400 bucks

# Structured Request:

# """


# # I want a hotel in Austria or Sweden for 400 bucks.
# # {'filter': {'$and': [{'$or': [{'country': {'$eq': 'Austria'}}, {'country': {'$eq': 'Sweden'}}]}, {'onsiterate': {'$eq': 400}}]}}



# # {
# #    "filter":{
# #       "$and":[
# #          {
# #             "$or":[
# #                {
# #                   "country":{
# #                      "$eq":"Austria"
# #                   }
# #                },
# #                {
# #                   "country":{
# #                      "$eq":"Sweden"
# #                   }
# #                }
# #             ]
# #          },
# #          {
# #             "onsiterate":{
# #                "$eq":400
# #             }
# #          }
# #       ]
# #    }
# # }



# prompt = """
# The list of all allowed comparators is : [eq, ne, gt, gte, lt, lte, contain]

# The list of all fields is:

# {
#     "content": {
#         description: "A detailed description of a hotel room, including information about the room type and room amenities.",
#         "type": "string"
#     },
#     "onsiterate": {
#         "description": "The rate of the room",
#         "type": "float"
#     },
#     "maxoccupancy": {
#         "description": "Maximum number of people that can occupy the room. Valid values are [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 24]",
#         "type": "integer"
#     },
#     "hotelname": {
#         "description": "The name of the hotel or room",
#         "type": "string"
#     },
#     "city": {
#         "description": "City where the hotel is located",
#         "type": "string"
#     },
#     "country": {
#         "description": "Country where the hotel is located. Valid values are ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']. NOTE: Only use the 'eq' operator if a specific country is mentioned. If a region is mentioned, include all relevant countries in filter.",
#         "type": "string"
#     },
#     "starrating": {
#         "description": "Star rating of the hotel. Valid values are [2, 3, 4]",
#         "type": "integer"
#     },
#     "mealsincluded": {
#         "description": "Whether meals are included or not",
#         "type": "boolean"
#     }
# }

# NOTE: "content" must not be used in filters

# Examples of usage:

# Query: I want a room with king-sized bed and AC in Bulgaria
# output: 
# ```json
# {{
#     "query": "king-sized bed; AC",
#     "filters": "and(eq(\"country\", \"Bulgaria\"), limit=None)"
# }}
# ```

# Query: I want any hotel in Balkans with 4 stars and a price of 350$ per night
# output: 
# ```json
# {{
#     "query": "hotel",
#     "filters": "and(in(\"country\", [\"Bulgaria\", \"Greece\", \"Croatia\", \"Serbia\"]), eq(\"starrating\", 4) lte(\"onsiterate\", 350), limit=None)"
# }}
# ```

# Query: Find me 5 rooms with included breakfast and top rating in Italy
# output: 
# ```json
# {{
#     "query": "room",
#     "filters": "and(eq(\"country\", \"Italy\"), eq(\"mealsincluded\", True), eq(\"starrating\", 5), limit=5)"
# }}
# ```

# Query: I want a 2 star hotel with \"Top\" in its name. It should have AC and my budget is 100$
# output: 
# ```json
# {{
#     "query": "hotel; AC",
#     "filters": "and(contain(\"hotelname\", \"Top\"), eq(\"starrating\", 2), eq(\"onsiterate\", 100), limit=None)"
# }}
# ```

# Query: I want a hotel in Austria or Germany with hot tub, AC, 5 stars and included breakfast. The room must be for 6 people and hotel name must start with Best. Price mut be in a range of 600 to 1200$
# """



# message_log = [
#         {
#             "role":"user",
#             "content": prompt2,
#         },
#     ]

# # response = openai.ChatCompletion.create(
# #         model="gpt-4-1106-preview",
# #         messages=message_log,
# #         max_tokens=256,
# #         temperature=0,
# #         presence_penalty=0,
# #         frequency_penalty=0
# #     )
# # data = response.choices[0].message.content

# # print(data)



# # query, search_kwargs = ChromaTranslator().visit_structured_query(StructuredQuery(query='hotel', filter=Operation(operator=Operator.AND, arguments=[Comparison(comparator=Comparator.EQ, attribute='country', value='Italy'), Comparison(comparator=Comparator.LTE, attribute='onsiterate', value=200)]), limit=None))
# # query, search_kwargs = ElasticsearchTranslator().visit_structured_query(StructuredQuery(query='hotel', filter=Operation(operator=Operator.AND, arguments=[Operation(operator=Operator.OR, arguments=[Comparison(comparator=Comparator.EQ, attribute='country', value='Austria'), Comparison(comparator=Comparator.EQ, attribute='country', value='Sweden')]), Comparison(comparator=Comparator.EQ, attribute='onsiterate', value=400)]), limit=None))
# # query, search_kwargs = ElasticsearchTranslator().visit_structured_query(StructuredQuery(query='hotel', filter=Operation(operator=Operator.AND, arguments=[Operation(operator=Operator.OR, arguments=[Comparison(comparator=Comparator.CONTAIN, attribute='hotelname', value='Top'), Comparison(comparator=Comparator.EQ, attribute='country', value='Sweden')]), Comparison(comparator=Comparator.EQ, attribute='onsiterate', value=400)]), limit=None))
    
# # output = """
# # ```json
# # {{
# #     \"query\": \"hotel, hot tub, AC\",
# #     \"filter\": \"and(or(eq(\"country\", \"Austria\"), eq(\"country\", \"Germany\")), eq(\"starrating\", 5), eq(\"mealsincluded\", true))\"
# # }}
# # ```
# # """

# output = """
# ```json
# {{
#     "query": "Hilton",
#     "filter": "and(eq(\"mealsincluded\", true), gte(\"maxoccupancy\", 3))"
# }}
# ```
# """




# q = 


# # from langchain.output_parsers.json import parse_and_check_json_markdown


# # print(parse_and_check_json_markdown(output, expected_keys=["query", "filter"]))
# # from langchain.chains.query_constructor.base import StructuredQueryOutputParser

# # parser = StructuredQueryOutputParser()

# # print(parser.parse(text=output))

# # StructuredQuery(query='hotel', filter=Operation(operator=Operator.AND, arguments=[Operation(operator=Operator.OR, arguments=[Comparison(comparator=Comparator.CONTAIN, attribute='hotelname', value='Top'), Comparison(comparator=Comparator.EQ, attribute='country', value='Sweden')]), Comparison(comparator=Comparator.EQ, attribute='onsiterate', value=400)]), limit=None))
    

# # StructuredQuery(query='hotel', filter=Operation(
# #     operator=Operator.AND, arguments=[
# #         Operation(
# #             operator=Operator.OR,
# #             arguments=[
# #                 Comparison(comparator=Comparator.CONTAIN, attribute='hotelname', value='Top'),
# #                 Comparison(comparator=Comparator.EQ, attribute='country', value='Sweden')
# #             ]
# #         ),
# #         Comparison(comparator=Comparator.EQ, attribute='onsiterate', value=400)
# #     ]), limit=None))


# # StructuredQuery(query='hotel', filter=Operation(operator=Operator.AND, arguments=[Operation(operator=Operator.OR, arguments=[Comparison(comparator=Comparator.EQ, attribute='country', value='Austria'), Comparison(comparator=Comparator.EQ, attribute='country', value='Sweden')])],limit=None)))



# # print(search_kwargs)
    

#     # "filter": "and(in("country", ['Austria', 'Czech Republic', 'Germany', 'Hungary', 'Poland', 'Slovakia', 'Slovenia']), lte("onsiterate", 400))"


# # print(query, search_kwargs)

# # import json
# # from langchain.schema import Document
# # from langchain.vectorstores import Chroma
# # from langchain.embeddings import OpenAIEmbeddings
# # embeddings = OpenAIEmbeddings()


# # # print(latest_price.iloc[:50])

# # docs = []
# # for _, room in latest_price.iloc[:50].fillna("").iterrows():
# #     doc = Document(
# #         page_content=json.dumps(room.to_dict(), indent=2),
# #         metadata=room.to_dict()
# #     )
# #     docs.append(doc)
# # db = Chroma.from_documents(docs, embeddings)

# # docs = db.search(query, 'similarity', **search_kwargs)










# # # print(prompt)


# # p = """

# # I am having this issue with langchain:

# # During handling of the above exception, another exception occurred:

# # Traceback (most recent call last):
# #   File "/home/maxym/Projects/retreival/main.py", line 77, in <module>
# #     print(chain.invoke({"query": "I want a hotel in Central Europe for 400 bucks."}))
# #   File "/home/maxym/anaconda3/envs/retreival/lib/python3.9/site-packages/langchain/schema/runnable/base.py", line 1213, in invoke
# #     input = step.invoke(
# #   File "/home/maxym/anaconda3/envs/retreival/lib/python3.9/site-packages/langchain/schema/output_parser.py", line 174, in invoke
# #     return self._call_with_config(
# #   File "/home/maxym/anaconda3/envs/retreival/lib/python3.9/site-packages/langchain/schema/runnable/base.py", line 715, in _call_with_config
# #     output = call_func_with_variable_args(
# #   File "/home/maxym/anaconda3/envs/retreival/lib/python3.9/site-packages/langchain/schema/runnable/config.py", line 308, in call_func_with_variable_args
# #     return func(input, **kwargs)  # type: ignore[call-arg]
# #   File "/home/maxym/anaconda3/envs/retreival/lib/python3.9/site-packages/langchain/schema/output_parser.py", line 175, in <lambda>
# #     lambda inner_input: self.parse_result(
# #   File "/home/maxym/anaconda3/envs/retreival/lib/python3.9/site-packages/langchain/schema/output_parser.py", line 226, in parse_result
# #     return self.parse(result[0].text)
# #   File "/home/maxym/anaconda3/envs/retreival/lib/python3.9/site-packages/langchain/chains/query_constructor/base.py", line 60, in parse
# #     raise OutputParserException(
# # langchain.schema.output_parser.OutputParserException: Parsing text
# # ```json
# # {
# #     "query": "hotel",
# #     "filter": "and(eq(\"country\", \"Austria\"), eq(\"country\", \"Belgium\"), eq(\"country\", \"Bulgaria\"), eq(\"country\", \"Croatia\"), eq(\"country\", \"Czech Republic\"), eq(\"country\", \"Denmark\"), eq(\"country\", \"Estonia\"), eq(\"country\", \"Finland\"), eq(\"country\", \"Germany\"), eq(\"country\", \"Hungary\"), eq(\"country\", \"Poland\"), eq(\"country\", \"Romania\"), eq(\"country\", \"Slovakia\"), eq(\"country\", \"Slovenia\"), eq(\"country\", \"Switzerland\"), eq(\"country\", \"United Kingdom\")), lte(\"onsiterate\", 400)"
# # }
# # ```
# #  raised following error:
# # Unexpected token Token('COMMA', ',') at line 1, column 440.
# # Expected one of: 
# # 	* $END


# # What should I do
# # """

# # message_log = [
# #         {
# #             "role":"user",
# #             "content": p,
# #         },
# #     ]

# # response = openai.ChatCompletion.create(
# #         model="gpt-4-1106-preview",
# #         messages=message_log,
# #         max_tokens=1600,
# #         temperature=0,
# #         presence_penalty=0,
# #         frequency_penalty=0
# #     )
# # data = response.choices[0].message.content

# # print(data)



import pandas as pd
from langchain.chat_models import ChatOpenAI

import os
import openai

import regex

os.environ['OPENAI_API_KEY'] = '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'
openai.api_key = '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'

details = (
    pd.read_csv("Hotel_details.csv")
    .drop_duplicates(subset="hotelid")
    .set_index("hotelid")
)
attributes = pd.read_csv(
    "Hotel_Room_attributes.csv", index_col="id"
)
price = pd.read_csv("hotels_RoomPrice.csv", index_col="id")

latest_price = price.drop_duplicates(subset="refid", keep="last")[
    [
        "hotelcode",
        "roomtype",
        "onsiterate",
        "roomamenities",
        "maxoccupancy",
        "mealinclusiontype",
    ]
]
latest_price["ratedescription"] = attributes.loc[latest_price.index]["ratedescription"]
latest_price = latest_price.join(
    details[["hotelname", "city", "country", "starrating"]], on="hotelcode"
)
latest_price = latest_price.rename({"ratedescription": "roomdescription"}, axis=1)
latest_price["mealsincluded"] = ~latest_price["mealinclusiontype"].isnull()
latest_price.pop("hotelcode")
latest_price.pop("mealinclusiontype")
latest_price = latest_price.reset_index(drop=True)
latest_price.head()

latest_price.nunique()[latest_price.nunique() < 40]

from langchain.chains.query_constructor.base import (
    get_query_constructor_prompt,
    load_query_constructor_runnable,
)

attribute_info = [
 {'name': 'roomtype', 'description': 'The type of the room', 'type': 'string'},
 {'name': 'onsiterate', 'description': 'The rate of the room', 'type': 'float'},
 {'name': 'roomamenities', 'description': 'Amenities available in the room', 'type': 'string'},
 {'name': 'maxoccupancy', 'description': 'Maximum number of people that can occupy the room. Valid values are [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 24]', 'type': 'integer'},
 {'name': 'roomdescription', 'description': 'Description of the room', 'type': 'string'},
 {'name': 'hotelname', 'description': 'Name of the hotel', 'type': 'string'},
 {'name': 'city', 'description': 'City where the hotel is located', 'type': 'string'},
 {'name': 'country', 'description': "Country where the hotel is located. Valid values are ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']", 'type': 'string'},
 {'name': 'starrating', 'description': 'Star rating of the hotel. Valid values are [2, 3, 4]', 'type': 'integer'},
 {'name': 'mealsincluded', 'description': 'Whether meals are included or not', 'type': 'boolean'}
]

attribute_info[-3][
    "description"
] += ". NOTE: Only use the 'eq' operator if a specific country is mentioned. If a region is mentioned, include all relevant countries from this list ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom'] in filter."


doc_contents = "Detailed description of a hotel room"
prompt = get_query_constructor_prompt(doc_contents, attribute_info)

# print(prompt.format(query="{query}"))

chain = load_query_constructor_runnable(
    ChatOpenAI(model="gpt-3.5-turbo", 
    temperature=0),
    doc_contents,
    attribute_info,
    enable_limit=True,
)

# print(chain)

# print(chain.invoke({"query": "I want 2 hotels located in Austria or Sweden. My budget is 400 bucks."}))



from langchain.retrievers.self_query.chroma import ChromaTranslator
from langchain.retrievers.self_query.elasticsearch import ElasticsearchTranslator


from langchain.chains.query_constructor.ir import (
    Comparator,
    Comparison,
    Operation,
    Operator,
    StructuredQuery,
    Visitor,
)


prompt2 = """
Your goal is to structure the user's query to match the request schema provided below.

<< Structured Request Schema >>
When responding use a markdown code snippet with a JSON object formatted in the following schema:

```json
{
    "query": string \ text string to compare to document contents
    "filter": string \ logical condition statement for filtering documents
}
```

The query string should contain only text that is expected to match the contents of documents. Any conditions in the filter should not be mentioned in the query as well.

A logical condition statement is composed of one or more comparison and logical operation statements.

A comparison statement takes the form: `comp(attr, val)`:
- `comp` (eq | ne | gt | gte | lt | lte | contain | like | in | nin): comparator
- `attr` (string):  name of attribute to apply the comparison to
- `val` (string): is the comparison value

A logical operation statement takes the form `op(statement1, statement2, ...)`:
- `op` (and | or | not): logical operator
- `statement1`, `statement2`, ... (comparison statements or logical operation statements): one or more statements to apply the operation to

Make sure that you only use the comparators and logical operators listed above and no others.
Make sure that filters only refer to attributes that exist in the data source.
Make sure that filters only use the attributed names with its function names if there are functions applied on them.
Make sure that filters only use format `YYYY-MM-DD` when handling timestamp data typed values.
Make sure that filters take into account the descriptions of attributes and only make comparisons that are feasible given the type of data being stored.
Make sure that filters are only used as needed. If there are no filters that should be applied return "NO_FILTER" for the filter value.

<< Data Source >>
```json
{
    "content": "A detailed description of a hotel room, including information about the room type and room amenities.",
    "attributes": {
    "onsiterate": {
        "description": "The rate of the room",
        "type": "float"
    },
    "maxoccupancy": {
        "description": "Maximum number of people that can occupy the room. Valid values are [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 24]",
        "type": "integer"
    },
    "city": {
        "description": "City where the hotel is located",
        "type": "string"
    },
    "country": {
        "description": "Country where the hotel is located. Valid values are ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']. NOTE: Only use the 'eq' operator if a specific country is mentioned. If a region is mentioned, include all relevant countries in filter.",
        "type": "string"
    },
    "starrating": {
        "description": "Star rating of the hotel. Valid values are [2, 3, 4]",
        "type": "integer"
    },
    "mealsincluded": {
        "description": "Whether meals are included or not",
        "type": "boolean"
    }
}
}
```


<< Example 1. >>
User Query:
I want a hotel in the Balkans with a king sized bed and a hot tub. Budget is $300 a night

Structured Request:
```json
{
    "query": "king-sized bed, hot tub",
    "filter": "and(in(\"country\", [\"Bulgaria\", \"Greece\", \"Croatia\", \"Serbia\"]), lte(\"onsiterate\", 300))"
}
```


<< Example 2. >>
User Query:
A room with breakfast included for 3 people, at a Hilton

Structured Request:
```json
{
    "query": "Hilton",
    "filter": "and(eq(\"mealsincluded\", true), gte(\"maxoccupancy\", 3))"
}
```


<< Example 3. >>
User Query:
I want a hotel in Italy with 4 stars

Structured Request:
```json
{
    "query": "Hilton",
    "filter": "and(eq(\"country\", \"Italy\"), eq(\"starrating\", 4))"
}
```


<< Example 4. >>
User Query:
I want a hotel in the Central Europe. My budget is 400 bucks

Structured Request:

"""


# I want a hotel in Austria or Sweden for 400 bucks.
# {'filter': {'$and': [{'$or': [{'country': {'$eq': 'Austria'}}, {'country': {'$eq': 'Sweden'}}]}, {'onsiterate': {'$eq': 400}}]}}



# {
#    "filter":{
#       "$and":[
#          {
#             "$or":[
#                {
#                   "country":{
#                      "$eq":"Austria"
#                   }
#                },
#                {
#                   "country":{
#                      "$eq":"Sweden"
#                   }
#                }
#             ]
#          },
#          {
#             "onsiterate":{
#                "$eq":400
#             }
#          }
#       ]
#    }
# }



prompt = """
The list of all allowed comparators is : [eq, ne, gt, gte, lt, lte, contain]

The list of all fields is:

{{
    "content": {{
        description: "A detailed description of a hotel room, including information about the room type and room amenities.",
        "type": "string"
    }},
    "onsiterate": {{
        "description": "The rate of the room",
        "type": "float"
    }},
    "maxoccupancy": {{
        "description": "Maximum number of people that can occupy the room. Valid values are [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 24]",
        "type": "integer"
    }},
    "hotelname": {{
        "description": "The name of the hotel or room",
        "type": "string"
    }},
    "city": {{
        "description": "City where the hotel is located",
        "type": "string"
    }},
    "country": {{
        "description": "Country where the hotel is located. Valid values are ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']. NOTE: Only use the 'eq' operator if a specific country is mentioned. If a region is mentioned, include all relevant countries in filter.",
        "type": "string"
    }},
    "starrating": {{
        "description": "Star rating of the hotel. Valid values are [2, 3, 4]",
        "type": "integer"
    }},
    "mealsincluded": {{
        "description": "Whether meals are included or not",
        "type": "boolean"
    }}
}}

NOTE: "content" must not be used in filters

Examples of usage:

Query: I want a room with king-sized bed and AC in Bulgaria
output: 
{{
    "query": "king-sized bed; AC",
    "filters": "and(eq(\\"country\\", \\"Bulgaria\\"))",
    "limit": "None"
}}

Query: I want any hotel in Balkans with 4 stars and a price of 350$ per night
output: 
{{
    "query": "hotel",
    "filters": "and(in(\\"country\\", [\\"Bulgaria\\", \\"Greece\\", \\"Croatia\\", \\"Serbia\\"]), eq(\\"starrating\\", 4) lte(\\"onsiterate\\", 350))",
    "limit": "None"
}}

Query: Find me 5 rooms with included breakfast and top rating in Italy
output: 
{{
    "query": "room",
    "filters": "and(eq(\\"country\\", \\"Italy\\"), eq(\\"mealsincluded\\", True), eq(\\"starrating\\", 5))",
    "limit": 5
}}

Query: I want a 2 star hotel with \\"Top\\" in its name. It should have AC and my budget is 100$
output: 
{{
    "query": "hotel; AC",
    "filters": "and(contain(\\"hotelname\\", \\"Top\\"), eq(\\"starrating\\", 2), eq(\\"onsiterate\\", 100))",
    "limit": "None"
}}


Query: {query}
output:
"""


q = 'I want a 5 or 2 or 3 star hotel, somwhere in Austria, Germany or Poland. Price must be between 500 and 1000'


# print(prompt.format(query=q))

message_log = [
        {
            "role":"user",
            "content": prompt.format(query=q),
        },
    ]

# response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=message_log,
#         max_tokens=256,
#         temperature=0,
#         presence_penalty=0,
#         frequency_penalty=0
#     )
# data = response.choices[0].message.content

# print(data)


import json


# data = """
# {
#     "query": "hotel",
#     "filters": "and(in(\\"country\\", [\\"Austria\\", \\"Belgium\\", \\"Czech Republic\\", \\"Denmark\\", \\"Finland\\", \\"France\\", \\"Germany\\", \\"Hungary\\", \\"Ireland\\", \\"Italy\\", \\"Luxembourg\\", \\"Netherlands\\", \\"Poland\\", \\"Portugal\\", \\"Slovakia\\", \\"Spain\\", \\"Sweden\\", \\"Switzerland\\", \\"United Kingdom\\"]), lte(\\"onsiterate\\", 200))",
#     "limit": "None"
# }
# """

# output = json.loads(data)

# print(output['query'])
# print(output['filters'])



# query, search_kwargs = ChromaTranslator().visit_structured_query(StructuredQuery(query='hotel', filter=Operation(operator=Operator.AND, arguments=[Comparison(comparator=Comparator.EQ, attribute='country', value='Italy'), Comparison(comparator=Comparator.LTE, attribute='onsiterate', value=200)]), limit=None))
# query, search_kwargs = ElasticsearchTranslator().visit_structured_query(StructuredQuery(query='hotel', filter=Operation(operator=Operator.AND, arguments=[Operation(operator=Operator.OR, arguments=[Comparison(comparator=Comparator.EQ, attribute='country', value='Austria'), Comparison(comparator=Comparator.EQ, attribute='country', value='Sweden')]), Comparison(comparator=Comparator.EQ, attribute='onsiterate', value=400)]), limit=None))
# query, search_kwargs = ElasticsearchTranslator().visit_structured_query(StructuredQuery(query='hotel', filter=Operation(operator=Operator.AND, arguments=[Operation(operator=Operator.OR, arguments=[Comparison(comparator=Comparator.CONTAIN, attribute='hotelname', value='Top'), Comparison(comparator=Comparator.EQ, attribute='country', value='Sweden')]), Comparison(comparator=Comparator.EQ, attribute='onsiterate', value=400)]), limit=None))
    
# output = """
# ```json
# {{
#     \"query\": \"hotel, hot tub, AC\",
#     \"filter\": \"and(or(eq(\"country\", \"Austria\"), eq(\"country\", \"Germany\")), eq(\"starrating\", 5), eq(\"mealsincluded\", true))\"
# }}
# ```
# """





from langchain.chains.query_constructor.ir import (
    Comparator,
    Comparison,
    Operation,
    Operator,
    StructuredQuery,
)

from langchain.retrievers.self_query.chroma import ChromaTranslator

DEFAULT_TRANSLATOR = ChromaTranslator()



# q = chain.invoke({"query": "I want 2 hotels located in Austria or Sweden. My budget is 400 bucks."})

# print(DEFAULT_TRANSLATOR.visit_structured_query(q))


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



st = """and(in(\"country\", [\"Austria\", \"Germany\", \"Poland\"]), in(\"starrating\", [2, 3, 5]), gte(\"onsiterate\", 500), lte(\"onsiterate\", 1000))"""
# print(transform_in_comparison(find_in_comparison(st)))
# print(output['filters'])



def gather_components(string):

    operators = []

    root_operator = find_root(string)
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

    # for comparison in remaining_comparisons:
    #     candidate_in = find_in_comparison(comparison)
    #     # print(candidate_in)
    #     if candidate_in:
    #         print('in')
    #     else:
    #         print('no in')
    #     #     valid_comparisons = transform_in_comparison(candidate_in)
    #     #     remaining_comparisons.remove(candidate_in)
    #     #     remaining_comparisons.extend(valid_comparisons)

    # # limit = regex.findall('limit.?=.?.*\)', string)[0].split('=')[1].strip()[:-1]

    return root_operator, operators, remaining_comparisons, 0


print(gather_components(st))



def construct_filter(string):
    root_operator, operators, remaining_comparisons, limit = gather_components(string)
    
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

# TODO: limit must not be used in query, just return first n items from results list

# print(construct_filter(st))


# st = "and(or(eq(\"country\", \"United Kingdom\"), eq(\"country\", \"Germany\"), eq(\"country\", \"Poland\")), eq(\"maxoccupancy\", 2), eq(\"mealsincluded\", False), limit=None)"


# filter_for_structured_query = construct_filter(st)

# query = "Apartment"
# structured_query = StructuredQuery(
#         query=query,
#         filter=filter_for_structured_query,
#     )

# query, search_kwargs = ChromaTranslator().visit_structured_query(structured_query)


import json
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()


# print(latest_price.iloc[:50])

docs = []
for _, room in latest_price.iloc[:50].fillna("").iterrows():
    doc = Document(
        page_content=json.dumps(room.to_dict(), indent=2),
        metadata=room.to_dict()
    )
    docs.append(doc)

db = Chroma.from_documents(docs, embeddings)

docs = db.search(query, 'similarity', **search_kwargs)
# print(docs)


for document in docs:
    print(document.page_content)


# op1 = Operation(
#         operator=Operator.OR,
#         arguments=[
#             Comparison(comparator=Comparator.EQ, attribute="country", value='Germany'),
#             Comparison(comparator=Comparator.EQ, attribute="country", value='Poland'),
#             Comparison(comparator=Comparator.GT, attribute="onsiterate", value=1),
#         ],
#     )

# filter_for_structured_query = Operation(
#         operator=Operator.AND,
#         arguments=[
#             op1,
#             Comparison(comparator=Comparator.GT, attribute="onsiterate", value=1),

#         ],
#     )

# query = "Room"
# structured_query = StructuredQuery(
#         query=query,
#         filter=filter_for_structured_query,
#     )

# query, search_kwargs = ChromaTranslator().visit_structured_query(structured_query)


# print(search_kwargs)

# import json
# from langchain.schema import Document
# from langchain.vectorstores import Chroma
# from langchain.embeddings import OpenAIEmbeddings
# embeddings = OpenAIEmbeddings()


# # print(latest_price.iloc[:50])

# docs = []
# for _, room in latest_price.iloc[:1000].fillna("").iterrows():
#     doc = Document(
#         page_content=json.dumps(room.to_dict(), indent=2),
#         metadata=room.to_dict()
#     )
#     docs.append(doc)

# db = Chroma.from_documents(docs, embeddings)

# docs = db.search(query, 'similarity', **search_kwargs)
# # print(docs)


# for document in docs:
#     print(document.page_content)
