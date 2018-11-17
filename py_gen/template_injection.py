import re


def template_inject(injects, template_name, file_out_name):
    '''
    copy template_name file to out file replacing for injects
    '''
    #file_contents = ''
    #print('file_out_name:', file_out_name)
    inject_reg = re.compile('{{[ ]*[0-9A-Za-z_-]+[ ]*}}')
    name_reg = re.compile('[0-9A-Za-z_-]+')
    with open(file_out_name, 'w') as file_out:
        with open(template_name, 'r') as template_f:
            for line in template_f:
                matches = re.findall(inject_reg, line)
                if matches:
                    for match in matches:
                        #print(match, '\n')
                        inject_name = re.search(name_reg, match).group(0)
                        line = line.replace(match, injects[inject_name], 1)

                #file_contents += line
                file_out.write(line)


