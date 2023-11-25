import os
import openai
import json
import json
import pandas as pd
from dotenv import load_dotenv

from langchain.chains.query_constructor.ir import StructuredQuery
from langchain.retrievers.self_query.chroma import ChromaTranslator
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from query_logic import construct_filter

load_dotenv()

openai.api_key = os.getenv('OPENAI_KEY')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_KEY')


model_name = "BAAI/bge-base-en-v1.5"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
EMBEDDINGS = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
DEFAULT_TRANSLATOR = ChromaTranslator()


def construct_raw_query(query):
    prompt = f"""
The list of all allowed comparators is : [eq, ne, gt, gte, lt, lte]
The list of all allowed fields is: [onsiterate, maxoccupancy, hotelname, city, country, starrating, mealsincluded]

The list of all fields is:

{{
    "onsiterate": {{
        "description": "The rate of the room. NOTE when user specifies the budget - use lte comparator",
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
        "description": "Whether meals are included or not. NOTE: must only be included when explicitly asked to",
        "type": "boolean"
    }}
}}

When user asks for things like cleaning service, AC, mini-bar, wifi, chairs, etc - include that into \\"query\\"

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
    "filters": "and(contain(\\"hotelname\\", \\"Top\\"), eq(\\"starrating\\", 2), lte(\\"onsiterate\\", 100))",
    "limit": "None"
}}

Query: Find me a hotel for 6 people and free wifi in France
output: 
{{
    "query": "hotel; Wi-Fi",
    "filters": "and(eq(\\"country\\", \\"France\\"), eq(\\"maxoccupancy\\", 6))",
    "limit": "None"
}}

Query: {query}
output:
"""

    message_log = [{"role":"user","content": prompt}]

    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_log,
            max_tokens=256,
            temperature=0,
            presence_penalty=0,
            frequency_penalty=0
        )
    data = response.choices[0].message.content

    return data


def get_search_parameters(query):
    raw = construct_raw_query(query)
    
    json_representation = json.loads(raw)

    query = json_representation['query']
    filter = json_representation['filters']
    limit = json_representation['limit']


    print(query)
    print(filter)


    filter_for_structured_query = construct_filter(filter)

    structured_query = StructuredQuery(
            query=query,
            filter=filter_for_structured_query,
        )

    query, search_kwargs = ChromaTranslator().visit_structured_query(structured_query)

    print(search_kwargs)

    limit = None if type(limit) != int else limit

    return query, search_kwargs, limit

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

#TODO: to insert data
# docs = []
# for idx, room in latest_price.iloc[:].fillna("").iterrows():
#     print(f'{idx}/ {len(list(latest_price.iloc[:].fillna("").iterrows()))}')
#     doc = Document(
#             page_content=json.dumps(room.to_dict(), indent=2),
#             metadata=room.to_dict()
#         )
#     docs.append(doc)

def answer(question):
    query, search_kwargs, limit = get_search_parameters(question)

    db = Chroma(persist_directory="data", embedding_function=EMBEDDINGS)

    docs = db.search(query, 'similarity', **search_kwargs, k=50 if not limit else limit)

    return [json.loads(doc.page_content) for doc in docs]


import streamlit as st

def display_data(data):
    for entry in data:
        st.markdown(
            f"""
            <div style="border: 2px solid #fff; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                <p>Name of place: <b>{entry.get("hotelname", "")}</b></p>
                <p>Type: <b>{entry.get("roomtype", "")}</b></p>
                <p>Price per night: <span style="font-size:16px; color:green;"><b>$ {entry.get("onsiterate", "")}</b></span></p>
                <p>Country: <b>{entry.get("country", "")}</b></p>
                <p>City: <b>{entry.get("city", "")}</b></p>
                <p>Suitable for: <b>{entry.get("maxoccupancy", "")}</b> people</p>
                <p>Stars: <b>{entry.get("starrating", "")}</b></p>
                <p>Luxuries: <b>{entry.get("roomamenities", "")}</b></p>
                <p>Meal: <b>{'Included' if entry.get("mealsincluded", "") == True else 'Not included'}</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

def main():
    st.title("Hotel Searcher")

    question = st.text_input("Input your requirements:")

    if question:
        answers = answer(question)
        if answers:
            display_data(answers)
        else:
            st.markdown(f'<div>No entries found</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
