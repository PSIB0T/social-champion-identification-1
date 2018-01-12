import json
import pandas as pd
from gensim import corpora
from gensim.models import lsimodel
from elasticsearch import Elasticsearch
from text_cleansing_step1 import Text_retrieve

class LSIModeling:

    def train(self, texts, num_topics=5, num_words=10):
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        self.model = lsimodel.LsiModel(corpus, num_topics=num_topics, id2word = dictionary)
        self.topics = []
        for topic in self.model.print_topics(num_topics=num_topics, num_words=num_words):
            self.topics.append(topic)
    
    def index(self):
        config = json.load(open("config.json", 'r'))
        elasticConfig = config['elasticsearch']
        self.es = Elasticsearch([{'host': elasticConfig['host'], 'port': elasticConfig['port']}])
        index = elasticConfig['index']
        doc_type = elasticConfig['doc_type']
        if not self.es.indices.exists(index):
            print("creating index")
            for i in range(len(lsimodel.topics)):
                self.es.create(index=index, doc_type=doc_type, id=i+1, body={"content": str(self.topics[i])})
    
    def topicDist(self, docs):
        textAndNoise = Text_retrieve(docs)
        lemmatized = textAndNoise.lemmatize()
        doc_dictionary = corpora.Dictionary(lemmatized)
        doc_bow = [doc_dictionary.doc2bow(text) for text in lemmatized]
        doc_sample = []
        for topic in self.model[doc_bow]:
            sample = [b for (a,b) in topic]
            doc_sample.append(sample)
        doc_topic_dist = pd.DataFrame(doc_sample,columns=[a for (a,b) in topic])
        return doc_topic_dist



