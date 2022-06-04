import mongoengine as me
from collections import deque

class Billionaire(me.Document):
    bill_id = me.IntField(required = True, pk = True)
    name = me.StringField(required = True, unique = True)
    age = me.IntField(required = True)
    worth = me.IntField(required = True)
    category = me.StringField(required = True)
    citizenship = me.StringField(required = True)
    gender = me.StringField(required = True)
    connectedTo = me.ListField()

    def add_connection(self, newPartner):
        self.connectedTo.append(newPartner)
        
    def get_connections(self):
        return self.connectedTo

    def __str__(self):
        return str(self.name) + ': '+ str(self.worth)

    def to_json(self):
        return {
            'name': self.name,
            'age': self.age,
            'worth': self.worth,
            'category': self.category,
            'citizenship': self.citizenship,
            'gender': self.gender
            }
class Graph:
    def __init__(self):
        self.billList = {}

    def addBillionaire(self, newBill):
        self.billList[newBill.name] = newBill
        return newBill

    def addEdge(self, f, t):
        'forms a connection between first and second vertices'
        self.billList[f.name].add_connection(t)
  
    def __iter__(self):
        return iter(self.billList.values())
    def __contains__(self, n):
        return n in self.billList 
    def __str__(self):
        return str({s.name: str(s.get_connections()) for s in self.billList.values()})
    def getBillionaire(self, n):
        if n in self.billList:
            return self.billList[n]
        else:
            return None
    def getBillionaires(self):
        return self.billList.keys()


def breadthFirstSearch(graph, start):
    '''
    graph - graph containing vertices which may have connections to other vertices

    start - billionaire vertex object, for whom the search is performed
    '''
    layers = {}
    visited = set()
    queue = deque([start])
    c = 1
    while queue:
        vertex = queue.popleft()
        if vertex not in visited:
            visited.add(vertex)
        circle_of_friends = set(vertex.get_connections()) - visited
        queue.extend(circle_of_friends)
        layers[c] = [f.name for f in circle_of_friends]
  
        c += 1
    layers = '  |  '.join(str(x) + ':' + str(layers[x]) for x in layers)
    return visited, layers
