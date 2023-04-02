import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def rec(name):
        nfMovies = pd.read_csv('netflix_titles.csv')
        data = nfMovies[['show_id', 'type', 'title', 'director', 'cast', 'country', 'rating', 'listed_in', 'description']]
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

        vectorizer=TfidfVectorizer(stop_words='english')
        response=vectorizer.fit_transform(df['tags'])
        cosine_similarities = linear_kernel(response,response)

        ind=df[df['title']==name].index[0]
        distances=cosine_similarities[ind]
        lis=sorted((list(enumerate(distances))),reverse=True, key=lambda x:x[1])[1:6]
        l = []
        for i in lis:
            l.append(df.iloc[i[0]].title)
        return l
