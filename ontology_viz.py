#!/usr/bin/env python
import argparse
from uuid import uuid4
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import RDF, RDFS, SKOS, XSD, DOAP, FOAF, OWL, split_uri, Namespace
from collections import namedtuple

query_classes = prepareQuery("""
SELECT ?s {
  { ?s a owl:Class } UNION
  { ?s owl:subClassOf+ ?o . ?o a owl:Class . }
} """, initNs={'owl': OWL})
query_properties = prepareQuery("""
SELECT ?s {
  { ?s a ?property } UNION { ?s owl:subPropertyOf+ ?o . ?o a ?property }
  FILTER ( ?property IN ( owl:DatatypeProperty, owl:ObjectProperty ) )
} """, initNs={'owl': OWL})
colors = namedtuple('Colors', ['cls', 'lit', 'ins'])('#1f77b4', '#ff7f0e', '#e377c2')
SCHEMA = Namespace('http://schema.org/')
common_ns = set(map(lambda ns: ns.uri, (RDF, RDFS, SKOS, SCHEMA, XSD, DOAP, FOAF)))


class OntologyGraph:
    def __init__(self, files, format='ttl', ontology=None):
        self.g = Graph()
        if ontology is not None:
            g = Graph()
            self._load_files(g, ontology)
            self.ontology_defined = True
            self.ontology_cls = {cls for cls, in g.query(query_classes)}
            self.ontology_pty = {pty for pty, in g.query(query_properties)}
        else:
            self.ontology_defined = False
        self._load_files(self.g, files, format)
        self.classes = set()
        self.instances = set()
        self.edges = set()
        self.literals = set()
        self._read_graph()

    @staticmethod
    def _load_files(graph, files, format='ttl'):
        if isinstance(files, str):
            files = [files]
        for file in files:
            graph.load(file, format=format)

    def _read_graph(self):
        for s, p, o in self.g:
            if p == RDF.type:
                if o == OWL.Class:
                    self.add_to_classes(s)
                else:
                    self.add_to_classes(o)
                    self.instances.add(s)
                    self.add_edge((s, p, o))
            elif isinstance(o, Literal):
                literal_id = uuid4().hex
                self.literals.add((literal_id, o))
                self.add_edge((s, p, literal_id))
            else:
                self.add_edge((s, p, o))

    def add_to_classes(self, cls):
        if self.ontology_defined:
            if cls not in self.classes and cls not in self.ontology_cls:
                print("[WARNING] Class {} doesn't exist in the ontology!".format(cls))
                self.ontology_cls.add(cls)  # Only bark once
        self.classes.add(cls)

    def add_edge(self, triple):
        if self.ontology_defined:
            _, p, _ = triple
            if p not in self.ontology_pty:
                prefix, _ = split_uri(p)
                if URIRef(prefix) not in common_ns:
                    print("[WARNING] Property {} doesn't exist in the ontology!".format(p))
                    self.ontology_pty.add(p)  # Only bark once
        self.edges.add(triple)

    def convert(self):
        node_strings = []
        edge_strings = []
        for class_ in self.classes:
            node_strings.append(self._dot_class_node(class_))
        for instance in self.instances:
            node_strings.append(self._dot_instance_node(instance))
        for uri, literal in self.literals:
            node_strings.append('  "{}" [label="{}" shape=rect{}]'.format(uri, text_justify(literal, 20), node_color(colors.lit)))
        for s, p, o in self.edges:
            edge_strings.append('  "{}" -> "{}" [label="{}"]'.format(s, o, self._pred_label(p)))
        return node_strings, edge_strings

    def _dot_class_node(self, class_):
        color = node_color(colors.cls)
        if isinstance(class_, BNode):
            return '  "{}" [label=""{} shape=circle]'.format(class_, color)
        return '  "{}" [label="{}"{}]'.format(class_, self.compute_label(class_), color)

    def _dot_instance_node(self, instance):
        color = node_color(colors.ins)
        if isinstance(instance, BNode):
            return '  "{}" [label=""{} shape=circle]'.format(instance, color)
        return '  "{}" [label="{}"{}]'.format(instance, self.compute_label(instance), color)

    @classmethod
    def generate_dotstring(cls, node_strings, edge_strings):
        dot = [
            'digraph G {',
            '  rankdir=BT'
            '  node[style="filled" height=.3]',
        ]
        dot.extend(node_strings)
        dot.extend(edge_strings)
        dot.append('}')
        return '\n'.join(dot)

    def generate(self):
        nodes, edges = self.convert()
        dot = self.generate_dotstring(nodes, edges)
        return dot

    def write_file(self, file):
        dot = self.generate()
        with open(file, 'w') as f:
            f.write(dot)

    pred_map = { RDF.type: 'a' }

    def _pred_label(self, uri):
        return self.pred_map.get(uri, self.compute_label(uri, 0))

    def compute_label(self, uri, length=20):
        prefix, _, name = self.g.compute_qname(uri)
        label = '{}:{}'.format(prefix, name) if prefix else name
        if length and len(label) > length:
            label = label[:length-3] + '...'
        return label


def node_color(color):
    return ' fillcolor="{}" color="{}"'.format(color, color)


def text_justify(words, max_width):
    words.replace('"', '\"')
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
    words = res + [' '.join(cur).center(max_)]
    return '\\n'.join(words)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate dot for the input ontology files')
    parser.add_argument('files', nargs='+', help='Input ontology files.')
    parser.add_argument('-f', '--format', dest='format', default='ttl', help='Input file format.')
    parser.add_argument('-o', '--output', dest='out', default='ontology.dot',
                        help='Location of output dot file.')
    parser.add_argument('-O', '--ontology', dest='ontology', default=None,
                        help='Provided ontology for the graph.')
    args = parser.parse_args()

    og = OntologyGraph(args.files, args.format, ontology=args.ontology)
    og.write_file(args.out)
