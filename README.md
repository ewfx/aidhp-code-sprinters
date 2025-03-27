# Modern Personalization Engine As a Service

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

### 🎯 Introduction
## Our Approach to Personalization  
We follow a simple yet powerful mantra:  

**Data + Interactions = Recommendations + Actionable Insights**  

Traditional systems struggle with contextual relationships and suffer from the cold-start problem. To overcome this, we leverage **Large Language Models (LLMs)** to build scalable personalization engines.
**Explainability** is at the core of our system, providing clear, data-driven reasoning behind every product or service recommendation for our banking customers.
Major computational tasks are offloaded as scheduled jobs, running periodically outside business hours to enhance reliability and minimize latency.  

---
## 🎥 Demo
[Video Demo](https://drive.google.com/file/d/1SHHJPrF3cci9GzqY4Z8p1HhokKAWsVv8/view?usp=sharing)



## 💡 Inspiration
LLMs have transformed application development, shifting from **keyword-based search to contextual search**, unlocking new ways to solve problems. A key focus area is **customer engagement**, which directly drives business growth. However, this shift brings challenges such as **scalability, explainability, and real-time processing**. Our goal is to embrace this evolution while proactively addressing these challenges to deliver innovative, efficient solutions.  


## ⚙️ What It Does
  
### 1. Recommendations for You  
Get **personalized financial product suggestions** tailored to your **spending habits, transactions, and financial profile**, ensuring you make the best investment and savings decisions.  

### 2. For the People You Love  
Receive **curated financial recommendations** for your **spouse, parents, or children** using **relationship-based insights** and **advanced graph-based TF-IDF models**.  

### 3. Healthcare Services  
Discover the **best available healthcare services and financial plans** based on your profile, helping you make informed **medical and insurance decisions**.  

### 4. Conversational Search Engine  
Ask about any financial product, and our **Fargo AI** will instantly analyze your needs to provide **smart, relevant recommendations** in a conversational manner.  

### 5. Boost Outreach with AI-Driven Recommendations  
Analyze **social media data** to deliver **personalized product suggestions** and **empower customer service** for impactful engagement. 

## 🛠️ How We Built It
### Data Sourcing Layer  
We collect data from multiple sources,including:  

- **Customer Information Profile (CIP)**  
- **KYC Documents**  
- **Voluntary Disclosures**  
- **Social Media Campaigns**  

Feature engineering is applied to extract relevant insights from the data warehouse, which are then stored in the application database.  

### Data Computation Layer  
At this stage, we:  

- **Generate linguistic constructs**  
- **Perform vectorization and embedding creation**  
- **Compute scoring and ranking** based on user and service data  

This ensures **highly relevant and personalized recommendations**.  
 
### Algorithmic Implementation  
We utilize a combination of advanced techniques, including:  

- **TF-IDF Vectorization** for relevance scoring  
- **Graph Modeling** to identify family relationships  
- **Intent Classification** for understanding user queries  
- **Embedding Search & Ranking** for precise recommendations  
- **Reasoning & Explanations** to enhance transparency  
- **LLM Integration** for intelligent, context-aware interactions
  
### Slave Server Implementation  
To enhance social media campaigns and outreach, we deploy a **dedicated server** that:  

- **Receives real-time campaign data**  
- **Queues and processes data in batches**  
- **Generates tailored financial service and product recommendations**  

This approach ensures **optimized customer engagement** and **higher outreach effectiveness**.  


## 🚧 Challenges We Faced
### Data Modeling Challenges  
One of the major challenges was **data modeling**, given the vast pool of data from both **customers** and **banking financial catalogs**. To address this, we:  

- **Identified relevant fields** to ensure meaningful insights  
- **Created synthetic data** to simulate real-time scenarios  
- **Modeled relationships using Graph-based structures**  
- **Designed a NoSQL database** for scalability and flexibility  

This approach enabled **efficient data handling and enhanced recommendation accuracy**.  
 

## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/your-repo.git](https://github.com/ewfx/aidhp-code-sprinters.git
   ```
2. Install dependencies  
   ```sh
   pip install -r requirements.txt
   ```

3. Run Master server
   ```sh
   python app.py
   ```
4. Run slave server
   ```sh
   cd slave-server 
   ```
   ```sh
   python app.py 
   ```

4. Make sure to create .env file with open-ai key
   ```sh
   OPENAI_API_KEY = <api-key>
   ```

## 🏗️ Tech Stack
- 🔹 Frontend: HTML/CSS/JavaScript
- 🔹 Backend: Flask 
- 🔹 Database: MongoDB
- 🔹 Others: Sentence Transformers | Open-ai as LLM service

## 👥 Team
- **Murali** - [GitHub](https://github.com/MuraliB123) | [LinkedIn](https://www.linkedin.com/in/muralib1729)  
- **Poojaa S** - [GitHub](https://github.com/poojaa1908) | [LinkedIn](https://www.linkedin.com/in/poojaa-s)
- **Sawthisri** - [Github](https://github.com/SwathishriJL) | [LinkedIn](https://www.linkedin.com/in/swathishri-jaisankar/)
- **Nithin** - [Linkedin](https://www.linkedin.com/in/nithin-srivatsan-0a885b236?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app)
