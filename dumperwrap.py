import re
import sublime
import sublime_plugin

LOG_TYPES = ['log', 'info', 'warn', 'error']

def get_indent(view, region):
    matches = re.findall(r'^(\s*)[^\s]', view.substr(region))
    indent_str = matches and len(matches) and matches[0] or ''
    indent_line = view.substr(find_next_line(view, region)).strip()
    need_indent = [True for i in ['{', '=', ':', '->', '=>'] if indent_line.endswith(i)]
    indent_line.lstrip('{}[]() \t')
    if need_indent:
        indent_str += len(indent_str) and indent_str[0] == '\t' and '\t' or '    '
    return indent_str

def find_next_line(view, region):
    while 0 < region.a and region.b < view.size() and view.classify(region.a) is sublime.CLASS_EMPTY_LINE:
        region = view.line(region.a - 1)
    return region

def get_wrapper(view, var_text, indent_str):
    # text_escaped = var_text.replace("'", "\\'")
    tmpl = "\n" + indent_str

    tmpl += "use Data::Dumper;"
    tmpl += "\n" + indent_str
    tmpl += "print Dumper (%s);" % (var_text)
    return tmpl

def strip_semicolon(text):
    if text[-1:] == ";":
        text = text[:-1]
    return text

class DumperwrapCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        selections = view.sel()

        for selection in selections:
            line_region = view.line(selection)

            if selection.empty():
                selected_text = sublime.get_clipboard()
            else:
                selected_text = view.substr(selection)

            strip_semicolon(selected_text)

            if len(selected_text) == 0:
                sublime.status_message('Nothing is selected or copied to clipbiard.')
            else:
                indent_str = get_indent(view, line_region)
                text = get_wrapper(view, selected_text, indent_str)
                view.insert(edit, line_region.end(), text)



class DumperremoveCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.get_selections()
        cursor = self.view.sel()[0]
        line_region = self.view.line(cursor)
        string = self.view.substr(line_region)
        newstring = re.sub(r"(?m)^((?!//|/\*).)*((use\ Data\:\:Dumper\;)|(print\ Dumper.*))", '', string)
        self.view.replace(edit, line_region, newstring)
        self.view.sel().clear()

    def get_selections(self):
        selections = self.view.sel()
        has_selections = False
        for sel in selections:
            if sel.empty() == False:
                has_selections = True
        if not has_selections:
            full_region = sublime.Region(0, self.view.size())
            selections.add(full_region)
        return selections
