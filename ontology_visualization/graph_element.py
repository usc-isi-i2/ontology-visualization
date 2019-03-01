class Element:
    def __init__(self, id_, attrs=None):
        self.id = id_
        self.attrs = attrs if attrs else dict()

    def update(self, new_attrs):
        self.attrs.update(new_attrs)

    def to_draw(self):
        if self.attrs:
            attrs = ' '.join(['{}="{}"'.format(k, v) for k, v in self.attrs.items()])
            return '{} [{}]'.format(self.id, attrs)
        return self.id

    def set_color(self, color):
        self.attrs['color'] = color

    @staticmethod
    def text_justify(words, max_width):
        words = words.split()
        res, cur, num_of_letters = [], [], 0
        max_ = 0
        for w in words:
            if num_of_letters + len(w) + len(cur) > max_width:
                res.append(' '.join(cur))
                max_ = max(max_, num_of_letters)
                cur, num_of_letters = [], 0
            cur.append(w)
            num_of_letters += len(w)
        return res + [' '.join(cur).center(max_)]

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other):
        return isinstance(other, Element) and self.id == other.id

    def __repr__(self):
        return self.id


class Node(Element):
    def __init__(self, id_, attrs):
        super().__init__('"{}"'.format(id_), attrs)

    def set_color(self, color):
        super().set_color(color)
        self.attrs['fillcolor'] = color


class Edge(Element):
    def __init__(self, from_, to, attrs):
        if isinstance(from_, Node):
            from_ = from_.id
        if isinstance(to, Node):
            to = to.id
        id_ = '"{}" -> "{}"'.format(from_, to)
        super().__init__(id_, attrs)
