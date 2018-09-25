#+TITLE: Ontology Visualization

* Example
#+BEGIN_SRC bash
  ./ontology_viz.py -o test.dot test.ttl -O ontology.ttl
  dot -Tpng -o test.png test.dot
#+END_SRC

- Use ~-o~ to indicate the path of output file
- Use ~-O~ to indicate the input ontology (Optional).
- Use ~-C~ to indicate the configuration file (Optional).
  - ~max_label_length~: config the max length of labels. If the text exceeds the length, exceeded part will be replaced with "...". Default value is ~0~.
  - ~blacklist~: config the predicate that you don't want to see in the graph.
  - ~class_inference_in_object~: config the predicate that can inference the object is a ~Class~, even if the class doesn't defined in the ontology.
  - ~label_property~: config the predicate that used for labeling nodes, if such a label exists, it will display inside the node.
  - ~tooltip_property~: config the predicate that contains the tooltip texts.
  - ~bnode_regex~: a list of regexes, if an uri matches, then it will be dispaly as a blank node without its uri nor label. It can be useful if you have a lot of reifications.
  - ~colors~: config the colors of nodes
    - ~class~, ~literal~, ~instance~ can accept HEX value(e.g. ~"#ff0000"~ ), MATLAB style(e.g. ~"r"~ ), and color name (e.g. ~"red"~ ).
    #+BEGIN_SRC json
      "colors": {
        "class": "#ff0000",
        "literal": "r",
        "instance": "red",
      }
    #+END_SRC
    - ~instance~ can also accept a dict value to specify the color of each class instance. And use ~"default"~ to to set color for undefined instances.
    #+BEGIN_SRC json
      "instance": {
        "https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Facility": "#a6cee3",
        "default": "#ffff99"
      }
    #+END_SRC

    - ~filled~: config whether fill the node, default value: ~true~.
- Classes defined in the ontology will be omitted in the output graph. This action can be switched with argument ~-V~.

** Useful Graphviz flags

- ~-K~ to specify which [[https://graphviz.gitlab.io/_pages/pdf/dot.1.pdf][layout algorithm]] to use. E.g. ~-Kneato~ and ~-Ksfdp~ . Notice that inorder to use ~sfdp~ layout algorithm, you will need to build your graphviz with [[http://gts.sourceforge.net][GTS]].
- ~-T~ to specify the [[https://graphviz.gitlab.io/_pages/doc/info/output.html][output format]].
- ~-G~ to set a [[https://graphviz.gitlab.io/_pages/doc/info/attrs.html][graph attribute]]. E.g. ~-Goverlap=prism~

* Requirements
In order to use this tool, you'll need to make sure you have [[https://github.com/RDFLib/rdflib][rdflib]] installed.

In order to convert =dot= into =png= or =svg= image, you will need [[https://www.graphviz.org][Graphviz]].
