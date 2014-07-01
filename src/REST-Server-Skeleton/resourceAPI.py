from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

class $classname(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, location = 'json')
        self.reqparse.add_argument('description', type = str, location = 'json')
        self.reqparse.add_argument('done', type = bool, location = 'json')
        super($classname, self).__init__()

    def get(self, id):
        task = filter(lambda t: t['id'] == id, tasks)
        if len(task) == 0:
            abort(404)
        return { 'task': marshal(task[0], task_fields) }
        
    def put(self, id):
        task = filter(lambda t: t['id'] == id, tasks)
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        task['title'] = args.get('title', task['title'])
        task['description'] = args.get('description', task['description'])
        task['done'] = args.get('done', task['done'])
        return { 'task': marshal(task, task_fields) }

    def delete(self, id):
        task = filter(lambda t: t['id'] == id, tasks)
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        return { 'result': True }
