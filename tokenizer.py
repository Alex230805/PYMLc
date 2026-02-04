

# quick reference for token value and token literal word

global TOK_VAL;  
global TOK_NAME;  
global TOK_LIT;
global token_table;
global token_list;
global UNDEFINED_TOKEN_VAL;
global UNDEFINED_TOKEN_NAME;

TOK_VAL:int=0;
TOK_NAME:int=1;
TOK_LIT:int=2;

UNDEFINED_TOKEN_VAL:int = -69;
UNDEFINED_TOKEN_NAME: str = "Not a token";

# Main token table: edit here to add a new token usable 
# by the lexer. 

token_table: dict = dict({
        "ARROW_LEFT": "<",
        "ARROW_RIGHT": ">",
        "CLOSE_SLASH": "/",
        "HTML_TAG_P": "p",
        "HTML_TAG_A": "a",
        "HTML_TAG_H1": "h1",
        "HTML_TAG_H2": "h2",
        "HTML_TAG_H3": "h3",
        "HTML_TAG_H4": "h4",
        "HTML_TAG_H5": "h5",
        "HTML_TAG": "html",
        "HTML_BODY": "body",
        "HTML_FOOTER": "footer",
        "HTML_HEAD": "head",
        "HTML_TAG_SECTION": "section",
        "HTML_TAG_DIV": "div",
        "HTML_TAG_UL": "ul",
        "HTML_TAG_LI": "li",
        "HTML_TITLE": "title",
        "DOCTYPE": "DOCTYPE",
        "ASSIGNMENT": "=",
        "DOUBLE_QUOTE": "\"",
        "HTML_CLASS": "class",
        "HTML_SRC": "src",
        "HTML_HREF": "href",
});

token_list: [(int, str, str)] = [];

# Token list initialization 
for i, tok in enumerate(token_table):
    token_list.append((i, tok, token_table[tok]));


def get_token_lit(i):
    return token_list[i][TOK_LIT];

def get_token_name_by_value(token_value: int):
    for i in token_list:
        if i[TOK_VAL] == token_value:
            return i[TOK_NAME];
    return UNDEFINED_TOKEN_NAME;

def get_token_value_by_name(token_name: str):
    for i in token_list:
        if i[TOK_NAME] == token_name:
            return i[TOK_VAL];
    return UNDEFINED_TOKEN_VAL;

def get_token_lit_by_value(token_value: int):
    for i in token_list:
        if i[TOK_VAL] == token_value:
            return i[TOK_LIT];
    return UNDEFINED_TOKEN_NAME;

def get_token_val(i):
    return token_list[i][TOK_VAL];

def get_token_name(i):
    return token_list[i][TOK_NAME];

# By using the token_tracker embedded in the tokenized_output array as the first element, 
# this function will evaluate if from the current position there is a sequence of tokens 
# that define a valid HTML tag like "<p>" or "</p>". 
def has_valid_tag(tokenized_output: [int, [dict]]): 
    token_tracker = tokenized_output[0]; 
    tag_limit_start:int = 0;
    tag_limit_end:int  = 0;
    for i in token_list:
        if i[TOK_NAME] == "CLOSE_SLASH":
            tag_limit_start = i[TOK_VAL];
            break;
    for i in token_list:
        if i[TOK_NAME] == "DOCTYPE":
            tag_limit_end = i[TOK_VAL];
            break;

    if not (get_token_value_by_name("ARROW_LEFT") == tokenized_output[1][token_tracker]["token"]): return [False, tokenized_output];
    token_tracker += 1;
    if get_token_value_by_name("CLOSE_SLASH") == tokenized_output[1][token_tracker]["token"]: token_tracker += 1;
    if not (tag_limit_start < tokenized_output[1][token_tracker]["token"] and tokenized_output[1][token_tracker]["token"] < tag_limit_end): return [False, tokenized_output];
    token_tracker += 1;
    end:bool = False;
    while not end and token_tracker < len(tokenized_output[1]):
        if tokenized_output[1][token_tracker]["token"] == get_token_value_by_name("ARROW_RIGHT"):
            end = True;
        else:
            token_tracker += 1;

    if not end: return [False, tokenized_output];
    tokenized_output[0] = token_tracker;
    return [True, tokenized_output];


# This is the lexer that parse the source file provided and return a list of tokens 
# and a tracker (set to 0) in the form of an array of [int, [dict]]. 

def parse_html(source: str):
    tracker:int=0;
    tokenized_output: [dict] = [];
    while tracker < len(source):
        increment: int=1;
        end:bool = False;
        i:int = 0;
        while i < len(token_list) and not end:
            current_token:int = token_list[i][TOK_VAL];
            token_literal:str = token_list[i][TOK_LIT];
            buffer:str = "";
            j:int = 0;
            while j < len(token_literal):
                if tracker+j < len(source):
                    buffer += source[tracker+j];
                j+=1;
            if str(buffer).lower() == str(token_literal).lower():
                # writing down tag as new token
                tokenized_output.append(dict({
                    "token": current_token,
                    "pos": tracker,
                    "len": len(token_literal)
                }));
                increment = len(token_literal);
                end = True;
            i+=1;
        tracker += increment;
    return [0, tokenized_output];

# debug function: print the token list created by parse_html(source:str). 
def print_tokenizer_output(tok: [dict]):
    for i, t in enumerate(tok):
        print(f"Tok {get_token_name_by_value(t['token'])} -> '{get_token_lit_by_value(t['token'])}' found at {t['pos']}, tok pos = {i}");
