"""
Copied from Sphinx plugins for Django documentation.-----------------------------------------------
"""

from importlib import import_module
from inspect import getsource

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes
from sphinx.domains.std import Cmdoption
from sphinx.util.nodes import set_source_info


def setup(app):
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )
    app.add_crossref_type(
        directivename="templatetag",
        rolename="ttag",
        indextemplate="pair: %s; template tag"
    )
    app.add_crossref_type(
        directivename="templatefilter",
        rolename="tfilter",
        indextemplate="pair: %s; template filter"
    )
    app.add_crossref_type(
        directivename="fieldlookup",
        rolename="lookup",
        indextemplate="pair: %s; field lookup type",
    )
    app.add_directive('django-admin-option', Cmdoption)
    app.add_config_value('django_next_version', '0.0', True)

    # register the snippet directive
    app.add_directive('snippet', SnippetWithFilename)
    # register a node for snippet directive so that the xml parser
    # knows how to handle the enter/exit parsing event
    app.add_node(snippet_with_filename,
                 html=(visit_snippet, depart_snippet_literal),
                 man=(visit_snippet_literal, depart_snippet_literal),
                 text=(visit_snippet_literal, depart_snippet_literal),
                 texinfo=(visit_snippet_literal, depart_snippet_literal))

    app.add_directive('pprint', PrettyPrintIterable)

    return {'parallel_read_safe': True}


class snippet_with_filename(nodes.literal_block):
    """
    Subclass the literal_block to override the visit/depart event handlers
    """
    pass


def visit_snippet_literal(self, node):
    """
    default literal block handler
    """
    self.visit_literal_block(node)


def depart_snippet_literal(self, node):
    """
    default literal block handler
    """
    self.depart_literal_block(node)


def visit_snippet(self, node):
    """
    HTML document generator visit handler
    """
    lang = node["language"]
    linenos = node.get('linenos', False)
    fname = node['filename']
    highlight_args = node.get('highlight_args', {})
    if 'language' in node:
        # code-block directives
        lang = node['language']
        highlight_args['force'] = True
    if 'linenos' in node:
        linenos = node['linenos']

    def warner(msg):
        self.builder.warn(msg, (self.builder.current_docname, node.line))

    highlighted = self.highlighter.highlight_block(node.rawsource, lang,
                                                   warn=warner,
                                                   linenos=linenos,
                                                   **highlight_args)
    starttag = self.starttag(node, 'div', suffix='',
                             CLASS='highlight-%s snippet' % lang)
    self.body.append(starttag)
    self.body.append('<div class="snippet-filename">%s</div>\n''' % (fname,))
    self.body.append(highlighted)
    self.body.append('</div>\n')
    raise nodes.SkipNode


class SnippetWithFilename(Directive):
    """
    The 'snippet' directive that allows to add the filename (optional)
    of a code snippet in the document. This is modeled after CodeBlock.
    """
    has_content = True
    optional_arguments = 1
    option_spec = {'filename': directives.unchanged_required}

    def run(self):
        code = '\n'.join(self.content)

        literal = snippet_with_filename(code, code)
        if self.arguments:
            literal['language'] = self.arguments[0]
        literal['filename'] = self.options['filename']
        set_source_info(self, literal)
        return [literal]


def parse_django_admin_node(env, sig, signode):
    command = sig.split(' ')[0]
    env.ref_context['std:program'] = command
    title = "django-admin %s" % sig
    signode += addnodes.desc_name(title, title)
    return command


#----------------Human readable iterables in Sphinx documentation--------
# https://stackoverflow.com/a/62253904/3437454

class PrettyPrintIterable(Directive):
    required_arguments = 1

    def run(self):
        def _get_iter_source(src, varname):
            # 1. identifies target iterable by variable name, (cannot be spaced)
            # 2. determines iter source code start & end by tracking brackets
            # 3. returns source code between found start & end
            start = end = None
            open_brackets = closed_brackets = 0
            for i, line in enumerate(src):
                if line.startswith(varname):
                    if start is None:
                        start = i
                if start is not None:
                    open_brackets   += sum(line.count(b) for b in "([{")
                    closed_brackets += sum(line.count(b) for b in ")]}")

                if open_brackets > 0 and (open_brackets - closed_brackets == 0):
                    end = i + 1
                    break
            return '\n'.join(src[start:end])

        module_path, member_name = self.arguments[0].rsplit('.', 1)
        src = getsource(import_module(module_path)).split('\n')
        code = _get_iter_source(src, member_name)

        literal = nodes.literal_block(code, code)
        literal['language'] = 'python'

        return [addnodes.desc_content('', literal)]
