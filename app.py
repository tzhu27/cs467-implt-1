import pandas as pd
from flask import Flask, render_template, request, jsonify
from langdetect import detect
from textblob import TextBlob

app = Flask(__name__)

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
    
    words = {}
    for tweet in tweets:
        if tweet['author_id'] == company:
            text = tweet['text'].split(' ')
            for word in text:
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1
    
    words_list = [[word, count] for word, count in words.items()]
    
    # Return a JSON response
    return jsonify(words_list[:500])

@app.route('/update-sentiment-analysis', methods=['POST'])
def update_sentiment_analysis():
    # Create DataFrame from the tweets data
    cont = pd.DataFrame(tweets)
    cont = cont.head(5000)
    # Get JSON data from request
    data = request.get_json()
    company = data.get('selectedCompany')
    # Language Detection
    from langdetect import detect, DetectorFactory

    def language_detection(text):
        try:
            language = detect(text)
            return(language)
        except:
            return('error')

    cont['language'] = cont['text'].apply(language_detection)

    # Filter to English texts
    cont = cont[cont['language'] == 'en']
    # Sentiment Analysis
    def get_sentiment(text):
        blob = TextBlob(text)
        return 'positive' if blob.sentiment.polarity > 0 else 'negative' if blob.sentiment.polarity < 0 else 'neutral'
    
    cont['sentiment'] = cont['text'].apply(get_sentiment)
    # Load positive and negative words
    positive_words = pd.read_csv('static/data/positive-words.txt', skiprows=35, names=['words'])['words'].tolist()
    negative_words = pd.read_csv('static/data/negative-words.txt', skiprows=35, names=['words'])['words'].tolist()

    # Count positive and negative words
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

    # Sort and select top 10
    sorted_pos = dict(sorted(pos_word_counts.items(), key=lambda item: item[1], reverse=True)[:10])
    sorted_neg = dict(sorted(neg_word_counts.items(), key=lambda item: item[1], reverse=True)[:10])
    # Return JSON response

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


@app.route('/')
def home():
    global tweets
    companies = get_companies()
    return render_template('index.html', companies=companies)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4006, debug=True)  # It's safer to not use host='0.0.0.0' and port=80 unless specifically needed
