import re 

def clean_text(input_string : str):
    output_string = input_string.strip().lower()
    output_string = re.sub(r'\W+',' ', output_string )
    return output_string.strip()