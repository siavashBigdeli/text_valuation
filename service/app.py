from flask import Flask, request, jsonify, abort
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from matplotlib import pyplot as plt
from matplotlib.cm import get_cmap
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib
import matplotlib as mpl
import numpy as np
import json
import pickle
import re


load_dotenv()

with open("measures", "rb") as fp:
    list_of_measures = pickle.load(fp)

def get_str(l):
    if type(l)==list:
        s = [get_str(j) for j in l]
        return '. '.join(s)
    return l

list_of_measures = list(map(get_str, list_of_measures))

regex = re.compile('[^0-9]')
def get_percentage(res):
    i = regex.sub('', res)
    try:
        return int(i)
    except:
        return 0


def plot_result(scores):
    mpl.use('Agg')
    matplotlib.rc('xtick', labelsize=20) 
    matplotlib.rc('ytick', labelsize=20) 
    plt.rcParams['font.family'] = ['DejaVu Sans']

    inds = np.argsort(scores)
    l = [get_display(arabic_reshaper.reshape(l[0][:200])) for l in list_of_measures[:32]]
    l = [get_display(arabic_reshaper.reshape(l[:200])) for l in list_of_measures]
    l = [l[i] for i in inds][:32]
    print(l)
    v = np.sort(scores)[:32]

    colors = []
    cmap = get_cmap('cool')
    for decimal in v:
        colors.append(cmap(decimal/100))


    fig, ax = plt.subplots(figsize=(50,100))

    hbars = ax.barh(range(32), v, color=colors, height=.1)
    ax.set_yticks(range(32))
    _ = ax.set_yticklabels(l)
    ax.spines[['right', 'top']].set_visible(False)
    plt.grid()
    plt.tight_layout()
    plt.savefig('1.png')

client = OpenAI()
app = Flask(__name__)


@app.route('/')
def main_page():
    return jsonify('This page not exists.'), 403


@app.route('/query', methods=['POST'])
def query():
    q = json.loads(request.form['query'])['query']
    is_plot = json.loads(request.form['query'])['is_plot']
    result = []
    futures = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for measures in list_of_measures:
            query = f"""
ک متن ورودی بهت میدم و یک متن معیار. بعد با توجه به متن معیار بگو چقدر نویسنده‌ی متن ورودی معیار را رعایت کرده. متن ورود
متن :
{measures}
جمله:
{q}

در پایان لطفا به من بگو این متن با جمله نسبت منفی داشته یا مثبت؟
            """
            futures.append(executor.submit(client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": query}
                ]
            ))
        for future in futures:
            result.append(future.result().choices[0].message.content)
    response = {"result" : result}
    if is_plot:
        plot_result(result)
    with open('1.txt', 'w') as f:
        f.write(' ============== '.join(result))
    return jsonify({"response" : result}), 201


if __name__ == '__main__':
    # app.run(debug=True)
    print(list_of_measures[1])