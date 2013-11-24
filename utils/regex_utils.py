
import re

class RegexUtils:

    @classmethod
    def wild_cards_to_pattern(cls, text):
        tkn = text.split('?*')
        buf = ''
        buf += '^'
        last_star = False
        for tk in tkn:
            st = tk
            if st == '?':
                buf += '.'
                last_star = False
            elif st == '*':
                if last_star:
                    buf += '.*'
                last_star = True
            else:
                buf += st
                last_star = False
        buf += '$'
        return re.compile(buf, re.IGNORECASE)

    @classmethod
    def wild_card_match(cls, search_criteria_with_wildcard, text_to_match_against):
        if search_criteria_with_wildcard is None or text_to_match_against is None:
            return False
        return cls.wild_cards_to_pattern(search_criteria_with_wildcard).match(text_to_match_against) is not None


    @classmethod
    def extract(cls, string, regex=None, pattern=None, group=None):
        if regex is None and pattern is None:
            raise TypeError('either regex or pattern must be supplied')
        if group is None:
            group = 1
        if pattern is None:
            pattern = re.compile(regex)
        m = pattern.match(string)
        if m is not None:
            return m.group(group)
        return None

    @classmethod
    def matches(cls, input_, pattern):
        m = pattern.match(input_)
        return m is not None


