import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
# pd.set_option("display.max_rows", 12)

# ### Load the spreadsheet containing sample utterences

xlsx = pd.ExcelFile('utterence_samples.xlsx')
df = pd.read_excel(xlsx, 'utterences')
# df


# ### Format columns as required to train the classifier

X = np.array(df["UTTERENCES"])
y = np.array(df["INTENT"])


# from sklearn.cross_validation import train_test_split
# X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)


# ## Building a Model

# ### Punctuation remover, Tokenizer and Stemmer

# In[7]:

import string
from nltk import word_tokenize          
from nltk.stem.porter import PorterStemmer
import pandas as pd

stemmer = PorterStemmer()
def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    text = "".join([ch for ch in text if ch not in string.punctuation])
    tokens = word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems


# ### Train the classifier

# In[8]:

vect = TfidfVectorizer(tokenizer=tokenize,ngram_range=(1, 1),stop_words='english',strip_accents='unicode')


# In[9]:

# vect.fit_transform(np.array(['What is the amount of the structured loan portfolio of Natixis ?']))
# vect.get_feature_names()


# In[10]:

X_vect = vect.fit_transform(X)
vect.get_feature_names()


# In[11]:

clf = LinearSVC()
clf.fit(X_vect, y)


from sklearn.externals import joblib
joblib.dump(clf, 'qa_clf.pkl')  
joblib.dump(vect, 'vectorizer.pkl')
# joblib.dump(answers, 'answers.pkl')


# In[ ]:



