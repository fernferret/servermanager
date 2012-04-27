#!/usr/bin/env python
import tokenize
import pprint

class ParseError(Exception):
    pass

#class AdConfig(SMConfig):
#    '''
#    {'Advertisements': 
#        {'1': 
#            {'text': 'Welcome to The Melons of Mass Distraction!', 'type': 'S'}
#        }, 
#        '3': {'text': 'W]M[D FestiveFerret is bad.', 'type': 'H'}, 
#        '2': {'text': 'Next map is {SM_NEXTMAP} in {TIMELEFT} minutes.', 'type': 'S'}, 
#        '5': {'text': 'Visit us at www.wmdgaming.com and www.ubermelons.com!', 'type': 'S'}, 
#        '4': {'text': '{GREEN}Current {LIGHTGREEN}Map: {DEFAULT}{CURRENTMAP}', 'type': 'S'}, 
#        '6': {'text': 'Shoutcasting {GREEN}TODAY {TEAM}@{LIGHTGREEN} 8pm EST {DEFAULT}with {TEAM}[UM] Drunken Wolf{DEFAULT}!', 'type': 'S'}
#    }
#    '''
#    def get_ads(self):
#        ad_dict = self.load()        

class SMConfig(object):
    def __init__(self, filename):
        self._in_comment = False
        self.filename = filename
        self.cfg = self.load()
    
    def save(self, filename=None):
        if filename:
            self.filename = filename
        my_file = open(self.filename, "r+")
        f.seek(0)
        f.write(self._get_as_text(self.cfg))
        my_file.close()
    
    def load(self, filename=None):
        if filename:
            self.filename = filename
        my_file = open(self.filename)
        tokens = tokenize.generate_tokens(my_file.readline)
        final_dict = {}
        try:
            self._parse_node(tokens, final_dict)
        except StopIteration:
            pass
        my_file.close()
        return final_dict

    def text(self):
        return SMConfig._get_as_text(self.cfg)

    @staticmethod
    def _get_as_text(my_dict, space_lvl=0):
        spaces = "    " * space_lvl
        return_arr = []
        for key, value in my_dict.items():
            if isinstance(value, dict):
                return_arr.append('%s"%s"\n%s{\n%s\n%s}\n' % \
                    (spaces, key, spaces, 
                        SMConfig._get_as_text(value, space_lvl + 1), spaces))
            else:
                return_arr.append('%s"%s" "%s"\n' % (spaces, key, value))
        return ''.join(return_arr)
    
    def _parse_node(self, tokens, my_dict, prev_name=None):
        next = tokens.next()
        if self._in_comment:
            if tokenize.tok_name[next[0]] == "NEWLINE" or tokenize.tok_name[next[0]] == "NL":
                self._in_comment = False
            return self._parse_node(tokens, my_dict, prev_name)
        if my_dict == None:
            my_dict = {}
        if tokenize.tok_name[next[0]] == "STRING":
            if prev_name:
                my_dict[prev_name] = next[1].strip('"')
                self._parse_node(tokens, my_dict)
                return my_dict
            return self._parse_node(tokens, my_dict, next[1].strip('"'))
        elif tokenize.tok_name[next[0]] == "OP":
            if next[1] == "{":
                if not prev_name == None:
                    my_dict[prev_name] = self._parse_node(tokens, None, None)
                    return self._parse_node(tokens, my_dict, None)
                self._parse_node(tokens, my_dict, prev_name)
            elif next[1] == "}":
                return my_dict
            elif next[1] == "//":
                self._in_comment = True
                return self._parse_node(tokens, my_dict, prev_name)
            else:
                return self._parse_node(tokens, my_dict, prev_name)
        return self._parse_node(tokens, my_dict, prev_name)

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    cfg = SMConfig("ads.txt") 
    pp.pprint(cfg.load())
    print cfg.text()

