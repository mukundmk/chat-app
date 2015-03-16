__author__ = 'mukundmk'

from py2neo import *

class Neo4jClient():
    def __init__(self, host=None, port=None, username=None, password=None):
        url = 'http://'
        if username:
            url += str(username)+':'+str(password)+'@'

        if host:
            url += str(host)
        else:
            url += 'localhost'

        if port:
            url += ':'+str(port)
        else:
            url += ':7474'

        url += '/db/data/'
        self.graph = Graph(url)

    def get_friends(self, user_id):
        res = self.graph.cypher.execute(
            'match (n:Person {id:{ID}})-[r:FriendsWith]->(m:Person)-[s:FriendsWith]->(n) return m.id as id',
            {'ID': str(user_id)})
        friends = []
        for i in res:
            friends.append(str(i.id))

        return friends

    def add_friend(self, user_id1, user_id2):
        self.graph.cypher.run(
            'match (n:Person {id:{ID1}}), (m:Person {id:{ID2}}) create unique (n)-[r:FriendsWith]->(m)',
            {'ID1': str(user_id1), 'ID2': str(user_id2)})

    def add_user(self, user_id):
        self.graph.cypher.run('create (n:Person {id:{ID}})', {'ID': str(user_id)})

    def get_added_user(self, user_id):
        res = self.graph.cypher.execute('match (n:Person)-[r:FriendsWith]->(m:Person {id:{ID}}) return n.id as id',
                                        {'ID': str(user_id)})
        friends = self.get_friends(str(user_id))
        added = list()
        for i in res:
            if str(i.id) not in friends:
                added.append(str(i.id))

        return added, friends

    def decline_friend(self, user_id1, user_id2):
        self.graph.cypher.run('match (n:Person {id:{ID1}})-[r:FriendsWith]->(m:Person {id:{ID2}}) delete r',
                              {'ID1': str(user_id1), 'ID2': str(user_id2)})

    def is_friend_of(self, user_id1, user_id2):
        res = self.graph.cypher.execute('match (n:Person {id:{ID1}})-[r:FriendsWith]->(m:Person {id:{ID2}}) return r',
                                        {'ID1': str(user_id1), 'ID2': str(user_id2)})
        if len(res) > 0:
            return True
        return False