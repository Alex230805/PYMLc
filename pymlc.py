#!/usr/bin/env python3

import tokenizer;
import sys;
import os;
import time;

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

--debug: 

    Output the tokenizer array used for parsing the content.

""");
    exit(1);

def parameter_error(param: str, message: str):
    print(f"Wrong parameter argument for '{param}': {message}");
    exit(1);



def parse_html(ctx:dict):
    tracker:int = ctx["tokens"][0];
    tag_open:bool = False;
    status: int = tokenizer.INVALID_TAG;
    current_token:int = ctx["tokens"][1][tracker]["token"];

    start:int = 0;
    length:int = 0;

    stack:[int] = [];
    
    while tracker < len(ctx["tokens"][1]):
        if not tag_open:
            status, ctx["tokens"] = tokenizer.has_valid_tag(ctx["tokens"]);
            tracker = ctx["tokens"][0];
            if tracker < len(ctx["tokens"][1]):
                current_token = ctx["tokens"][1][tracker]["token"];
            if status == tokenizer.TAG_OPEN:
                tag_open = True;
                stack.append(ctx["tokens"][1][tracker-1]["pos"]+1);
            if status == tokenizer.TAG_CLOSE:
                if len(stack) > 0:
                    start = stack.pop(-1);
                    length = (ctx["tokens"][1][tracker-4]["pos"]-1) - start;
                    j:int = 0;
                    while j <= length:
                        ctx["out"] += ctx["src"][start+j];
                        j+=1;
                    ctx["out"] += "\n";
                    stack = [];
            if status == tokenizer.INVALID_TAG:
                current_token:int = ctx["tokens"][1][tracker]["token"];
                raise Exception(f"invalid tag at {ctx["tokens"][1][tracker]["pos"]}, pointing at tracker {tracker}: '{tokenizer.get_token_name_by_value(current_token)}': literal: '{tokenizer.get_token_lit_by_value(current_token)}'");

        # search for the first token for the close tag
        if tracker < len(ctx["tokens"][1]):
            current_token = ctx["tokens"][1][tracker]["token"];
        if tag_open and current_token == tokenizer.get_token_value_by_name("ARROW_LEFT"):
            tag_open = False;
            ctx["tokens"][0] = tracker;
        else:
            tracker += 1;
    return ctx;

def main(argv: [str]):
    dest:str="./out";
    src:str = "./"
    custom_src:bool = False;
    file_types = {"text", "mark"};
    enum_prefix: bool = False;
    file_list: [str] = [];
    output_type: str = "text";
    i:int = 1;
    DEBUG = False;
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
        elif argv[i] == "--debug":
            DEBUG = True;
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

            message = f"Reading {fpath}".ljust(64);
            print(f"{message}{time.asctime():>}");
            f = open(fpath, "r");
            source:str = str(f.read());
            f.close();
            tokenized_output: [int, [dict]] = tokenizer.html_lexer(source);
            if DEBUG: tokenizer.print_tokenizer_output(tokenized_output[1]);
            parse_ctx:dict = {
                "src": source,
                "out": "",
                "tokens": tokenized_output
            };
            message = f"Parsing {fpath}".ljust(64);
            print(f"{message}{time.asctime():>}");
            # TODO: add the nested tag: <p>this is a <a>button</a></p>
            return_ctx = parse_html(parse_ctx);
            fpath = os.path.join(dest, file.split(".")[0]+".txt");
            
            message = f"Writing down {fpath}".ljust(64);
            print(f"{message}{time.asctime():>}");
            f = open(fpath, "w");
            f.write(return_ctx["out"]);
            f.close();

            print("Done!");

        except Exception as ex:
            print(f"Error while parsing file: {ex}");
            exit(1);
        print("Coffe is ready sir!");
    return 0;


main(sys.argv);
