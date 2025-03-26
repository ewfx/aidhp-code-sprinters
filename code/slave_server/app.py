from flask import Flask, render_template, request, jsonify
import logging
import json
from pymongo.mongo_client import MongoClient 
from sentence_transformers import SentenceTransformer
from utils import get_openai_reasoning

client = MongoClient("mongodb+srv://stark:Murali123@cluster0.qq2ou.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['vector_store']
collection = db['products']

logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2") 

app = Flask(__name__)
 
def get_constructs(data):
    profiles_list = data["users"]
    response = []
    for profile in profiles_list:
        construct = get_openai_reasoning(profile) 
       # print(construct)
        response.append({"id":profile["id"],"construct":construct}) 
    return response

@app.route("/sales_inbox",methods=["POST"])
def sales_inbox():
    if request.method == "POST":
        data = request.get_json()
        return jsonify(f"{"response": 'success'}") 
    
@app.route("/process", methods=["POST"])
def index():
    if request.method == "POST":
        logger.info("Processing requests in batches") 
        data = get_constructs(request.get_json())
        logger.info("Linguitics Constructs generated successfully")
        logger.info("Searching suitable recommendations")
        user_constructs = data
        response = []
        for item in user_constructs:
            query_vector = model.encode(item["construct"]).tolist() 
            pipeline = [
            {
            "$vectorSearch": {
                "index": "product_search",
                "path": "embedding",
                "queryVector": query_vector,
                "exact": True,
                "limit": 3
            }
            }
            ]
            results = db["products"].aggregate(pipeline) 
            recom_list = []

            for service in results:
                recom_list.append({"about":service["about"],"name":service["name"]})

            item_response = {"id": item["id"], "recommendations": recom_list}
            response.append(item_response) 
        logger.info("Recommendations generated successfully")
        return jsonify({"response":response})


if __name__ == "__main__":
    app.run(debug=True, port=8000)
