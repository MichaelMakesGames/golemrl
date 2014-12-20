class Material:
    def __init__(self,name,color,written_color,value):
        self.name = name
        self.color = color
        self.written_color = written_color
        self.value = value

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
