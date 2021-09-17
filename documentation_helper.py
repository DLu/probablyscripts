#!/usr/bin/python3
import pathlib
import re
import requests

WSD_URL = 'https://www.websequencediagrams.com/'
EQ_PATTERN = re.compile(r'!eq\[([^\]]*[^\\])\]')


def translate_sequence_diagram(text, out_fn, style='modern-blue'):
    request = {}
    request['message'] = text
    request['style'] = style
    request['apiVersion'] = '1'

    r = requests.post(WSD_URL, data=request)
    response = r.json()
    if 'img' not in response:
        print('Invalid response from server.')
        return

    with open(out_fn, 'wb') as f:
        print(out_fn)
        r = requests.get(WSD_URL + response['img'])
        f.write(r.content)


def clean_equation_text(s):
    new_s = ''
    for c in s:
        if c in ' \\(){}':
            continue
        elif c.isalnum():
            new_s += c
        else:
            new_s += '_'
    return new_s


def update_markdown_with_equations(input_markdown_fn, output_markdown_fn):
    s = open(input_markdown_fn).read()
    m = EQ_PATTERN.search(s)
    parent_folder = input_markdown_fn.parent
    while m:
        equation = m.group(1)
        img_filename = parent_folder / (clean_equation_text(equation) + '.gif')
        if not img_filename.exists():
            url = 'http://latex.codecogs.com/gif.download?' + equation
            print('\t{} => {}'.format(m.group(0), img_filename))
            img = requests.get(url)
            with open(img_filename, 'wb') as f:
                f.write(img.content)
        # if img_filename in gifs_to_remove:
         #   gifs_to_remove.remove(img_filename)
        s = s.replace(m.group(0), '![%s](%s)' % (equation, img_filename))
        m = EQ_PATTERN.search(s)

    with open(output_markdown_fn.name, 'w') as f:
        f.write(s)


if __name__ == '__main__':
    current_directory = pathlib.Path('.')
    for fn in current_directory.glob('*'):
        if fn.suffix == '.flow' and False:
            text = open(fn).read()
            out_fn = fn.with_suffix('.png')
            translate_sequence_diagram(text, out_fn)
        elif fn.suffix == '.md' and fn.stem[0] == '_':
            output_path = fn.parent / (fn.stem[1:] + '.md')
            gifs = update_markdown_with_equations(fn, output_path)


#existing_gifs = [p for p in doc_folder.iterdir() if p.suffix == '.gif']
#gifs_to_remove = set(existing_gifs)

# for gif_to_remove in gifs_to_remove:
 #   print('Deleting {}'.format(gif_to_remove))
  #  gif_to_remove.unlink()
