import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load tweets at app start
def read_csv():
    df = pd.read_csv('twcs.csv')
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
    return jsonify(words_list)

@app.route('/')
def home():
    global tweets
    companies = get_companies()
    return render_template('index.html', companies=companies)

if __name__ == '__main__':
    app.run(debug=True)  # It's safer to not use host='0.0.0.0' and port=80 unless specifically needed
