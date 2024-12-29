
def html_write_row(file, values: list[str]) -> None:
    file.write("<tr>\n")
    for idx, item in enumerate(values):
        file.write("  <td")
        if (idx == len(values) - 1):
            file.write(' valign="top"')
        file.write(">" + str(item) + "</td>" + '\n')
    file.write("</tr>\n")


def html_table_write_header(file, values: list[str]) -> None:
    file.write("<tr>\n")
    for idx, item in enumerate(values):
        file.write("  <th onclick=\"sortTable({})\">".format(idx) + str(item) + "</th>" + '\n')
    file.write("</tr>\n")


def to_html_list(items, ordered: bool = False) -> str:
    pre = list(items)
    pre.sort()
    
    result = ""
    if ordered:
        result += '<ol>\n'
    else:
        result += '<ul>\n'

    for item in pre:
        result += '    <li>' + str(item) + '</li>\n'

    if ordered:
        result += '</ol>\n'
    else:
        result += '</ul>\n'
    
    return result


def html_embed_scripts(htmlFile):
    htmlFile.write('<script type = "text/javascript">\n')
    with open('scripts.js') as sFile:
        htmlFile.write(sFile.read())
    htmlFile.write("</script>\n")


def html_embed_styles(htmlFile):
    htmlFile.write('  <style>\n')
    with open('styles.css') as sFile:
        htmlFile.write(sFile.read())
    htmlFile.write('  </style>\n')


def write_html_header(htmlFile, title):
    htmlFile.write('<!DOCTYPE html>\n')
    htmlFile.write('<html>\n')
    htmlFile.write('<head>\n')
    htmlFile.write(f'  <title>{title}</title>\n')
    htmlFile.write('\n')
    html_embed_styles(htmlFile)
    htmlFile.write('</head>\n')
