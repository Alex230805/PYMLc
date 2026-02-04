#!/usr/bin/env python3

import tokenizer;
import sys;
import os;


DEBUG:bool = False;

def help():
    print("""PYMLc is a html simple parser written with the only intent of extracting informations 
from local html pages (which can be downloaded for example) and formalize them inside 
a separate file with a raw-content format, where only the important informations are 
preserved without any html tags from the original file. 

It can support a list of pages or just one single page and will output in the default 
location ( the current position of PYMLc.py ) a list of raw text files, named the same 
as the original page, parsed with a simple tokenizer made just to grep the improtant 
informations and stripping off link tags, paragraph tags and/or any other tags intended 
to contain some content that might be important. Due to the simplicity of the html 
structural format it's possible to extract informations and output them not only as a raw 
output file, but also as a MarkDown file to preserve titles, link and so on.

Check the following parameter if needed.

Syntax: 
          pymlc.py [param] page1.html page2.html ...

-h:
    
    Print helper to get information.

-d [dest]:
    
    Change the default output location for each single file. Te 
    default one is './out'.

-s [src]:

    Change the default source directory from which PYMLc will search
    for the specified files. By default the specified file must include 
    the path, but if that's not the case it's possible to specify a 
    root directory that will be used as base. 

--set-enum:
    
    Include this to strip the default page name as the output file name.
    Every page will be written with an incremental numeric value such 
    as "page_0.txt", "page_1.txt"... instead of using the original 
    file name as the output file name.

-t [type]:
    
    Set the file type for the output format. Default is "text". The 
    available options are:
        - text : raw format
        - mark : markdown format, titles will be preserved


""");
    exit(1);

def parameter_error(param: str, message: str):
    print(f"Wrong parameter argument for '{param}': {message}");
    exit(1);

def main(argv: [str]):
    dest:str="./out";
    src:str = "./"
    custom_src:bool = False;
    file_types = {"text", "mark"};
    enum_prefix: bool = False;
    file_list: [str] = [];
    output_type: str = "text";
    i:int = 1;
    if len(argv) == 1: print("Invalid parameter, run with '-h' for more informations."); exit(1);
    while i < len(argv):
        if argv[i] == "-h":
            help();
        elif argv[i] == "-d":
            if i+1< len(argv):
                dest = argv[i+1];
                i+=1;
            else:
                parameter_error("-d", "Missing destination path name.");
        elif argv[i] == "--set-enum":
            enum_prefix = True;
        elif argv[i] == "-t":
            if i+1 < len(argv):
                if argv[i+1] not in file_types:
                    parameter_error("-t", f"{argv[i+1]} is not a supported type, see '-h' for help");
                else:
                    output_type = argv[i+1];
                    i+=1;
            else:
                parameter_error("-t", "Missing file type");
        elif argv[i] == "-s":
            if i+1 < len(argv):
                src = argv[i+1];
                custom_src = True;
                i+=1;
            else:
                parameter_error("-s", "Not a valid source file directory");
        else:
            file_list.append(argv[i]);
        i+=1;
    
    if not os.path.isdir(dest):
        os.mkdir(dest);
    if not os.path.isdir(src) and custom_src:
        print(f"Cannot find source directory, '{src}' does not exist");
        exit(1);

    for file in file_list:
        try:
            fpath:str = file;
            if custom_src:
                fpath = os.path.join(src,file);
            if not os.path.isfile(fpath):
                raise Exception(f"The specified '{file}' is not a valid file");
            f = open(fpath, "r");
            source:str = str(f.read());
            f.close();
            tokenized_output: [int, [dict]] = tokenizer.parse_html(source);
            if DEBUG: tokenizer.print_tokenizer_output(tokenized_output[1]);
            # TODO: continue the parser

        except Exception as ex:
            print(f"Error while parsing file: {ex}");
            exit(1);


    return 0;


main(sys.argv);
