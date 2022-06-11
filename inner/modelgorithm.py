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

    def add_connection(self, newFriend):
        if newFriend not in self.connectedTo:
            self.connectedTo.append(newFriend)
            return True
        return False
        
    def get_connections(self):
        return self.connectedTo
    
    def del_connection(self, oldFriend):
        self.connectedTo.remove(oldFriend)

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
        '''forms a connection between first and
           second vertices'''

        self.billList[f.name].add_connection(t)
    
    def getBillionaire(self, n):
        if n in self.billList:
            return self.billList[n]
        else:
            return None

    def getBillionaires(self):
        return self.billList.keys()
  
    def __iter__(self):
        return iter(self.billList.values())

    def __contains__(self, n):
        return n in self.billList

    def __str__(self):
        return str({s.name: str(
          s.get_connections()) for s in self})

def bfs_paths(graph, start, goal):
    '''accepts existing graph vertices start and end,
       generates paths from start vertex to end vertex'''
       

    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next in set(graph.billList[vertex.name
                        ].get_connections()) - set(path):
            if next == goal:
                yield [x.name for x in path] + [next.name]
            else:
                queue.append((next, path + [next]))

def shortest_path(graph, start, goal):
    try:
        return next(bfs_paths(graph, start, goal))
    except StopIteration:
        return None

def breadthFirstSearch(graph, start):
    '''
    graph - graph containing vertices which may have
            connections to other vertices

    start - billionaire vertex object, for whom the search
            is performed
    '''
    layers = {}
    visited = set()
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        if vertex not in visited:
            visited.add(vertex)
        circle_of_friends = set(graph.billList[vertex.name
                                ].get_connections()) - visited
        if circle_of_friends:
            queue.extend(circle_of_friends)
            for friend in circle_of_friends:
                l = len(shortest_path(graph, start, friend)) - 1
                if not layers.get(l, 0):
                    layers[l] = [friend]
                else:
                    layers[l] += [friend]
      
    layers = '  |  '.join(str(x) + ':' + str([i.name for i in layers[x]
              ]) for x in layers)
    return visited, layers
