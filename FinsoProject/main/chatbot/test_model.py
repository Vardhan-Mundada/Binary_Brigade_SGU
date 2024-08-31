import json
import joblib
import nltk
from preprocess import preprocess_text
model = joblib.load('chatbot_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')
user_input = "Give me transactions of last 5 days spent on health."
preprocessed_input = preprocess_text(user_input)
prediction = model.predict([preprocessed_input])
intent = label_encoder.inverse_transform(prediction)[0]
print(intent)

categories = ['entertainment', 'groceries', 'utilities', 'transportation', 'food', 'education',"health"]
preprocessed_categories = [preprocess_text(category) for category in categories]


print(preprocessed_input)
print(preprocessed_categories)

def get_category_response(preprocessed_input):
    # Check for top spending or ranking queries
    if "top 5" in preprocessed_input or "highest spending" in preprocessed_input or "rank" in preprocessed_input:
        return "Here are the top 5 categories by spending: [Top categories details]"
    
    # Check for specific category queries
    for category in preprocessed_categories:
        if category in preprocessed_input:
            # Find the original category name corresponding to the preprocessed text
            original_category = categories[preprocessed_categories.index(category)]
            return f"Here’s the spending for {original_category}: [Specific category details]"
    
    # Default response if no specific category or top spending query is matched
    return "I can provide a detailed breakdown of your expenses by category."

    
ans = get_category_response(preprocessed_input)
print(ans)