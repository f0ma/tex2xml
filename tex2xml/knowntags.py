
args_count = {'documentclass':(1, 1),
              'usepackage':(1, 1),
              'begin':(1, 0),
              'end':(1, 0),
              'emph':(1, 0),
              'left':(1, 0),
              'right':(1, 0),
              'verb':(1, 0),
              'frac':(2, 0)}

env_opts = {'figure': (0, 1),
            'array': (1, 1),
            'tabular': (1, 1)}

shortcuts = [('\\-', '\u00AD'),
             ('---', '\u2014'),
             ('~', '\u00A0'),
             ('"=', '\u2010')]

verb_tags = ['verb']
verb_envs = ['verbatim', 'lstlisting'] 
