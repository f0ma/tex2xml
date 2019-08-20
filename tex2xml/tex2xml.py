#!/usr/bin/env python3

import sys
import argparse
from lxml import etree
import .knowntags
from copy import deepcopy

class TeXSyntax:
    def __init__(self):
        self.args_count = deepcopy(knowntags.args_count)
        self.env_opts = deepcopy(knowntags.env_opts)
        self.shortcuts = deepcopy(knowntags.shortcuts)
        self.verb_tags = deepcopy(knowntags.verb_tags)
        self.verb_envs = deepcopy(knowntags.verb_envs)

    def add_tag_args_count(tag, args, opts):
        self.args_count[tag] = (args, opts)

    def add_env_args_count(env, args, opts):
        self.env_opts[env] = (args, opts)

    def add_shortcut(tex, symbol):
        self.shortcuts.append((tex, symbol))

    def add_verb_tag(tag):
        self.verb_tags.append(tag)

    def add_verb_env(env):
        self.verb_envs.append(env)

class TeX2XML:
    def __init__(self, texstream, syntax = None):
        self.source = texstream.read()
        self.i = 0
        self.root = etree.Element("tex")
        self.node = self.root
        self.textbuffer = ''

        if syntax is None:
            self.syntax = TeXSyntax()
        else:
            assert type(syntax) == TeXSyntax
            self.syntax = syntax

    def current(self):
        return self.source[self.i]

    def next(self):
        if self.i+1 < len(self.source):
            return self.source[self.i+1]
        else:
            return None

    def next_nonspace(self, index = False):
        j = self.i
        while True:
            if j < len(self.source):
                if not self.source[j].isspace():
                    if index:
                        return j
                    else:
                        return self.source[j]
                j += 1
            else:
                return None

    def drain(self):
        self.textbuffer += self.current()
        self.step()

    def flush(self):
        if self.textbuffer != '':
            if self.textbuffer.strip() == '':
                el = etree.SubElement(self.node, "spaces")
                el.text = self.textbuffer
            else:
                spaces_before_index = 0
                spaces_after_index = 0
                for i in range(0, len(self.textbuffer)):
                    if self.textbuffer[i].isspace():
                        spaces_before_index+=1
                    else:
                        break

                for i in range(len(self.textbuffer)-1,-1,-1):
                    if self.textbuffer[i].isspace():
                        spaces_after_index+=1
                    else:
                        break

                if spaces_before_index > 0:
                    el = etree.SubElement(self.node, "spaces")
                    el.text = self.textbuffer[:spaces_before_index]

                el = etree.SubElement(self.node, "text")
                el.text = self.textbuffer[spaces_before_index:len(self.textbuffer)-spaces_after_index]

                if spaces_after_index > 0:
                    el = etree.SubElement(self.node, "spaces")
                    el.text = self.textbuffer[len(self.textbuffer)-spaces_after_index:]

            self.textbuffer = ''

    def step(self, n=1):
        self.i += n

    def move (self, n):
        self.i = n

    def next_text_is(self, txt):
        return self.source[self.i:self.i+len(txt)] == txt

    def convert(self):
        try:
            self._parse()
        except Exception as e:
            print("Parsing error", file=sys.stderr)
            print(e, file=sys.stderr)
            print(self.source[self.i-10:self.i+10], file = sys.stderr)
            print('          ^', file = sys.stderr)
        return self.root

    def _parse(self):
        while self.i < len(self.source):

            # EOF
            if self.current() == None:
                break

            if self.current() == '\n' and self.next() == '\n':
                self.flush()
                el = etree.SubElement(self.node, "tag")
                el.attrib['name'] = 'par'
                self.step(2)
                continue

            if self.current() == '\n':
                self.drain()
                self.flush()
                continue

            # Comment
            if self.current() == '%':
                comment_start = self.i
                while self.current() not in [None, '\n']:
                    self.step()
                comment_end = self.i
                self.step()
                el = etree.SubElement(self.node, "comment")
                el.text = self.source[comment_start+1:comment_end]

                el = etree.SubElement(self.node, "spaces")
                el.text = '\n'
                continue

            # Escaping
            if self.current() == '\\' and self.next() in '#$%^&_{}~\\':
                self.step()
                self.drain()
                continue

            for sc, rep in self.syntax.shortcuts:
                if self.next_text_is(sc):
                    self.textbuffer += rep
                    self.step(len(sc))
                    continue

            # Control seq
            if self.current() == '\\' and self.next() != None and self.next().isalpha():
                self.flush()
                self.step()
                control_start = self.i
                while self.current().isalpha():
                    self.step()
                control_end = self.i

                tag_name = self.source[control_start:control_end]

                el = etree.SubElement(self.node, "tag")
                el.attrib['name'] = tag_name
                el.attrib['args_await'] = str(0)
                el.attrib['opts_await'] = str(0)

                if el.attrib['name'] in self.syntax.args_count:
                    arg_no, opt_arg = self.syntax.args_count[el.attrib['name']]

                    if opt_arg > 0 and self.next_nonspace() != '[':
                        opt_arg = 0
                    if arg_no == 1 and self.next_nonspace() != '{' and opt_arg == 0:
                        symb = self.next_nonspace()
                        symb_index = self.next_nonspace(True)

                        spaces_before = self.source[self.i:symb_index]

                        if spaces_before != '':
                            sel = etree.SubElement(el, "space")
                            sel.text = spaces_before

                        el.attrib['arg'] = symb

                        self.move(symb_index+1)
                        arg_no = 0

                    el.attrib['args_await'] = str(arg_no)
                    el.attrib['opts_await'] = str(opt_arg)

                    if arg_no > 0 or opt_arg > 0:
                        self.node = el
                    if el.attrib['name'] in self.syntax.verb_tags:
                        delimiter = el.attrib['arg']
                        data = ''
                        while self.current() != delimiter and self.current() is not None:
                            data += self.current()
                            self.step()
                        self.step()
                        vel = etree.SubElement(el, "verb")
                        vel.text = data

                continue

            # Special control seq
            if self.current() in '$_^':
                self.flush()
                if self.current() == '$' and self.node.tag == 'tag' and self.node.attrib['name'] in ['$','$$']:
                    self.step()
                    if self.current() == '$':
                        self.step()
                    self.node = self.node.getparent()
                    continue
                el = etree.SubElement(self.node, "tag")
                if self.current() in '_^':
                    el.attrib['name'] = self.current()
                    el.attrib['args_await'] = str(1)
                    el.attrib['opts_await'] = str(0)

                    self.step()

                    if self.next_nonspace() != '{':
                        symb = self.next_nonspace()
                        symb_index = self.next_nonspace(True)

                        spaces_before = self.source[self.i:symb_index]

                        if spaces_before != '':
                            sel = etree.SubElement(el, "space")
                            sel.text = spaces_before

                        ael = etree.SubElement(el, "arg")
                        ael.text = symb

                        self.move(symb_index+1)
                        el.attrib['args_await'] = str(0)
                        continue

                elif self.current() == '$':
                    el.attrib['name'] = '$'
                    el.attrib['args_await'] = str(0)
                    el.attrib['opts_await'] = str(0)
                    if self.next() == '$':
                        el.attrib['name'] = '$$'
                        self.step()
                    self.step()

                self.node = el
                continue

            # Group
            if self.current() == '{':
                self.flush()
                if (self.node.tag == 'tag' or self.node.tag == 'env') and int(self.node.attrib['args_await']) > 0:
                    tag = 'arg'
                else:
                    tag = 'group'
                el = etree.SubElement(self.node, tag)
                self.node = el
                self.step()
                continue

            if self.current() == '}':
                self.flush()
                self.node = self.node.getparent()
                if self.node.tag == 'tag':
                    tag_name = self.node.attrib['name']
                    if int(self.node.attrib['args_await']) > 0:
                        self.node.attrib['args_await'] = str(int(self.node.attrib['args_await']) - 1)
                        if int(self.node.attrib['args_await']) == 0:
                            self.node = self.node.getparent()
                    if tag_name == 'begin':
                        el = etree.SubElement(self.node, 'env')
                        el.attrib['name'] = self.node[-2][-1][-1].text
                        del self.node[-2]
                        self.node = el

                        self.node.attrib['args_await'] = str(0)
                        self.node.attrib['opts_await'] = str(0)
                        if el.attrib['name'] in self.syntax.env_opts:
                            nargs, nopts = self.syntax.env_opts[el.attrib['name']]
                            self.node.attrib['args_await'] = str(nargs)
                            self.node.attrib['opts_await'] = str(nopts)

                        if el.attrib['name'] in self.syntax.verb_envs:
                           self.step()
                           delimiter = '\\end{'+el.attrib['name']+'}'
                           start_verb = self.i
                           end_verb = self.source.find(delimiter, self.i)
                           data = self.source[start_verb:end_verb]
                           self.step(len(data)+len(delimiter)-1)
                           vel = etree.SubElement(el, "verb")
                           vel.text = data
                           #self.step()
                           self.node = self.node.getparent()

                    if tag_name == 'end':
                        del self.node[-1]
                        self.node = self.node.getparent()
                self.step()
                continue

            #Optgroup
            if self.current() == '[' and (self.node.tag == 'tag' or self.node.tag == 'env') and int(self.node.attrib['opts_await']) > 0:
                self.flush()
                el = etree.SubElement(self.node, 'opt')
                self.node = el
                self.step()
                continue

            if self.current() == ']' and self.node.tag == 'opt':
                self.flush()
                self.node = self.node.getparent()
                self.node.attrib['opts_await'] = '0'
                self.step()
                continue

            self.drain()

        for element in self.root.iter():
            if 'args_await' in element.attrib:
                del element.attrib['args_await']
            if 'opts_await' in element.attrib:
                del element.attrib['opts_await']
def escape(s):
    ss = ''
    for sym in s:
        replaced = False

        if sym in '#$%^&_{}~\\':
            ss += '\\'+sym
            replaced = True

        for sc, rep in self.syntax.shortcuts:
            if sym == rep:
                ss += sc
                replaced = True
                break

        if not replaced:
            ss += sym

    return ss

class XML2TeX:
    def __init__(self, file, syntax = None):
        self.file = file

        if syntax is None:
            self.syntax = TeXSyntax()
        else:
            assert type(syntax) == TeXSyntax
            self.syntax = syntax

    def convert(self):
        self.tree = etree.parse(self.file)
        self.tex = []
        self.make_tex(self.tree.getroot())
        return ''.join(self.tex)

    def write_tex(self, element):
        tail = ''

        if element.tag == 'tex':
            pass
        elif element.tag == 'comment':
            self.tex.append('%'+element.text)
        elif element.tag == 'text':
            self.tex.append(escape(element.text))
        elif element.tag == 'spaces':
            self.tex.append(escape(element.text))
        elif element.tag == 'verb':
            self.tex.append(element.text)
        elif element.tag == 'tag':
            if element.attrib['name'] in ['$','$$','^','_']:
                if element.attrib['name'] in ['$','$$']:
                    tail = element.attrib['name']+tail
            elif element.attrib['name'] == 'par':
                self.tex.append('\n\n')
            elif 'arg' in element.attrib:
                self.tex.append('\\'+element.attrib['name']+element.attrib['arg'])
                if element.attrib['name'] in ['verb']:
                    tail = element.attrib['arg']+tail
            else:
                tex.append('\\'+element.attrib['name'])
        elif element.tag == 'group':
            self.tex.append('{')
            tail = '}'+tail
        elif element.tag == 'arg':
            if len(element) > 0:
                self.tex.append('}')
                tail = '}'+tail
            else:
                self.tex.append(element.text)
                last_verb = element.text
        elif element.tag == 'opt':
            self.tex.append('[')
            tail = ']'+tail
        elif element.tag == 'env':
            self.tex.append('\\begin{'+element.attrib['name']+'}')
            tail = '\\end{'+element.attrib['name']+'}'+tail

        for child in element:
            self.write_tex(child)

        self.tex.append(tail)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Bidirectional XML <-> TeX converter")

    parser.add_argument("-x", "--to-xml", action="store_true", default=False,
                        help="Direction: XML from TeX (default)")

    parser.add_argument("-t", "--to-tex", action="store_true", default=False,
                        help="Direction: TeX from XML")

    parser.add_argument("-i", "--input", action="store", default=None,
                        help="Input file (default stdin)")

    parser.add_argument("-o", "--output", action="store", default=None,
                        help="Output file (default stdout)")

    args = parser.parse_args()

    if args.to_xml or (args.to_xml == False and args.to_tex == False):
        infile = open(args.input) if args.input != None else sys.stdin
        xml = TeX2XML(infile).convert()
        outfile = open(args.output, 'w') if args.output != None else sys.stdout
        print(etree.tostring(xml, pretty_print=True, encoding="UTF-8").decode('utf8'), file = outfile)
    if args.to_tex:
        infile = open(args.input) if args.input != None else sys.stdin
        tex = XML2TeX(infile).convert()
        outfile = open(args.output, 'w') if args.output != None else sys.stdout
        print(tex, file = outfile)

