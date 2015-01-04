class Material:
    def __init__(self,material_id,name,color,value):
        self.material_id = material_id
        self.name = name
        self.color = color
        self.value = value

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
