#!/usr/bin/env python
import argparse
from uuid import uuid4
from rdflib import Graph, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import RDF, OWL

query_classes = prepareQuery("""
SELECT ?s {
  { ?s a owl:Class } UNION
  { ?s owl:subClassOf+ ?o . ?o a owl:Class . }
}
""", initNs={'owl': OWL})


class OntologyGraph:
    def __init__(self, files, format='ttl', verbose=False):
        self.g = Graph()
        self.verbose = verbose
        self._load_files(files, format)
        self.classes = set()
        self.instances = set()
        self.edges = set()
        self.literals = set()
        self._read_graph()

    def _load_files(self, files, format):
        if isinstance(files, str):
            files = [files]
        for file in files:
            self.g.load(file, format=format)

    def _read_graph(self):
        # for class_ in self.g.subjects(RDF.type, OWL.Class):
        for class_, in self.g.query(query_classes):
            self.classes.add(class_)
            self._add_predicate_object(class_, True)
            for instance in self.g.subjects(RDF.type, class_):
                self.instances.add(instance)
                self._add_predicate_object(instance)

    def _add_predicate_object(self, subject, is_class=False):
        for prop, obj in self.g.predicate_objects(subject):
            if isinstance(obj, Literal):
                literal_id = uuid4().hex
                self.literals.add((literal_id, obj))
                self.edges.add((subject, prop, literal_id))
            else:
                if is_class:
                    if not self.verbose and obj == OWL.Class:
                        continue
                    self.classes.add(obj)
                self.edges.add((subject, prop, obj))

    def convert(self):
        node_strings = []
        edge_strings = []
        for class_ in self.classes:
            node_strings.append('  "{}" [label="{}"{}]'.format(class_, self.compute_label(class_), node_color('#1f77b4')))
        for instance in self.instances:
            node_strings.append(
                '  "{}" [label="{}"{}]'.format(instance, self.compute_label(instance), node_color('#e377c2')))
        for uri, literal in self.literals:
            node_strings.append('  "{}" [label="{}" shape=rect{}]'.format(uri, literal, node_color('#ff7f0e')))
        for s, p, o in self.edges:
            edge_strings.append('  "{}" -> "{}" [label="{}"]'.format(s, o, self.compute_label(p)))
        return node_strings, edge_strings

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

    def compute_label(self, uri):
        prefix, _, name = self.g.compute_qname(uri)
        if prefix:
            return '{}:{}'.format(prefix, name)
        return name


def node_color(color):
    return ' fillcolor="{}" color="{}"'.format(color, color)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate dot for the input ontology files')
    parser.add_argument('files', nargs='+', help='Input ontology files.')
    parser.add_argument('-f', '--format', dest='format', default='ttl', help='Input file format.')
    parser.add_argument('-o', '--output', dest='out', default='ontology.dot',
                        help='Location of output dot file.')
    parser.add_argument('-V', '--verbose', dest='verbose', default=False, action='store_true',
                        help='Include obvious owl:Class node in the graph.')
    args = parser.parse_args()

    og = OntologyGraph(args.files, args.format, verbose=args.verbose)
    og.write_file(args.out)
