import pandas as pd
from flask import Flask, render_template, request, jsonify
import subprocess
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)
from langdetect import detect
from textblob import TextBlob

app = Flask(__name__)

def language_detection(text):
    try:
        language = detect(text)
        return(language)
    except:
        return('error')
    
def get_sentiment(text):
    blob = TextBlob(text)
    return 'positive' if blob.sentiment.polarity > 0 else 'negative' if blob.sentiment.polarity < 0 else 'neutral'



# Load tweets at app start
def read_csv(file):
    df = pd.read_csv(file)
    return df.to_dict(orient='records')

tweets = read_csv('static/data/twcs.csv')
t1 = read_csv('static/data/en.csv')

def get_companies():
    # Using list comprehension for readability and ensuring it returns a list
    return sorted(list({tweet['author_id'] for tweet in tweets if 'author_id' in tweet and not tweet['author_id'].isnumeric()}))

@app.route('/update-word-cloud', methods=['POST'])
def update_word_cloud():
    data = request.get_json()
    company = data.get('selectedCompany')
    stopwords_total = stopwords.words('english')
    custom_stopwords = ['dm', 'us', 'hi']
    words = {}
    for tweet in tweets:
        if tweet['author_id'] == company:
            text = tweet['text'].split(' ')
            # Check if a word contains only English letters.
            for word in text:
                if bool(re.match('^[a-zA-Z]+$', word)):
                    if word.lower() not in stopwords_total and word.lower() not in custom_stopwords:
                        if word in words:
                            words[word.lower()] += 1
                        else:
                            words[word.lower()] = 1
    
    words_list = [[word, count] for word, count in words.items()]
    
    # Return a JSON response
    return jsonify(words_list[:500])

@app.route('/update-sentiment-analysis', methods=['POST'])
def update_sentiment_analysis():
    keywords = ["raping", "shit", "problem", "issue", "unable"]
    cont = pd.DataFrame(t1)
    cont = cont.head(30000)
    data = request.get_json()
    company = data.get('selectedCompany')
    #cont['language'] = cont['text'].apply(language_detection)
    #cont = cont[cont['language'] == 'en']
    cont['sentiment'] = cont['text'].apply(get_sentiment)
    positive_words = pd.read_csv('static/data/positive-words.txt', skiprows=35, names=['words'])['words'].tolist()
    negative_words = pd.read_csv('static/data/negative-words.txt', skiprows=35, names=['words'])['words'].tolist()
    def count_words(tweets, words):
        word_count = {}
        c = 0
        for tweet in tweets:
            if company in tweet:
                text = tweet.split()
                for word in text:
                    if word in words:
                        if word not in keywords:
                            print(word)
                            if word in word_count:
                                word_count[word] += 1
                            else:
                                word_count[word] = 1
                            c += 1
        return word_count, c

    all_tweets = cont['text'].values
    pos_word_counts, posC = count_words(all_tweets, set(positive_words))
    neg_word_counts, negC = count_words(all_tweets, set(negative_words))
    pos_word = dict(pos_word_counts)
    neg_word = dict(neg_word_counts)
    posC = len(pos_word)
    negC = len(neg_word)
    sorted_pos = dict(sorted(pos_word_counts.items(), key=lambda item: item[1], reverse=True)[:10])
    sorted_neg = dict(sorted(neg_word_counts.items(), key=lambda item: item[1], reverse=True)[:10])
    return jsonify({'Company': company, 'PositiveWords': posC, 'NegativeWords': negC, 'Pos': sorted_pos, 'Neg': sorted_neg})

@app.route('/get-bar-chart-data')
def get_bar_chart_data():
    # Calculate response counts as before
    response_counts = {}
    for tweet in tweets:
        company_name = tweet['author_id']
        response_counts[company_name] = response_counts.get(company_name, 0) + 1

    # Sort and get top 20 companies based on response count
    sorted_companies = sorted(response_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    company_names = [company[0] for company in sorted_companies]
    response_rates = [count[1] for count in sorted_companies]

    # Convert created_at to datetime and sort
    data = pd.DataFrame(tweets)
    data['created_at'] = pd.to_datetime(data['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    data.sort_values('created_at', inplace=True)
    
    # Calculate response times only for the top 20 companies
    top_companies_data = data[data['author_id'].isin(company_names)]
    top_companies_data['response_time'] = top_companies_data.groupby('in_response_to_tweet_id')['created_at'].diff()

    # Calculate mean response time for each company in seconds and convert to hours
    mean_response_times = top_companies_data.groupby('author_id')['response_time'].mean().dt.total_seconds() / 3600
    mean_response_times = mean_response_times.reindex(company_names).fillna(0).tolist()  # Reindex to ensure the order matches company_names and fill missing data with 0

    # Return response rates and mean response times for the top 20 companies
    return jsonify({'companyNames': company_names, 'responseRates': response_rates, 'meanResponseTimes': mean_response_times})


@app.route('/')
def home():
    global tweets
    companies = get_companies()
    return render_template('index.html', companies=companies)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4356, debug=True)  # It's safer to not use host='0.0.0.0' and port=80 unless specifically needed
