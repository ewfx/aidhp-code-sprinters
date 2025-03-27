from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, Response
from utils import call_openai_service
import logging
import json
import os
import openai
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient
from marshmallow import Schema, fields, ValidationError
from flask_cors import CORS  
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

file_path = os.path.join(BASE_DIR, "products.json")

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)


logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

client_1 = MongoClient("mongodb+srv://stark:Murali123@cluster0.qq2ou.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db_1 = client_1['USER_DATA']
user_health_collection = db_1["user_health_profile"]
collection_user = db_1['user_profile']

client_2 = MongoClient("mongodb+srv://alan_stark:Murali123@cluster0.fniocgq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db_2 = client_2['USER_DATA']
collection_target = db_2['user_vector_store']

services_plans = client_1["services_plans"] 
health_services_catalog = services_plans["health_care_services"] 

app = Flask(__name__)
app.secret_key = 'code-sprinters'
CORS(app)

with open("products.json", "r") as f:
    products_catalog = json.load(f)
with open("user_schema.json", "r") as file:
    user_profile = json.load(file)

CATEGORY_MAPPING = {
    "grocery": "deposit accounts",  
    "dining": "cards", 
    "travel_fuel": "credit_loan_products",  
    "entertainment": "cards", 
    "shopping": "credit_loan_products",
    "healthcare": "insurance_protection_plans",  
    "education": "investment_wealth_management", 
}


products_by_category = {}

for category in data["financial_products"]:
    category_name = category["category"]
    products_by_category[category_name] = category["products"]

products_df = {category: pd.DataFrame(products) for category, products in products_by_category.items()}

def content_based_recommendation():
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(products_df["about"])
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    recommended_indices = similarity_matrix.sum(axis=0).argsort()[-5:][::-1]
    recommendations = products_df.iloc[recommended_indices]
    
    return recommendations[["name", "about", "eligible_customers"]].to_dict(orient="records")

 

def graph_based_recommendation():
    
    if 'user' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    customer_id = session['user']
    user_data = collection_user.find_one({"Customer.customer_id": customer_id})

    if not user_data:
        return jsonify({"error": "User not found"}), 404

    
    relationships = user_data.get("RelationshipInsights", {})
    related_customer_ids = set()

    if "spouse" in relationships:
        related_customer_ids.add(relationships["spouse"]["customer_id"])
    if "parents" in relationships:
        related_customer_ids.update(relationships["parents"])
    if "linked_accounts" in relationships:
        related_customer_ids.update(relationships["linked_accounts"])


    related_products = set()
    for rel_customer_id in related_customer_ids:
        related_user = collection_user.find_one({"Customer.customer_id": rel_customer_id})
        if related_user and "BankingProducts" in related_user:
            for category, products in related_user["BankingProducts"].items():
                if isinstance(products, list): 
                    for product in products:
                        related_products.add(product["type"])
                elif isinstance(products, dict):  
                    for product, owned in products.items():
                        if owned:
                            related_products.add(product)


    product_list = []
    for category in products_catalog["financial_products"]:
        for product in category["products"]:
            product["category"] = category["category"]
            product_list.append(product)

    products_df = pd.DataFrame(product_list)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(products_df["about"])

    user_vector = vectorizer.transform([" ".join(related_products)])
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()
    recommended_indices = similarity_scores.argsort()[-15:][::-1]  

    recommended_products = products_df.iloc[recommended_indices]

    user_owned_products = set()
    for category, products in user_data.get("BankingProducts", {}).items():
        if isinstance(products, list):
            for product in products:
                user_owned_products.add(product["type"])
        elif isinstance(products, dict):
            for product, owned in products.items():
                if owned:
                    user_owned_products.add(product)

    final_recommendations = [
    {key: (None if pd.isna(value) or value is np.nan else value)  
     for key, value in product.to_dict().items()}  
    for _, product in recommended_products.iterrows()
    if product["name"] not in user_owned_products
    ]


    return final_recommendations

def get_similar_users_recommendations():

    if 'user' not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    customer_id = session['user'] 
    user_data = collection_user.find_one({"Customer.customer_id": customer_id})
    
    if not user_data:
        return jsonify({"error": "User data not found"}), 404
    
    query_result = collection_target.find_one({"customer_id": customer_id})
    if not query_result:
        return jsonify({"error": "Embedding not found for user"}), 404
    
    query_vector = query_result["embedding"]
    
    pipeline = [
        {"$vectorSearch": {
            "index": "profile_index",
            "path": "embedding",
            "queryVector": query_vector,
            "exact": True,
            "limit": 5
        }}
    ]
    results = db_2["user_vector_store"].aggregate(pipeline)
    
    similar_users = [user["customer_id"] for user in results]

    banking_products = set()
    for cust_id in similar_users:
        user_profile = collection_user.find_one({"Customer.customer_id": cust_id})
        if user_profile and "BankingProducts" in user_profile:
            products = user_profile["BankingProducts"]
            banking_products.update(
                set(products.get("accounts", {}).keys()) |  
                {loan["type"] for loan in products.get("loans", [])} |  
                set(products.get("investments", {}).keys()) |  
                set(products.get("insurance", {}).keys()) |  
                {card["type"] for card in products.get("credit_cards", [])}  
            )
 
    
    
    recommended_products = []
    for category in products_catalog["financial_products"]:
        for product in category["products"]:
            if product["name"] in banking_products:
                recommended_products.append(product)  
   
    return recommended_products


def recommend_health_services():
    if 'user' not in session:
        return {}

    customer_id = session['user']

    user_profile = json.loads(json.dumps(user_health_collection.find_one({"user_id": customer_id}, {"_id": 0}))) 

    health_catalog = json.loads(json.dumps(health_services_catalog.find_one({}, {"_id": 0})))

    recommendations = {"user_id": user_profile["user_id"], "recommended_services": []}

    user_id_int = int(user_profile["user_id"])
    if user_id_int > 700:
        age_group = "senior_citizen"
    elif 500 <= user_id_int <= 520:
        age_group = "mid_career"
    else:
        age_group = "student_early_career"

    annual_expenses = int(user_profile["financial_health"]["health_spending"]["annual_medical_expenses"].strip("$").replace(",", ""))
    active_loans = user_profile["financial_health"]["medical_loan_status"]["active_loans"]
    avg_steps = user_profile["wellness_activity"]["fitness_expenses"]["average_steps_per_day"]
    mental_health_subscription = user_profile["wellness_activity"]["mental_health"]["subscription"]
    
    last_session_str = user_profile["wellness_activity"]["mental_health"]["last_session"]
    last_session_date = datetime.strptime(last_session_str, "%Y-%m-%d")
    days_since_last_session = (datetime.today() - last_session_date).days

    # --- Rule 1: Recommend Health Insurance Plan based on Age Group ---
    for plan in health_catalog["health_services_catalog"]["health_insurance_wellness_plans"]:
        if age_group == "senior_citizen" and plan["name"] == "Senior Citizen Health Plan":
            recommendations["recommended_services"].append({
                "service": plan["name"],
                "reason": "As a senior, you qualify for a plan designed to cover hospitalization, OPD, and medicines."
            })
        elif age_group == "mid_career" and plan["name"] == "Family Health Plan":
            recommendations["recommended_services"].append({
                "service": plan["name"],
                "reason": "We care your family much, our Family Health Plan can cover your family needs."
            })
        elif age_group == "student_early_career" and plan["name"] == "Basic Health Cover":
            recommendations["recommended_services"].append({
                "service": plan["name"],
                "reason": "A medical plan for young individuals like you, covering basic health needs."
            })

    # --- Rule 2: Recommend Financing Options if expenses are high or active loans exist ---
    if annual_expenses > 5000 or active_loans:
        for product in health_catalog["health_services_catalog"]["medical_financing_health_savings"]:
            if product["name"] == "Medical Emergency Loan":
                recommendations["recommended_services"].append({
                    "service": product["name"],
                    "reason": "Your medical spending or existing loans indicate that financing options might help manage costs."
                })
                break

    # --- Rule 3: Recommend Wellness Programs for active users ---
    if avg_steps > 7000:
        for partnership in health_catalog["health_services_catalog"]["exclusive_health_partnerships"]:
            if partnership["name"] == "Fitness & Lifestyle Programs":
                recommendations["recommended_services"].append({
                    "service": partnership["name"],
                    "reason": "Your high daily activity suggests you could benefit from exclusive discounts on gym memberships and wellness coaching."
                })
                break

    # --- Rule 4: Recommend Mental Health Support if no recent session or no subscription ---
    if days_since_last_session > 60 or mental_health_subscription.lower() == "none":
        for partnership in health_catalog["health_services_catalog"]["exclusive_health_partnerships"]:
            if partnership["name"] == "Corporate Health Benefits":
                recommendations["recommended_services"].append({
                    "service": partnership["name"],
                    "reason": "Your mental health session was over 60 days ago, or you don't have a subscription. Consider Corporate Health Benefits for mental wellness support."
                })
                break

    # --- Rule 5: Recommend Health Savings Account (HSA) if high expenses or medical loan ---
    if annual_expenses > 7000 or active_loans:
        for product in health_catalog["health_services_catalog"]["medical_financing_health_savings"]:
            if product["name"] == "Health Savings Account (HSA)":
                recommendations["recommended_services"].append({
                    "service": product["name"],
                    "reason": "Since you have high medical expenses or active loans, an HSA can help you save money tax-free for future medical costs."
                })
                break
    
    return recommendations["recommended_services"]

def print_pretty_json(bot_reply):
    try:
        print(json.dumps(bot_reply, indent=4, ensure_ascii=False))
    except json.JSONDecodeError:
        print("Invalid JSON response:", bot_reply)


@app.route("/products.json")
def serve_products():
    return send_from_directory(BASE_DIR, "products.json")

@app.route("/user_schema.json")
def serve_user_schema():
    return send_from_directory(BASE_DIR, "user_schema.json") 
  
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))


    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        full_name = request.form.get('full_name')

        try:
            logger.info("Checking MongoDB connection...")
            db_status = client_1.server_info()  
            logger.info("MongoDB Connection: Successful")
        except Exception as e:
            logger.error(f"Mongo Connection Error: {str(e)}")
            return jsonify({"success": False, "message": "Database connection failed"}), 500

        logger.info(f"User Login Attempt - Customer ID: {customer_id}, Full Name: {full_name}")

        try:
            user = collection_user.find_one({"Customer.customer_id": customer_id, "Customer.full_name": full_name})
            if user:
                logger.info(f"User found in MongoDB: {user}")
                session['user'] = customer_id
                print(session)
                return jsonify({"success": True, "message": "Login successful"})
            else:
                logger.warning("Invalid login attempt - User not found in database")
                return jsonify({"success": False, "message": "Invalid Customer ID or Full Name"}), 401
        except Exception as e:
            logger.error(f"Error querying MongoDB: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": "Database query failed"}), 500

    return render_template('login.html')

@app.route('/debug/mongodb')
def debug_mongodb():
    try:
        logger.info("Checking MongoDB connection manually...")
        db_status = client_1.server_info() 
        return jsonify({"status": "Connected", "message": "MongoDB is working fine"})
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {str(e)}")
        return jsonify({"status": "Failed", "message": str(e)}), 500


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_recommendations = get_similar_users_recommendations()  
    relationship_recommendations = graph_based_recommendation() 
    healthcare_recommendations = recommend_health_services()

    return render_template(
        "index1.html", 
        user_recommendations=user_recommendations, 
        relationship_recommendations=relationship_recommendations,
        healthcare_recommendations=healthcare_recommendations
    )


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

    
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    system_prompt = f"""You are an intelligent reasoning assistant helping a user with their question.".  
    Your task is to analyze the intent of the question and respond accordingly:  
    1. **Casual Conversation**:  
    - If the user's message is general chat, respond casually.  
    - Set `"category"` as `"casual"`.  
    - Provide an appropriate casual response in the `"response"` key.  

    2. **Banking Product Inquiry**:  
     - If the user is asking about banking products, determine the relevant category.  
     - The available categories are:  
     - `"deposit_accounts"`  
     - `"credit_loan_products"`  
     - `"investment_wealth_management"`  
     - `"insurance_protection_plans"`  
     - `"cards"`  
    - Select the most appropriate category based on the user's intent.  
    - Set `"category"` to the selected category. """

    user_prompt=f"""The user asks: "{user_message}". Do not add additional content in the respone. Provide only json output.
    **Output Format (JSON):**  
    {{
    "category": "<'casual' or one of the banking categories>",
    "response": "<casual response or empty if providing category>"
    }}  
    """

    result = call_openai_service(system_prompt, user_prompt,logger) 
    try:
        result = result.strip()
        if result.startswith('```json'):
            result = result.split('```json')[1].split('```')[0].strip()
        elif result.startswith('```'):
            result = result.split('```')[1].split('```')[0].strip()
                
        final_result = json.loads(result)
        if final_result["category"] == "casual":
            bot_reply = final_result["response"]
        else:
            category = final_result["category"]
            list_of_categories = data.get("financial_products", []) 
            products = None
            for item in list_of_categories:
                if item.get("category") == category:
                    products = item.get("products")
                    break
            
            system_prompt_1 = (
            f"You are an intelligent reasoning assistant helping a user find the most suitable product.\n"
            f"Your task is to analyze the product catalog and the user's profile to recommend the top 3 most relevant products.\n"
            f"For each recommended product, provide a brief explanation of why it is a great fit for the user.\n"
            f"**Output Format:**\n"
            f"- The response must be in **JSON format**.\n"
            f'- Use the key **"products"** with a list of JSON objects, each representing a recommended product.\n'
            f'- Each product JSON must have only two keys "name" as product name and "reason" as explanation to user reasoning why the user needs it.\n'
            f" The explanations added to reason fields should be concise , limited to one or two lines,in second person tone and provide clear explanation to the user.\n"
            f"**Constraints:**\n"
            f"- Provide **only** the JSON response.\n"
            f"- Do **not** add extra content or explanations outside the JSON output.\n"
            f"- The response should include **exactly 3 products**.\n")

            user_prompt_1 = (
                f"The user is interested in the {category} category. They have the following profile:\n"
                f"{user_profile}\n"
                f"products: {products}"
                )
            
            result_1 = call_openai_service(system_prompt_1, user_prompt_1,logger)
            result_1 = result_1.strip()
            
            if result_1.startswith('```json'):
                result_1 = result_1.split('```json')[1].split('```')[0].strip()
            elif result_1.startswith('```'):
                result_1 = result_1.split('```')[1].split('```')[0].strip()
                
            bot_reply = json.loads(result_1)

    except Exception as parse_error:
        logger.error(f"Error parsing intend response: {str(parse_error)}", exc_info=True)                 
        bot_reply =  "an error occured"

    response_to_send = bot_reply
    return jsonify(response_to_send)

if __name__ == "__main__":
    app.run(debug=True)
