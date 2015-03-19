

class Channel():
    id = ''
    title = ''
    path=''
    filterList = []
    categoryList = []
    type = ''
    parameters = dict()
    
    def __init__(self,id, title, path,type,filter,category,params):
        self.id = id
        self.title = title
        self.path = path
        self.filterList = filter
        self.categoryList = category
        self.type = type
        self.parameters = params