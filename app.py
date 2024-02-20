import pandas as pd
from flask import Flask, render_template, request, jsonify

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
    data = request.get_json()
    company = data.get('selectedCompany')
    
    positive_words = ["excellent", "awesome", "positive", "authentic", "resolved", "escalate", "taking action", "brilliant", "phenomenal"]
    negative_words = [
    "late", "delayed", "overdue", "awaiting delivery", "difficulty",
    "expired", "missing", "poor", "damaged", "unsafe",
    "disappointed", "expired", "unauthorized", "dispute", "barrier", "counterfeit",
    "hacked", "breached", "stolen", "discontinued", "frustration", "unsatisfactory",
    "horrible"
    ]

    
    positive_count = 0
    negative_count = 0
    sneg = {}
    spos = {}
    for tweet in tweets:
        if company in tweet['text']:
            text = tweet['text'].lower()  # Convert text to lowercase for case-insensitive matching
            for word in text.split():
                if word in positive_words:
                    if word in spos:
                        spos[word] += 1
                    else:
                        spos[word] = 1
                    positive_count += 1
                if word in negative_words:
                    if word in sneg:
                        sneg[word] += 1
                    else:
                        sneg[word] = 1
                    negative_count += 1
        
    # Return a JSON response with sentiment analysis results
    pos = dict(sorted(spos.items(), key=lambda item: item[1], reverse=True)[:5])
    neg = dict(sorted(sneg.items(), key=lambda item: item[1], reverse=True)[:10])

    return jsonify({'Company': company, 'PositiveWords': positive_count, 'NegativeWords': negative_count, 'Pos': pos, 'Neg': neg})

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
    app.run(host='0.0.0.0', port=4001, debug=True)  # It's safer to not use host='0.0.0.0' and port=80 unless specifically needed
