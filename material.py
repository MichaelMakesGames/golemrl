class Material:
    def __init__(self,name,color,value):
        self.name = name
        self.color = color
        self.value = value

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
