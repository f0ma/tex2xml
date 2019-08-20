TeX2XML
=======

TeX2XML is a Python library and tool to bidirectional convertion between LaTeX files and XML files.

This library allows to work with LaTeX files like with XML element tree.

Requirements
------------

* Python 3
* ``lxml``

Example
-------

Simple LaTeX document:

```
%example.tex file
\documentclass{article}
\usepackage{amsmath}

\begin{document}
Lorem ipsum dolor sit amet $\sin(X)$, consectetur adipiscing elit.
Quisque pulvinar mauris at nisl imperdiet, ac laoreet arcu ullamcorper.

\begin{math}
\frac{n!}{k!(n-k)!} = \binom{n}{k}
\end{math}

Etiam vel tellus quis diam imperdiet dictum et id augue.
Pellentesque habitant morbi tristique senectus et netus.

\end{document}
```

XML representation:

```
<tex>
  <comment>example.tex file</comment>
  <spaces>
</spaces>
  <tag name="documentclass">
    <arg>
      <text>article</text>
    </arg>
  </tag>
  <spaces>
</spaces>
  <tag name="usepackage">
    <arg>
      <text>amsmath</text>
    </arg>
  </tag>
  <tag name="par"/>
  <env name="document">
    <spaces>
</spaces>
    <text>Lorem ipsum dolor sit amet</text>
    <spaces> </spaces>
    <tag name="$">
      <tag name="sin"/>
      <text>(X)</text>
    </tag>
    <text>, consectetur adipiscing elit.</text>
    <spaces>
</spaces>
    <text>Quisque pulvinar mauris at nisl imperdiet, ac laoreet arcu ullamcorper.</text>
    <tag name="par"/>
    <env name="math">
      <spaces>
</spaces>
      <tag name="frac">
        <arg>
          <text>n!</text>
        </arg>
        <arg>
          <text>k!(n-k)!</text>
        </arg>
      </tag>
      <spaces> </spaces>
      <text>=</text>
      <spaces> </spaces>
      <tag name="binom"/>
      <group>
        <text>n</text>
      </group>
      <group>
        <text>k</text>
      </group>
      <spaces>
</spaces>
    </env>
    <tag name="par"/>
    <text>Etiam vel tellus quis diam imperdiet dictum et id augue.</text>
    <spaces>
</spaces>
    <text>Pellentesque habitant morbi tristique senectus et netus.</text>
    <tag name="par"/>
  </env>
  <spaces>
</spaces>
</tex>
```

TeX2XML has know ``frac`` tag and unknown ``binom`` tag. Some spaces wrapped in ``spaces`` tags for preserving original document space based formatting.

Library usage
-------------

```
from TeX2XML import TeX2XML, XML2TeX

xml = TeX2XML(infile).convert()
tex = XML2TeX(infile).convert()
```

Command line tool usage
-----------------------

```
usage: tex2xml.py [-h] [-x] [-t] [-i INPUT] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -x, --to-xml          Direction: XML from TeX (default)
  -t, --to-tex          Direction: TeX from XML
  -i INPUT, --input INPUT
                        Input file (default stdin)
  -o OUTPUT, --output OUTPUT
                        Output file (default stdout)
```

Known tags, shortcuts and verbatims
-----------------------------------

In TeX we can't determine count of tag argument, at example:

```
\macro{IsArg?}
```

can be interpret as the tag ``macro`` with the required argument ``IsArg?`` or as the tag ``macro`` and a separate group ``{IsArg?}``.

To solve this problem TeX2XML have a dicts of well known tags and arguments count:

```
from TeX2XML import TeXSyntax

s = TeXSyntax()

s.add_tag_args_count('documentclass', 1, 1) # for tag: first number - required arguments count,
                                            # second - optional arguments count
s.add_env_args_count('tabular', 1, 1) # also for enviroments

xml = TeX2XML(infile, syntax = s).convert()
```

In TeX we can use inline shortcuts like ``"=``, verbatim tags and enviroments.

To correct handling this structures TeX2XML uses shortcuts dicts and verbatim lists in TeXSyntax object:

```
s.add_shortcut('\\-', '\u00AD') # Soft hyphen shortcut
s.add_verb_tag('verb') # verbatim tag
s.add_verb_env('lstlisting') # verbatim enviroment
```

Default TeXSyntax object created with data from file ``knowntags.py``

Authors
-------

Stanislav D. Ivanov
