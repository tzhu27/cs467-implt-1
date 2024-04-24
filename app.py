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
def read_csv():
    df = pd.read_csv('static/data/twcs.csv')
    return df.to_dict(orient='records')

tweets = read_csv()

def get_companies():
    # Using list comprehension for readability and ensuring it returns a list
    return sorted(list({tweet['author_id'] for tweet in tweets if 'author_id' in tweet and not tweet['author_id'].isnumeric()}))

@app.route('/update-word-cloud', methods=['POST'])
def update_word_cloud():
    data = request.get_json()
    company = data.get('selectedCompany')
    stopwords_total = stopwords.words('english')
    words = {}
    for tweet in tweets:
        if tweet['author_id'] == company:
            text = tweet['text'].split(' ')
            # Check if a word contains only English letters.
            for word in text:
                if bool(re.match('^[a-zA-Z]+$', word)):
                    if word.lower() not in stopwords_total:
                        if word in words:
                            words[word] += 1
                        else:
                            words[word] = 1
    
    words_list = [[word, count] for word, count in words.items()]
    
    # Return a JSON response
    return jsonify(words_list[:500])

@app.route('/update-sentiment-analysis', methods=['POST'])
def update_sentiment_analysis():
    cont = pd.DataFrame(tweets)
    cont = cont.head(5000)
    data = request.get_json()
    company = data.get('selectedCompany')
    cont['language'] = cont['text'].apply(language_detection)
    cont = cont[cont['language'] == 'en']
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
    response_counts = {}
    for tweet in tweets:
        company_name = tweet['author_id']
        response_counts[company_name] = response_counts.get(company_name, 0) + 1
    
    # Sort and get top 20 companies
    sorted_companies = sorted(response_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    company_names = [company[0] for company in sorted_companies]
    response_rates = [count[1] for count in sorted_companies]
    
    return jsonify({'companyNames': company_names, 'responseRates': response_rates})

@app.route('/get-top20-comp-response-time')
def get_top20_comp_response_time():
    data = pd.DataFrame(tweets)
    data['created_at'] = pd.to_datetime(data['created_at'], format='%a %b %d %H:%M:%S %z %Y')
    data.sort_values('created_at', inplace=True)
    data['response_time'] = data.groupby('in_response_to_tweet_id')['created_at'].diff()
    company_responses = data[data['inbound'] == False]
    mean_response_times = company_responses.groupby('author_id')['response_time'].mean().dropna()
    sorted_companies = mean_response_times.sort_values()
    sorted_companies = sorted_companies.to_frame(name='mean_response_time')
    sorted_companies['rank'] = pd.qcut(sorted_companies['mean_response_time'], 5, labels=["Quickest", "Quick", "Medium", "Slow", "Slowest"])
    top_20_companies = sorted_companies.head(20)
    response = top_20_companies.to_json(orient='index')
    return jsonify(response)

@app.route('/')
def home():
    global tweets
    companies = get_companies()
    return render_template('index.html', companies=companies)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4356, debug=True)  # It's safer to not use host='0.0.0.0' and port=80 unless specifically needed
