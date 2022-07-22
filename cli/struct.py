class ArgElement:

    def __init__(self, layer: int = 1, is_end: bool = True):
        # properties
        self.layer: int = layer
        self.is_end: bool = is_end

        # data
        self.type_: type or list
        self.restriction: any

        # hierarchy
        self.sons = []
