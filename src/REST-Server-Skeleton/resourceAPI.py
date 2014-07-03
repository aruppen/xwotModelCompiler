class $classname(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super($classname, self).__init__()
        
    def get(self):
    	data = datagen.next()
    	accept_type = request.headers.get('Accept')
    	if accept_type == "application/json":
        	return { 'temp': data}
        else:
        	return data
