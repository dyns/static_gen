
def split_md_text(md_file):
    header = ''
    body = ''

    md_file.seek(0)

    first_line = md_file.readline()
    # empty file
    if not first_line:
        return ('', '')

    if first_line.strip().startswith('---'):
        buf = []
        while True:
            line = md_file.readline()
            buf.append(line)
            if line.strip().startswith('---'):
                break
            if not line:
                buf = []
                md_file.seek(0)
                break

        # remove dashes - the first and last lines
        if len(buf) >= 1:
            del buf[-1]

        header = ''.join(buf)

    buf = []

    while True:
        line = md_file.readline()
        if line:
            buf.append(line)
        else:
            break

    body = ''.join(buf)

    return (header, body)



