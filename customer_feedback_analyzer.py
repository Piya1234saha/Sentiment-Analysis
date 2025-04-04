# -*- coding: utf-8 -*-
"""Customer Feedback Analyzer

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LZ3NW_Mi-hdOOsck0V1aQ5UGHMnIYrkN
"""

import pandas as pd
import numpy as np
import plotly.express as px

"""Dataset Overview:


*   The guest_data_with_reviews.xlsx dataset contains customer feedback from a hospitality business.
*   Key columns include:
How likely are you to recommend us to a friend or colleague? for Net Promoter Score (NPS) calculations.
Review for textual feedback, useful for sentiment analysis and topic modeling.



"""

from google.colab import drive
drive.mount('/content/drive')

df=pd.read_excel("/content/guest_data_with_reviews.xlsx")

df.head()

#we can see some columns might have missing value. we are looking for calculating the NPS score.

# How many rows  in the dataset
total_len=len(df)
total_len

#Missing value
missing_values = df.isnull().sum()
print(missing_values)

#we can see Start time,Completion time, Name, Email, Full Name >> we dont have any value. we assume that is fine bcz we have to undersatnd the review of the customers

"""Missing Value Treatement

"""

#We have 1 miising value in the Gym indicator#
# here will not use dropna()>> bcz kit will completely detele missing rows in any of the columns

#1st drop the column and then rows with missing value.
df_cleaned= df.dropna(axis=1)
df_cleaned

"""Key Concepts:
Net Promoter Score (NPS): Measures customer loyalty.
Scores:
*   9–10: Promoters
*   7–8: Passives
*   0–6: Detractors

Formula: NPS = percentage of promoters - percentage of detractors
*   Sentiment Analysis: Identifies the emotional tone (positive, negative, or neutral) in reviews.


*   Topic Modeling: Uses embeddings to identify recurring themes in text data.




"""

#How likely are you recommend us?
likelyhood= px.histogram(df_cleaned, x="How likely are you to recommend us to a friend or colleague?",nbins=10,title="Distribution of Recommmendation Score" )

likelyhood.show()

#calculate NPS score:

#classify score Promoter(9-10), passive (7-8), Detractor(0-6)

#We have to create a function to define the NPs score:

def classify_NPS(Score):
  if Score>=9:
    return 'Promoters'
  elif Score>=7:
    return 'Passive'
  else:
    return 'Detractor'

#Apply the classification on the recommendation score

df_cleaned['NPS Score']=df_cleaned["How likely are you to recommend us to a friend or colleague?"].apply(classify_NPS)

df_cleaned

#Ratio of Promoters, Dectractor and Passive
NPS_proportions= df_cleaned["NPS Score"].value_counts(normalize=True)*100
NPS_proportions

#As Larger num of Promoters than Dectractors. So, we can say more negative number of feedback.Business is not going vwey well.

#Interprate and claculate the overall NPS
Promoters=df_cleaned[df_cleaned["NPS Score"]=="Promoters"].shape[0]
Detractors=df_cleaned[df_cleaned["NPS Score"]=="Detractor"].shape[0]
Passive=df_cleaned[df_cleaned["NPS Score"]=="Passive"].shape[0]
Total_response=df_cleaned.shape[0]

Promoters, Detractors, Passive, Total_response

nps_score=((Promoters-Detractors)/Total_response)*100
nps_score

if nps_score>0:
  nps_interpretation="Positive"
elif nps_score<0:
  nps_interpretation="Negative"
else:
  nps_interpretation="Neutral"

nps_score,nps_interpretation

# What does NPS value indicate about customer loyalty?
if nps_score>50:
  loyalty_interpretation="Excellent customer loyalty"
elif 0 <nps_score<=50:
  loyalty_interpretation="Good customer loyalty"
else:
  loyalty_interpretation="very poor customer loyalty"

nps_score,nps_interpretation, loyalty_interpretation

#Sentiment Analysis

from transformers import pipeline

sentiment_analzer = pipeline("sentiment-analysis")

#Extracts the first prediction ([0]) and gets its sentiment label (['label']).
df_cleaned['sentiment']=df_cleaned['Review'].apply(lambda review:sentiment_analzer(review)[0]['label'])

df_cleaned[['Review','sentiment']]

#Visualize sentiment analysis accross the distribution:

fig= px.histogram(df_cleaned,x="sentiment",
                 title= "Sentiment analysis accross the dataset")

fig.show()

sentiment_count=df_cleaned['sentiment'].value_counts()
sentiment_percentage=(df_cleaned['sentiment'].value_counts())/len(df_cleaned)*100

sentiment_percentage

#prepare a dataframe to show :

sentiment_df = pd.DataFrame({'Sentiment': sentiment_count.index,
                             'count': sentiment_count.values,
                             'percentage': sentiment_percentage.values})

sentiment_df

#what are the common keywords in the review:
#CountVectorizer >>help to count

from sklearn.feature_extraction.text import CountVectorizer
Review= df_cleaned['Review']

vectorizer= CountVectorizer(stop_words='english', max_features=20)

#Fit the data:

X= vectorizer.fit_transform(Review)

get_vocab= vectorizer.get_feature_names_out()

word_count=X.toarray().sum(axis=0)

#create a dataframe with word and count

keywords_df= pd.DataFrame({
    'keyword': get_vocab,
    'count': word_count
}).sort_values(by='count', ascending= False)

keywords_df

"""TF-IDF vectorization and Non-negative Matrix Factorization (NMF) help
to extract key topics


*   TfidfVectorizer: Converts text data into a matrix of TF-IDF (Term Frequency-Inverse Document Frequency) features
*    NMF: A machine learning technique used for topic modeling (identifying hidden topics in text).


*  n_components=5: The model will extract 5 topics.
*   Trains the NMF model on the TF-IDF matrix to identify 5 topics based on word distributions.

*   Returns a matrix where each row represents a topic, and each column represents the importance of a word in that topic.
*   List item







"""

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

#using emedding extract key topics
# Initialize the TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)

# Fit and transform the reviews
tfidf = tfidf_vectorizer.fit_transform(Review)

#Initialize the NMF Model

nmf=NMF(n_components=5, random_state=42)

#Fit the NMF
nmf.fit(tfidf)

#get the topic

topic=nmf.components_

#Get the feature names(Words)
feature_names=tfidf_vectorizer.get_feature_names_out()

#Dispaly the top words for each topic
num_topword=10
topics_df=pd.DataFrame()

for topic_idx, topic in enumerate(topic):
  top_word=[feature_names[i] for i in topic.argsort()[:-num_topword -1:-1]]
  topics_df[f'Topic{topic_idx+1}'] = top_word
topics_df



# Visualize results as a word cloud

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Function to plot word cloud for each topic
def plot_word_cloud(lda_model, feature_names, num_top_words):
    for topic_idx, topic in enumerate(lda_model.components_):
        word_freq = {feature_names[i]: topic[i] for i in topic.argsort()[:-num_top_words - 1:-1]}
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Topic {topic_idx+1}')
        plt.show()

# Plot word clouds for each topic
plot_word_cloud(lda, tfidf_feature_names, no_top_words)

#Its group the review based on topic

#bigger the size of the word may be more important
Key Takeaway:
Improving Wi-Fi, pricing transparency, and faster service can significantly boost customer satisfaction and increase NPS.

################################# To be continue ################