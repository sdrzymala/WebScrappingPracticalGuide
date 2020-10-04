import re 

def clean_text(input_string : str):
    
    output = []
    for word in input_string.split(" "):
        new_word = ''
        for letter in word:
            if letter.isalpha() or letter.isdigit() or letter in ['*']:
                new_word += letter.lower()
            else:
                new_word += ' '
        output.append(new_word)

    _output_string = " ".join(output).strip()
    output_string = re.sub(' +', ' ', _output_string)

    if len(output_string) == 0:
        output_string = '#'

    return output_string