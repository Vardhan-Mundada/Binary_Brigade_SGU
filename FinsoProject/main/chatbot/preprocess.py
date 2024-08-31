from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer,PorterStemmer
import string

# Initialize lemmatizer and stop words

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    # Tokenize text
    tokens = word_tokenize(text)
    
    # Remove punctuation and convert to lower case
    tokens = [word.lower() for word in tokens if word.isalnum()]
    
    # Remove stop words
    tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatize tokens
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    tokens = [stemmer.stem(lemmatizer.lemmatize(word)) for word in tokens]
    
    
    return ' '.join(tokens)
