import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

def read_csv() -> dict:
    df = pd.read_csv('twcs.csv')
    return df.to_dict(orient='records')

def get_companies(df_dict: list) -> dict:
    return {tweet['author_id'] for tweet in df_dict if 'author_id' in tweet and not(tweet['author_id'].isnumeric())}

@app.route('/')
def home():
    tweets_lst = read_csv()
    companies = get_companies(tweets_lst)

    return render_template('index.html', companies=companies)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)