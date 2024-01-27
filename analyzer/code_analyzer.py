# write your code here
import argparse
import os
import re
import ast


def check_line_length(line, line_number, file_path):
    if len(line) >= 79:
        return "{}: Line {}: S001 Line too long".format(file_path, line_number)


def check_indentation(line, line_number, file_path):
    n_whitespace = 0
    if len(line) == 0:
        pass
    elif line[0] == " ":
        for char in line:
            if char == " ":
                n_whitespace += 1
            else:
                break
    if n_whitespace % 4 != 0:
        return "{}: Line {}: S002 Indentation is not a multiple of four".format(file_path, line_number)


def check_semicolon(line, line_number, file_path):
    if len(line) == 0:
        pass
    elif line[len(line) - 1] == ";" and '#' not in line:
        return "{}: Line {}: S003 Unnecessary semicolon".format(file_path, line_number)
    elif ';' in line and '#' in line:
        if line.index(';') < line.index('#'):
            return "{}: Line {}: S003 Unnecessary semicolon".format(file_path, line_number)


def check_inline_comment(line, line_number, file_path):
    if len(line) == 0:
        pass
    elif '#' in line:
        if line[line.index('#') - 1] and line[line.index('#') - 2] == " ":
            pass
        elif line.index('#') == 0:
            pass
        else:
            return "{}: Line {}: S004 Less than two spaces before inline comments".format(file_path, line_number)


def check_todo(line, line_number, file_path):
    if len(line) == 0:
        pass
    elif 'todo' in line or 'todo'.upper() in line or 'Todo' in line:
        if '#' in line:
            word_following_symbol = ""
            index_symbol = "".join(line.split()).index('#')
            for index in range(index_symbol + 1, index_symbol + 5):
                word_following_symbol += "".join(line.split())[index]
            if word_following_symbol in ["Todo", "todo", "TODO"]:
                return "{}: Line {}: S005 TODO found".format(file_path, line_number)


def check_empty_lines(lines, line_number, file_path):
    n_empty_line = 0
    for index, line in lines:
        if len(line) == 0:
            n_empty_line += 1
        elif n_empty_line > 2 and line_number == index:
            _empty_line = 0
            return "{}: Line {}: S006 More than two blank lines used before this line".format(file_path, line_number)
        elif len(line) != 0:
            n_empty_line = 0


def check_def_spacing(line, line_number, file_path):
    class_template = r"[\w\s\d]*class\s\w"
    def_template = r"[\w\s\d]*def\s\w"

    if "class" in line and re.match(class_template, line) is None:
        return "{}: Line {}: S007 Too many spaces after 'class'".format(file_path, line_number)
    elif "def" in line and re.match(def_template, line) is None:
        return "{}: Line {}: S007 Too many spaces after 'def'".format(file_path, line_number)


def check_class_name(line, line_number, file_path):
    camelcase_template = r"[\w\s\d]*class\s+[A-Z]\w+[A-Z]?\w+?"
    class_name = re.sub(r"class\s+", '', line).strip(":\n")
    if "class" in line and re.match(camelcase_template, line) is None:
        return "{}: Line {}: S008 Class name '{}' should use CamelCase".format(file_path, line_number, class_name)


def check_func_name(line, line_number, file_path):
    snakecase_template = r"\s*def\s+[a-z_]+"
    prefix_removed = re.sub(r"\s+def\s+", '', line)
    def_name = re.sub(r"\([\w\s,]*\):\s", "", prefix_removed)
    if "def" in line and re.match(snakecase_template, line) is None:
        return "{}: Line {}: S009 Function name '{}' should use snake_case".format(file_path, line_number, def_name)


def check_fun_attributes(line_number, file_path):
    file_to_read = open(file_path, 'r').read()
    tree = ast.parse(file_to_read)
    nodes = ast.walk(tree)
    error_message = ""

    for node in nodes:
        if isinstance(node, ast.FunctionDef):
            arguments = [fun.arg for fun in node.args.args]
            defaults = [node.args.defaults]

            for arg in arguments:
                arg_template = "[a-z0-9]+"
                if re.fullmatch(arg_template, arg) is None and node.lineno == int(line_number):
                    error_message += ("{}: Line {}: S010 Argument name '{}' should be written in snake_case"
                                      .format(file_path, line_number, arg))

            for i in node.body:
                if isinstance(i, ast.Assign):
                    current_line = i.lineno
                    array = i.targets
                    for item in array:
                        var_template = "[a-z0-9]+"
                        if isinstance(item, ast.Name):
                            if re.fullmatch(var_template, item.id) is None and current_line == int(line_number):
                                error_message += ("{}: Line {}: S011 Variable '{}' should be written in snake_case"
                                                  .format(file_path, line_number, item.id))

            for default in defaults:
                for i in default:
                    if isinstance(i, (ast.List, ast.Dict, ast.Set)) and node.lineno == int(line_number):
                        error_message += ("{}: Line {}: S012 Default argument value is mutable"
                                          .format(file_path, line_number))

    if error_message != "":
        return error_message


def style_check(lines, line, line_number, file_path):
    my_list = [(check_line_length(line, line_number, file_path)),
               check_indentation(line, line_number, file_path),
               check_semicolon(line, line_number, file_path),
               check_inline_comment(line, line_number, file_path),
               check_todo(line, line_number, file_path),
               check_empty_lines(lines, line_number, file_path),
               check_def_spacing(line, line_number, file_path),
               check_class_name(line, line_number, file_path),
               check_func_name(line, line_number, file_path),
               check_fun_attributes(line_number, file_path)]

    issues_in_line = list(filter(lambda x: x is not None, my_list))
    return issues_in_line


def find_python_files(dir_path):
    path_list = []

    folders = [dir_path]

    while len(folders) != 0:
        for folder in folders:
            for item in os.listdir(folder):
                file_path = folder + f"/{item}"
                if os.path.isfile(file_path) and ".py" in file_path:
                    path_list.append(file_path)
                elif os.path.isdir(file_path):
                    folders.append(file_path)
            folders.remove(folder)

    path_list.sort()
    return path_list


def file_review(file_path):
    file_to_review = open(file_path, 'r')
    lines = list(enumerate([i.strip("\n")for i in file_to_review.readlines()], start=1))

    for line_number, line in lines:
        line = style_check(lines, line, line_number, file_path)
        if len(line) != 0:
            print(*line, sep="\n")

    file_to_review.close()


parser = argparse.ArgumentParser(description="Input directory name you are looking for")

parser.add_argument('file')
# parser.add_argument('directory_or_file')

args = parser.parse_args()

# with open(args.file) as file:
#    exec(file.read())

path = args.file


if os.path.isfile(path):
    file_review(path)
elif os.path.isdir(path):
    file_list = find_python_files(path)
    for file in file_list:
        file_review(file)
