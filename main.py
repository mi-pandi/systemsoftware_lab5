from fs_commands import *


def ask_user_for_command():
    try:
        input_line = input('>>> ')
        eval('fs_' + input_line)
    except NameError as error:
        print_error(f'Error in function name! {error}')
    except SyntaxError as error:
        print_error(f'Syntax error! {error}')
    except TypeError as error:
        print_error(f'Arguments error! {error}')
    finally:
        ask_user_for_command()


if __name__ == '__main__':
    ask_user_for_command()
