

class Channel():
    id = ''
    title = ''
    filterList = []
    categoryList = []
    extraList = []
    type = ''
    
    def __init__(self,id, title,filter,category,extra):
        self.id = id
        self.title = title
        self.filterList = filter
        self.categoryList = category
        self.extraList = extra
        self.type = type
