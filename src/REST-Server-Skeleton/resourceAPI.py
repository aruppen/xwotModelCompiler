class $classname(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super($classname, self).__init__()
        
    def get(self):
        return { 'temp': '50'}
