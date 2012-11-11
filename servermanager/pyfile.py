#!/usr/bin/env python

def write_pyfile(filename, indict):
    fh = open(filename, 'w+')
    for key, value in indict.iteritems():
        if type(value) in [int, float, bool]:
            fh.write("%s = %s\n" % (key, value))
        else:
            fh.write("%s = '%s'\n" % (key, value))
    fh.close()

def main():
    my_dict = {'a':1, 'b':True, 'c':'MyString'}
    filename = 'myfile.test'
    write_pyfile(filename, my_dict)

if __name__ == "__main__":
    main()
