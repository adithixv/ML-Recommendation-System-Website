from flask import Flask, request, render_template
import mysql.connector
app = Flask(__name__)
mylist = []
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from fuzzywuzzy import fuzz


def rec(name):
        nf = pd.read_csv('netflix_titles.csv')
        data = nf[['show_id', 'type', 'title', 'director', 'cast', 'country', 'rating', 'listed_in', 'description']]
        data = data.fillna('')

        data['type']=data['type'].apply(lambda x:x.split())
        data['director'] = data['director'].apply(lambda x:x.split(","))
        data['cast'] = data['cast'].apply(lambda x:x.split(","))
        data['country']=data['country'].apply(lambda x:x.split(","))
        data['rating']=data['rating'].apply(lambda x:x.split())
        data['listed_in'] = data['listed_in'].apply(lambda x:x.split(","))
        data['description']=data['description'].apply(lambda x:x.split())

        col=['type', 'director', 'cast', 'country', 'rating', 'listed_in', 'description']
        for i in col:
            data[i]=data[i].apply(lambda x:[i.replace(" ","") for i in x])

        data['tags']=data['type']+data['director']+data['cast']+data['country']+data['rating']+data['listed_in']+data['description']
        df = data[['show_id', 'title', 'tags']]

        df['tags'] = df['tags'].apply(lambda x:' '.join(x))
        
        highest_score = -1
        best_match = ''

        for index, row in df.iterrows():
            score = fuzz.token_set_ratio(name, row['title'])
            if score > highest_score:
                highest_score = score
                best_match = row['title']
        
        vectorizer=TfidfVectorizer(stop_words='english')
        response=vectorizer.fit_transform(df['tags'])
        cosine_similarities = linear_kernel(response,response)

        ind=df[df['title']==best_match].index[0]
        distances=cosine_similarities[ind]
        lis=sorted((list(enumerate(distances))),reverse=True, key=lambda x:x[1])[1:6]
        l = []
        for i in lis:
            l.append(df.iloc[i[0]].title)
        return l


@app.route("/")
def main():
    return render_template("index.html")

@app.route("/reg", methods=['post'])
def reg():
    name=request.form["name"]
    password=request.form["password"]

    conn=mysql.connector.connect(user="root",host="localhost",password="snucc@123",database="users")
    cursor=conn.cursor()     
    if conn.is_connected():
           print("Connected")
    
    cursor.execute("SELECT * FROM accounts WHERE name = %s", (name,))
    user = cursor.fetchone()
    if user:
        error = 'Username already taken. Try Again.'
        return render_template('index.html', error=error)
    cursor.execute("INSERT INTO accounts (name,password)"
                   "values(%s,%s)",(str(name),str(password)))
    conn.commit()
    return render_template("home.html")
    

@app.route("/login",methods=['post'])
def login():
    nam=request.form["name"]
    pas=request.form["password"]

    conn=mysql.connector.connect(user="root",host="localhost",password="snucc@123",database="users")
    cursor=conn.cursor()     
    if conn.is_connected():
           print("Connected")
    
    cursor.execute('SELECT * FROM accounts WHERE name=%s and password=%s',(nam,pas))
    print("Done")
    rows=cursor.fetchone()
    if rows:
     return render_template("home.html")
    else:
        error="Invalid Username or Password. Try again."
        return render_template("login.html",error=error)



@app.route("/suggest",methods=["post"])
def suggest():
    movie=request.form["movie"]
    print(movie)
    try:
     mylist = rec(movie)
     print(mylist)
     return render_template("home.html", movie = movie, mylist=mylist)
    except:
     return render_template("home.html",err="Invalid Input. Try Again.")
    
    

@app.route("/signin")
def signin():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("index.html")


if __name__=='__main__':
    app.run(host='localhost',port=5000, debug=True)