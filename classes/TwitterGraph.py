import networkx as nx
from text_cleansing_step1 import Text_retrieve
from Instances import twitterInstance
from gensim.models import ldamodel
from gensim import corpora

class TwitterGraph:

    def __init__(self, fileName):
        self.G = nx.DiGraph()
        self.file_name = fileName

    def load_pickle(self):
        self.G = nx.read_gpickle(self.file_name)
    
    def write_pickle():
        nx.write_gpickle(self.G, self.file_name)
    
    def add_candidate(self, screen_name, max_followers, max_follower_friends):
        res = twitterInstance.api.get_user(screen_name)
        self.G.add_node(res.id, attr_dict = {'status_count': res.statuses_count, 
                                        'screen_name': res.screen_name})
        users = twitterInstance.fetchFollowers(res.id, limit=max_followers)
        
        for user in users:
            if not user.id in self.G.nodes():
                self.G.add_node(user.id, similarity = {})
            self.G.add_node(user.id, status_count = user.status_count, screen_name = user.screen_name )
            if not self.G.has_edge(user.id, res.id):
                self.G.add_edge(user.id, res.id, retweets=0)
            friends = twitterInstance.fetchFollowers(user.id, limit=max_follower_friends)

            for friend in friends:
                if not friend.id in self.G.nodes():
                    self.G.add_node(friend.id, similarity = {})
                self.G.add_node(friend.id, status_count = friend.status_count, screen_name = friend.screen_name )
                if not self.G.has_edge(user.id, friend.id):
                    self.G.add_edge(user.id, friend.id, retweets=0)

        self.write_pickle()

    def fetch_tweets_model(self, screen_name, max_tweets):
        res = twitterInstance.api.get_user(screen_name)
        tweets = twitterInstance.fetchTweets(screen_name, max_tweets)
        tweets_text = [tweet.message for tweet in tweets]
        text_retrieve = Text_retrieve(tweets)
        tweet_doc = text_retrieve.lemmatize()
        self.G.node[res.id]['tweet_doc'] = [word for tweet in tweet_doc for word in tweet]
        self.model, self.dictionary = self.createModel(tweet_doc)

    
    def createModel(self, doc):
        dictionary = corpora.Dictionary(doc)
        corpus = [dictionary.doc2bow(text) for text in doc]
        model = ldamodel.LdaModel(corpus, num_topics=10, id2word = dictionary)
        return model, dictionary

        

        