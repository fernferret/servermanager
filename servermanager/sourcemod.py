#!/usr/bin/env python
'''Allows reading and writing of SourceMod style configs.

Sourcemod configs are effectively space/newline separated 
python dictionaries. This class simply facilitates reading
and writing them.
'''

import tokenize
import pprint

class ParseError(Exception):
    '''Thrown when there was a problem parsing the SourceMod config.'''
    pass

class SMConfig(object):
    '''The sourcemod config class.

    You should instantiate one of these with the
    filename you wish it to parse. By default, it will
    load the config into memory.

    **Remember: These are configuration files, not databases.**

    If you have too many values, think to yourself, should 
    this be a database?'''
    def __init__(self, filename):
        self._in_comment = False
        self.filename = filename
        self.cfg = self.load()
    
    def save(self, filename=None):
        '''Save the configuration to disk.
        
        If no arguments are passed, this will save the config
        that was last loaded or saved.
        
        Params:
          filename - *OPTIONAL* The full path to save.'''
        if filename:
            self.filename = filename
        my_file = open(self.filename, "r+")
        f.seek(0)
        f.write(self._get_as_text(self.cfg))
        my_file.close()
    
    def load(self, filename=None):
        '''Load the configuration from disk.
        
        If no arguments are passed, this will save the config
        that was last loaded or saved.
        
        Params:
          filename - *OPTIONAL* The full path to load.'''
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
        '''A recursive parser using the python tokenizer.
        
        This method will recursively translate a sourcemod
        config file into a python dictionary.

        The parser will NOT return the dictionary, but rather
        the dictionary you pass into it, will be populated:

        ...
        sample_dict = {}
        self._parse_node(tokens, sample_dict)
        print sample_dict
          => {"Root"{"Key" "Value"}}
        ...

        Params:
          tokens    - The tokens generated from the file.
                      Get these with tokenizer.generate_tokens.
          my_dict   - The dictionary that should store the values.
          prev_name - *OPTIONAL*'''

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

def main():
    '''A simple test method to verify we're good to go!'''
    pp = pprint.PrettyPrinter(indent=4)
    cfg = SMConfig("ads.txt") 
    pp.pprint(cfg.load())
    print cfg.text()
    
if __name__ == "__main__":
    main()
