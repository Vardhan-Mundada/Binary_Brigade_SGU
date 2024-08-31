import json
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import joblib
from preprocess import preprocess_text
import warnings

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
# Download NLTK data
nltk.download('punkt')
nltk.download('wordnet')

# Load dataset
with open('data.json') as f:
    data = json.load(f)

intents = data['intents']
patterns = []
labels = []

for intent in intents:
    for pattern in intent['patterns']:
        patterns.append(preprocess_text(pattern))
        labels.append(intent['intent'])

# Encode labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(labels)

# Define a pipeline with text vectorization and classification
model = Pipeline([
    ('vect', CountVectorizer(tokenizer=nltk.word_tokenize)),
    ('clf', MultinomialNB())
])

# Train the model
model.fit(patterns, y)

# Save the model and label encoder
joblib.dump(model, 'chatbot_model.pkl')
joblib.dump(label_encoder, 'label_encoder.pkl')
