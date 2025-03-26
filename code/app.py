from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
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
from pymongo import MongoClient
from marshmallow import Schema, fields, ValidationError
from flask_cors import CORS  # To allow frontend to make requests

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load JSON files
file_path = os.path.join(BASE_DIR, "products.json")

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)


logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Connect to MongoDB
client = MongoClient("mongodb+srv://stark:Murali123@cluster0.qq2ou.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['USER_DATA']
collection = db['user_profile']

app = Flask(__name__)
app.secret_key = 'code-sprinters'
CORS(app)



class EmployerSchema(Schema):
    name = fields.Str(required=True)
    type = fields.Str(required=True)

class AddressSchema(Schema):
    city = fields.Str(required=True)
    zip_code = fields.Str(required=True)
    country = fields.Str(required=True)

class CustomerSchema(Schema):
    customer_id = fields.Str(required=True)
    full_name = fields.Str(required=True)
    dob = fields.Str(required=True)
    gender = fields.Str(required=True)
    marital_status = fields.Str(required=True)
    nationality = fields.Str(required=True)
    occupation = fields.Str(required=True)
    industry = fields.Str(required=True)
    education_level = fields.Str(required=True)
    employer = fields.Nested(EmployerSchema, required=True)
    annual_income_bracket = fields.Str(required=True)
    dependents_count = fields.Int(required=True)
    address = fields.Nested(AddressSchema, required=True)
    phone_number = fields.Str(required=True)
    email = fields.Str(required=True)

class RelationshipInsightsSchema(Schema):
    spouse = fields.Dict(keys=fields.Str(), values=fields.Str())
    children = fields.List(fields.Str())
    linked_accounts = fields.List(fields.Str())

class FinancialTransactionSchema(Schema):
    type = fields.Str(required=True)
    amount = fields.Float(required=True)
    date = fields.Str(required=True)

class FinancialTransactionsSchema(Schema):
    deposits_withdrawals = fields.List(fields.Nested(FinancialTransactionSchema))
    spending_categories = fields.Dict(keys=fields.Str(), values=fields.List(fields.Float()))
    bill_payments = fields.Dict(keys=fields.Str(), values=fields.List(fields.Float()))

class LoanSchema(Schema):
    type = fields.Str(required=True)
    amount = fields.Float(required=True)
    emi = fields.Float(required=True)
    status = fields.Str(required=True)

class CreditCardSchema(Schema):
    type = fields.Str(required=True)
    limit = fields.Float(required=True)
    usage = fields.List(fields.Float())
    due_date = fields.Str(required=True)
    late_payments = fields.Int(required=True)

class BankingProductsSchema(Schema):
    accounts = fields.Dict(keys=fields.Str(), values=fields.Bool())
    loans = fields.List(fields.Nested(LoanSchema))
    credit_cards = fields.List(fields.Nested(CreditCardSchema))
    investments = fields.Dict(keys=fields.Str(), values=fields.List(fields.Float()))
    insurance = fields.Dict(keys=fields.Str(), values=fields.Bool())

class DigitalBankingSchema(Schema):
    preferred_channels = fields.List(fields.Dict())

class CustomerDataSchema(Schema):
    Customer = fields.Nested(CustomerSchema, required=True)
    RelationshipInsights = fields.Nested(RelationshipInsightsSchema, required=True)
    FinancialTransactions = fields.Nested(FinancialTransactionsSchema, required=True)
    BankingProducts = fields.Nested(BankingProductsSchema, required=True)
    DigitalBanking = fields.Nested(DigitalBankingSchema, required=True)


CATEGORY_MAPPING = {
    "grocery": "cards",  # Credit cards with grocery rewards
    "dining": "cards",  # Dining reward credit cards
    "travel_fuel": "credit_loan_products",  # Travel loans, fuel credit cards
    "entertainment": "cards",  # Entertainment-focused cards
    "shopping": "cards",  # Shopping cashback/reward credit cards
    "healthcare": "insurance_protection_plans",  # Health insurance
    "education": "credit_loan_products",  # Education loans
}


# Organize products by category
products_by_category = {}

for category in data["financial_products"]:
    category_name = category["category"]
    products_by_category[category_name] = category["products"]

# Convert to DataFrame-like structure (Dictionary of DataFrames)
products_df = {category: pd.DataFrame(products) for category, products in products_by_category.items()}

# Content-Based Filtering (TF-IDF + Cosine Similarity)
def content_based_recommendation():
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(products_df["about"])
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Find best matches for user
    recommended_indices = similarity_matrix.sum(axis=0).argsort()[-5:][::-1]
    recommendations = products_df.iloc[recommended_indices]
    
    # Keep only 'about' and 'eligible_customers' fields
    return recommendations[["name", "about", "eligible_customers"]].to_dict(orient="records")


def personalized_recommendation():
    if 'user' not in session:
        return {}

    full_name = session['user']
    user = collection.find_one({"Customer.full_name": full_name})
    print("Fetched User:", user)

    if not user:
        logger.warning(f"No user data found for: {full_name}")
        return {}

    spending_categories = user.get("FinancialTransactions", {}).get("spending_categories", {})
    print("Spending Categories:", spending_categories)

    # Sort categories by highest spending first
    sorted_categories = sorted(spending_categories.items(), key=lambda x: sum(x[1]), reverse=True)
    recommendations = {}

    vectorizer = TfidfVectorizer(stop_words="english")

    # Print available product categories
    print("Available Product Categories:", list(products_df.keys()))

    for user_category, _ in sorted_categories[:3]:  # Top 3 spending categories
        if user_category in CATEGORY_MAPPING:
            product_category = CATEGORY_MAPPING[user_category]  # Get mapped financial category
            print(f"🔄 Mapping User Category '{user_category}' → Product Category '{product_category}'")

            if product_category in products_df:
                relevant_products = products_df[product_category]
                print(f"Relevant Products for {product_category}:", relevant_products)

                if not relevant_products.empty:
                    # Ensure 'about' column exists
                    if "about" not in relevant_products.columns:
                        print(f"⚠️ Missing 'about' column for {product_category}")
                        continue

                    # Compute TF-IDF similarity
                    tfidf_matrix = vectorizer.fit_transform(relevant_products["about"])
                    print(f"TF-IDF Shape for {product_category}:", tfidf_matrix.shape)

                    if tfidf_matrix.shape[0] == 0:
                        print(f"⚠️ Empty TF-IDF matrix for {product_category}")
                        continue

                    user_vector = vectorizer.transform([f"Spends on {user_category}"])
                    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()
                    recommended_indices = similarity_scores.argsort()[-3:][::-1]
                    filtered_recommendations = relevant_products.iloc[recommended_indices]

                    # Convert DataFrame to dictionary and replace NaN values with None
                    filtered_recommendations = filtered_recommendations.replace({np.nan: None}).to_dict(orient="records")
                    recommendations[product_category] = filtered_recommendations

    print("Final Recommendations:", recommendations)
    return recommendations

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

        # Debugging: Check if MongoDB is connected
        try:
            logger.info("Checking MongoDB connection...")
            db_status = client.server_info()  # This will throw an error if MongoDB is not connected
            logger.info("MongoDB Connection: Successful")
        except Exception as e:
            logger.error(f"Mongo Connection Error: {str(e)}")
            return jsonify({"success": False, "message": "Database connection failed"}), 500

        logger.info(f"User Login Attempt - Customer ID: {customer_id}, Full Name: {full_name}")

        try:
            user = collection.find_one({"Customer.customer_id": customer_id, "Customer.full_name": full_name})
            if user:
                logger.info(f"User found in MongoDB: {user}")
                session['user'] = full_name
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
        db_status = client.server_info()  # This will throw an error if MongoDB is not connected
        return jsonify({"status": "Connected", "message": "MongoDB is working fine"})
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {str(e)}")
        return jsonify({"status": "Failed", "message": str(e)}), 500


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    recommendations = personalized_recommendation()
    
    # Debugging - Check if recommendations structure is correct
    print("Final Recommendations Structure:", recommendations)
    
    return render_template("index1.html", recommendations=recommendations)


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
            full_name = session['user']
            user_profile = collection.find_one({"Customer.full_name": full_name})
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
