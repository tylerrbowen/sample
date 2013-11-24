import re
from and_sql_fragment import AndSqlFragment, OrSqlFragment
from container_sql_fragment import ContainerSqlFragment
from if_sql_fragment import IfSqlFragment
from include_sql_fragment import IncludeSqlFragment
from like_sql_fragment import LikeSqlFragment, PagingSqlFragment, OffsetFetchSqlFragment, WhereSqlFragment
from name_sql_fragment import NameSqlFragment
from text_sql_fragment import TextSqlFragment


class ParseIter:
    def __init__(self, iter_count):
        self._iter_count = iter_count

    def next(self):
        self._iter_count += 1

    def previous(self):
        self._iter_count -= 1

    def iter(self):
        return self._iter_count

class ElSqlParser:

    NAME_PATTERN = re.compile('[ ]*[@]NAME[(]([A-Za-z0-9_]+)[)][ ]*')
    AND_PATTERN = re.compile('[ ]*[@]AND[(]([:][A-Za-z0-9_]+)' + '([ ]?[=][ ]?[A-Za-z0-9_]+)?' + '[)][ ]*')
    OR_PATTERN = re.compile('[ ]*[@]OR[(]([:][A-Za-z0-9_]+)' + '([ ]?[=][ ]?[A-Za-z0-9_]+)?' + '[)][ ]*')
    IF_PATTERN = re.compile('[ ]*[@]IF[(]([:][A-Za-z0-9_]+)' + '([ ]?[=][ ]?[A-Za-z0-9_]+)?' + '[)][ ]*')
    INCLUDE_PATTERN = re.compile('[@]INCLUDE[(]([:]?[A-Za-z0-9_]+)[)](.*)')
    PAGING_PATTERN = re.compile('[@]PAGING[(][:]([A-Za-z0-9_]+)[ ]?[,][ ]?[:]([A-Za-z0-9_]+)[)](.*)')
    OFFSET_FETCH_PATTERN = re.compile('[@]OFFSETFETCH[(][:]([A-Za-z0-9_]+)[ ]?[,][ ]?[:]([A-Za-z0-9_]+)[)](.*)')
    FETCH_PATTERN = re.compile('[@]FETCH[(][:]([A-Za-z0-9_]+)[)](.*)')
    FETCH_ROWS_PATTERN = re.compile('[@]FETCH[(]([0-9]+)[)](.*)')
    VARIABLE_PATTERN = re.compile('([^:])*([:][A-Za-z0-9_]+)(.*)')
    
    def __init__(self,
                 lines):
        self._lines = []
        self._named_fragments = dict()
        for i, line in enumerate(lines):
            self._lines.append(Line(line, i + 1))

    def parse(self):
        self.reject_tabs()
        self.parse_named_sections()
        return self._named_fragments

    def reject_tabs(self):
        for line in self._lines:
            if line.contains_tab():
                raise TypeError('Tabs not permitted: ' + line.__str__())

    def parse_named_sections(self):
        container_fragment = ContainerSqlFragment()
        self.parse_container_section(container_fragment, self._lines, -1)

    def parse_container_section(self, container, line_iter, indent, parse_iter=None):
        remove_indices=[]
        r_count = 0
        if parse_iter is None:
            i = ParseIter(0)
        else:
            parse_iter.next()
            i = parse_iter
        len_lines = len(line_iter)
        while i.iter() < len_lines:
            try:
                line = line_iter[i.iter()]
            except IndexError:
                return
            if line.is_comment():
                line_iter.pop(i.iter())
                continue
            if line.indent() <= indent:
                i.previous()
                return
            trimmed = line.line_trimmed()
            if trimmed.startswith('@NAME'):
                name_matcher = self.NAME_PATTERN.match(trimmed)
                if name_matcher is None:
                    raise TypeError('@NAME with invalid format ' + line.__str__())
                name_fragment = NameSqlFragment(name_matcher.group(1))
                self.parse_container_section(name_fragment, line_iter, line.indent(), i)
                if len(name_fragment.get_fragments()) == 0:
                    raise TypeError('@NAME found with no indented lines: ' + line.__str__())
                container.add_fragment(name_fragment)
                self._named_fragments[name_fragment.get_name()] = name_fragment
            elif indent < 0:
                raise TypeError('Invalid fragment as root level, only @Name is permitted ' + line.__str__())
            elif trimmed.startswith('@PAGING'):
                paging_matcher = self.PAGING_PATTERN.match(trimmed)
                if paging_matcher is None:
                    raise TypeError('@PAGING with invalid format ' + line.__str__())
                where_fragment = PagingSqlFragment(paging_matcher.group(1), paging_matcher.group(2))
                self.parse_container_section(where_fragment, line_iter, line.indent(), i)
                if len(where_fragment.get_fragments()) == 0:
                    raise TypeError('@PAGING with no subsequent lines')
                container.add_fragment(where_fragment)
            elif trimmed.startswith('@WHERE'):
                if not trimmed.__eq__('@WHERE'):
                    raise TypeError('@WHERE with invalid format ' + line.__str__())
                where_fragment = WhereSqlFragment()
                self.parse_container_section(where_fragment, line_iter, line.indent(), i)
                if len(where_fragment.get_fragments()) == 0:
                    raise TypeError('@WHERE with no subsequent lines')
                container.add_fragment(where_fragment)
            elif trimmed.startswith('@AND'):
                and_matcher = self.AND_PATTERN.match(trimmed)
                if and_matcher is None:
                    raise TypeError('@AND with invalid format ' + line.__str__())
                and_fragment = AndSqlFragment(and_matcher.group(1), self.extract_variable(and_matcher.group(2)))
                self.parse_container_section(and_fragment, line_iter, line.indent(), i)
                if len(and_fragment.get_fragments()) == 0:
                    raise TypeError('@AND with no subsequent lines')
                container.add_fragment(and_fragment)
            elif trimmed.startswith('@OR'):
                or_matcher = self.OR_PATTERN.match(trimmed)
                if or_matcher is None:
                    raise TypeError('@OR with invalid format ' + line.__str__())
                or_fragment = OrSqlFragment(or_matcher.group(1), self.extract_variable(or_matcher.group(2)))
                self.parse_container_section(or_fragment, line_iter, line.indent(), i)
                if len(or_fragment.get_fragments()) == 0:
                    raise TypeError('@OR with no subsequent lines')
                container.add_fragment(or_fragment)
            elif trimmed.startswith('@IF'):
                if_matcher = self.IF_PATTERN.match(trimmed)
                if if_matcher is None:
                    raise TypeError('@IF with invalid format ' + line.__str__())
                if_fragment = IfSqlFragment(if_matcher.group(1), self.extract_variable(if_matcher.group(2)))
                self.parse_container_section(if_fragment, line_iter, line.indent(), i)
                if len(if_fragment.get_fragments()) == 0:
                    raise TypeError('@IF with no subsequent lines')
                container.add_fragment(if_fragment)
            else:
                self.parse_line(container, line)
            i.next()
            len_lines = len(line_iter)

    def extract_variable(self, text):
        if text is None:
            return None
        text = text.strip()
        if text.startswith('='):
            return self.extract_variable(text[1:])
        return text

    def parse_line(self, container, line):
        trimmed = line.line_trimmed()
        if len(trimmed) == 0:
            return
        if '@INCLUDE' in trimmed:
            self.parse_include_tag(container, line)
        elif '@LIKE' in trimmed:
            self.parse_like_tag(container, line)
        elif '@OFFSETFETCH' in trimmed:
            self.parse_offset_fetch_tag(container, line)
        elif '@FETCH' in trimmed:
            self.parse_fetch_tag(container, line)
        elif trimmed.startswith('@'):
            raise TypeError('Unknown Tag: ' + line.__str__())
        else:
            text_fragment = TextSqlFragment(trimmed)
            container.add_fragment(text_fragment)

    def parse_include_tag(self, container, line):
        trimmed = line.line_trimmed()
        pos = trimmed.index('@INCLUDE')
        text_fragment = TextSqlFragment(trimmed[0:pos])

        include_matcher = self.INCLUDE_PATTERN.match(trimmed[pos:])
        if include_matcher is None:
            raise TypeError('@Include ' + line.__str__())
        include_fragment = IncludeSqlFragment(include_matcher.group(1))
        remainder = include_matcher.group(2)
        container.add_fragment(text_fragment)
        container.add_fragment(include_fragment)

        sub_line = Line(remainder, line.line_number())
        self.parse_line(container, sub_line)

    def parse_like_tag(self, container, line):
        trimmed = line.line_trimmed()
        pos = trimmed.index('@LIKE')
        text_fragment = TextSqlFragment(trimmed[0:pos])
        trimmed = trimmed[pos+5:]
        content = trimmed
        try:
            end = trimmed.index('@ENDLIKE')
        except ValueError:
            end = -1
        remainder = ''
        if end  >= 0:
            content = trimmed[:end]
            remainder = trimmed[end+8:]
        content_fragment = TextSqlFragment(content)

        matcher = self.VARIABLE_PATTERN.match(content)
        if matcher is None:
            raise TypeError('@LIKE ' + line.__str__())
        like_fragment = LikeSqlFragment(matcher.group(2))
        container.add_fragment(text_fragment)
        container.add_fragment(like_fragment)
        like_fragment.add_fragment(content_fragment)
        #container.add_fragment(content_fragment)
        sub_line = Line(remainder, line.line_number())
        self.parse_line(container, sub_line)

    def parse_offset_fetch_tag(self, container, line):
        trimmed = line.line_trimmed()
        pos = trimmed.index('@OFFSETFETCH')
        text_fragment = TextSqlFragment(trimmed[0:pos])
        offset_variable = 'paging_offset'
        fetch_variable = 'paging_fetch'
        remainder = trimmed[pos + 12:]
        if trimmed[:pos].startswith('@OFFSETFETCH('):
            matcher = self.OFFSET_FETCH_PATTERN.match(trimmed[:pos])
            if matcher is None:
                raise TypeError
            offset_variable = matcher.group(1)
            fetch_variable = matcher.group(2)
            remainder = matcher.group(3)
        paging_fragment = OffsetFetchSqlFragment(offset_variable, fetch_variable)
        container.add_fragment(text_fragment)
        container.add_fragment(paging_fragment)
        sub_line = Line(remainder, line.line_number())
        self.parse_line(container, sub_line)

    def parse_fetch_tag(self, container, line):
        trimmed = line.line_trimmed()
        pos = trimmed.index('@FETCH')
        text_fragment = TextSqlFragment(trimmed[0:pos])
        fetch_variable = 'paging_fetch'
        remainder = trimmed[pos + 6:]
        if trimmed[:pos].startswith('@FETCH('):
            matcher = self.FETCH_PATTERN.match(trimmed[:pos])
            matcher_rows = self.FETCH_ROWS_PATTERN.match(trimmed[:pos])
            if matcher is not None:
                fetch_variable = matcher.group(1)
                remainder = matcher.group(2)
            elif matcher_rows is not None:
                fetch_variable = matcher_rows.group(1)
                remainder = matcher_rows.group(2)
            else:
                raise TypeError('Fetch f up')
        paging_fragment = OffsetFetchSqlFragment(fetch_variable)
        container.add_fragment(text_fragment)
        container.add_fragment(paging_fragment)
        sub_line = Line(remainder, line.line_number())
        self.parse_line(container, sub_line)


class Line(object):

    def __init__(self, line, line_number):
        self._line = line
        self._trimmed = line.strip()
        self._line_number = line_number

    def line(self):
        return self._line

    def line_trimmed(self):
        return self._trimmed

    def line_number(self):
        return self._line_number

    def contains_tab(self):
        return '\t' in self._line

    def is_comment(self):
        return self._trimmed.startswith('--') or len(self._trimmed) == 0

    def indent(self):
        for i in range(len(self._line)):
            if self._line[i] != ' ':
                return i
        return len(self._line)

    def __str__(self):
        return 'Line ' + self._line_number.__str__()

