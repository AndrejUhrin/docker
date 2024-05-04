import time
import redis
from flask import Flask, render_template
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

load_dotenv() 
cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379,  password=os.getenv('REDIS_PASSWORD'))
app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route('/titanic')
def titanic():
    df = pd.read_csv('titanic.csv')
    survived_df = df[df['survived'] == 1]
    survived_by_gender = survived_df.groupby('sex').size()
    fig, ax = plt.subplots(figsize=(8, 6))
    ax = survived_by_gender.plot(kind='bar')
    ax.set_ylabel('Count')
    ax.set_title('Survival Count by Gender')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data_uri = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    table_html = df.head().to_html(classes='small-table', border=0)
    
    return render_template('titanic.html', table_html=table_html, plot_data_uri=plot_data_uri)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)