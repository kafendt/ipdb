# Copyright (c) 2011-2016 Godefroid Chapelle and ipdb development team
#
# This file is part of ipdb.
# Redistributable under the revised BSD license
# https://opensource.org/licenses/BSD-3-Clause


import os
import sys

from contextlib import contextmanager

__version__= "0.10.3"

from IPython import get_ipython
from IPython.core.debugger import BdbQuit_excepthook
from IPython.terminal.ipapp import TerminalIPythonApp
from IPython.terminal.embed import InteractiveShellEmbed


shell = get_ipython()
if shell is None:
    # Not inside IPython
    # Build a terminal app in order to force ipython to load the
    # configuration
    ipapp = TerminalIPythonApp()
    # Avoid output (banner, prints)
    ipapp.interact = False
    ipapp.initialize([])
    shell = ipapp.shell
else:
    # Running inside IPython

    # Detect if embed shell or not and display a message
    if isinstance(shell, InteractiveShellEmbed):
        sys.stderr.write(
            "\nYou are currently into an embedded ipython shell,\n"
            "the configuration will not be loaded.\n\n"
        )

# Let IPython decide about which debugger class to use
# This is especially important for tools that fiddle with stdout
debugger_cls = shell.debugger_cls
def_colors = shell.colors

def add_custom_keybinds(p):
    def next_command(event):
        p.preloop()
        line = p.precmd("next")
        stop = p.onecmd(line)
        stop = p.postcmd(stop, line)
        p.postloop()
        buff = event.current_buffer
        buff.validate_and_handle()
    def step_command(event):
        p.preloop()
        line = p.precmd("step")
        stop = p.onecmd(line)
        stop = p.postcmd(stop, line)
        p.postloop()
        buff = event.current_buffer
        buff.validate_and_handle()
    def up_command(event):
        p.preloop()
        line = p.precmd("up")
        stop = p.onecmd(line)
        stop = p.postcmd(stop, line)
        p.postloop()
        buff = event.current_buffer
        buff.validate_and_handle()
    def down_command(event):
        p.preloop()
        line = p.precmd("down")
        stop = p.onecmd(line)
        stop = p.postcmd(stop, line)
        p.postloop()
        buff = event.current_buffer
        buff.validate_and_handle()
    def where_command(event):
        p.preloop()
        line = p.precmd("where")
        stop = p.onecmd(line)
        stop = p.postcmd(stop, line)
        p.postloop()
        buff = event.current_buffer
        buff.validate_and_handle()
    def args_command(event):
        p.preloop()
        line = p.precmd("args")
        stop = p.onecmd(line)
        stop = p.postcmd(stop, line)
        p.postloop()
        buff = event.current_buffer
        buff.validate_and_handle()
    def continue_command(event):
        p.preloop()
        line = p.precmd("continue")
        stop = p.onecmd(line)
        stop = p.postcmd(stop, line)
        p.postloop()
        buff = event.current_buffer
        buff.validate_and_handle()
    def longlist_command(event):
        p.preloop()
        line = p.precmd("longlist")
        stop = p.onecmd(line)
        stop = p.postcmd(stop, line)
        p.postloop()
        buff = event.current_buffer
        buff.validate_and_handle()
    def list_locals_command(event):
        p.preloop()
        line = p.precmd("from tabulate import tabulate;;pp tabulate([[k, type(v).__name__, '|'] for k, v in locals().items() if k not in ['tabulate', 'ipdb']])")
        stop = p.onecmd(line)
        stop = p.postcmd(stop, line)
        p.postloop()
        buff = event.current_buffer
        buff.validate_and_handle()

    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.shortcuts.prompt import PromptSession
    from prompt_toolkit.enums import EditingMode
    from prompt_toolkit.formatted_text import PygmentsTokens
    from prompt_toolkit.enums import DEFAULT_BUFFER
    from prompt_toolkit.filters import (Condition, has_focus, has_selection,
        vi_insert_mode, emacs_insert_mode)
    from prompt_toolkit.key_binding.bindings.completion import display_completions_like_readline
    from pygments.token import Token
    from IPython.terminal.shortcuts import suspend_to_bg, cursor_in_leading_ws
    from IPython.core.completer import IPCompleter
    from IPython.terminal.ptutils import IPythonPTCompleter
    import signal

    def get_prompt_tokens():
        return [(Token.Prompt, p.prompt)]

    compl = IPCompleter(shell=p.shell,
                                namespace={},
                                global_namespace={},
                                parent=p.shell,
                               )
    p._ptcomp = IPythonPTCompleter(compl)

    kb = KeyBindings()
    supports_suspend = Condition(lambda: hasattr(signal, 'SIGTSTP'))
    kb.add('c-z', filter=supports_suspend)(suspend_to_bg)

    if p.shell.display_completions == 'readlinelike':
        kb.add('tab', filter=(has_focus(DEFAULT_BUFFER)
                              & ~has_selection
                              & vi_insert_mode | emacs_insert_mode
                              & ~cursor_in_leading_ws
                          ))(display_completions_like_readline)

    kb.add('c-n')(next_command)
    kb.add('c-s')(step_command)
    kb.add('c-o')(up_command)
    kb.add('c-p')(down_command)
    kb.add('c-w')(where_command)
    kb.add('c-a')(args_command)
    kb.add('c-t')(continue_command)
    kb.add('c-l')(longlist_command)
    kb.add('c-v')(list_locals_command)

    p.pt_app = PromptSession(
        message=(lambda: PygmentsTokens(get_prompt_tokens())),
        editing_mode=getattr(EditingMode, p.shell.editing_mode.upper()),
        key_bindings=kb,
        history=p.shell.debugger_history,
        completer=p._ptcomp,
        enable_history_search=True,
        mouse_support=p.shell.mouse_support,
        complete_style=p.shell.pt_complete_style,
        style=p.shell.style,
        inputhook=p.shell.inputhook,
    )
    return p


def _init_pdb(context=3, commands=[]):
    try:
        p = debugger_cls(def_colors, context=context)
    except TypeError:
        p = debugger_cls(def_colors)
    p.rcLines.extend(commands)

    p = add_custom_keybinds(p)

    return p


def wrap_sys_excepthook():
    # make sure we wrap it only once or we would end up with a cycle
    #  BdbQuit_excepthook.excepthook_ori == BdbQuit_excepthook
    if sys.excepthook != BdbQuit_excepthook:
        BdbQuit_excepthook.excepthook_ori = sys.excepthook
        sys.excepthook = BdbQuit_excepthook


def set_trace(frame=None, context=15):
    wrap_sys_excepthook()
    if frame is None:
        frame = sys._getframe().f_back
    p = _init_pdb(context).set_trace(frame)
    if p and hasattr(p, 'shell'):
        p.shell.restore_sys_module_state()


def post_mortem(tb=None):
    wrap_sys_excepthook()
    p = _init_pdb()
    p.reset()
    if tb is None:
        # sys.exc_info() returns (type, value, traceback) if an exception is
        # being handled, otherwise it returns None
        tb = sys.exc_info()[2]
    if tb:
        p.interaction(None, tb)


def pm():
    post_mortem(sys.last_traceback)


def run(statement, globals=None, locals=None):
    _init_pdb().run(statement, globals, locals)


def runcall(*args, **kwargs):
    return _init_pdb().runcall(*args, **kwargs)


def runeval(expression, globals=None, locals=None):
    return _init_pdb().runeval(expression, globals, locals)


@contextmanager
def launch_ipdb_on_exception():
    try:
        yield
    except Exception:
        e, m, tb = sys.exc_info()
        print(m.__repr__(), file=sys.stderr)
        post_mortem(tb)
    finally:
        pass


_usage = """\
usage: python -m ipdb [-c command] ... pyfile [arg] ...

Debug the Python program given by pyfile.

Initial commands are read from .pdbrc files in your home directory
and in the current directory, if they exist.  Commands supplied with
-c are executed after commands from .pdbrc files.

To let the script run until an exception occurs, use "-c continue".
To let the script run up to a given line X in the debugged file, use
"-c 'until X'"
ipdb version %s.""" % __version__


def main():
    import traceback
    import sys
    import getopt

    try:
        from pdb import Restart
    except ImportError:
        class Restart(Exception):
            pass
    
    opts, args = getopt.getopt(sys.argv[1:], 'hc:', ['--help', '--command='])

    if not args:
        print(_usage)
        sys.exit(2)
    
    commands = []
    for opt, optarg in opts:
        if opt in ['-h', '--help']:
            print(_usage)
            sys.exit()
        elif opt in ['-c', '--command']:
            commands.append(optarg)

    mainpyfile = args[0]     # Get script filename
    if not os.path.exists(mainpyfile):
        print('Error:', mainpyfile, 'does not exist')
        sys.exit(1)

    sys.argv = args     # Hide "pdb.py" from argument list

    # Replace pdb's dir with script's dir in front of module search path.
    sys.path[0] = os.path.dirname(mainpyfile)

    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. There is a "restart" command
    # which allows explicit specification of command line arguments.
    pdb = _init_pdb(commands=commands)
    while 1:
        try:
            pdb._runscript(mainpyfile)
            if pdb._user_requested_quit:
                break
            print("The program finished and will be restarted")
        except Restart:
            print("Restarting", mainpyfile, "with arguments:")
            print("\t" + " ".join(sys.argv[1:]))
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            print("The program exited via sys.exit(). Exit status: ", end='')
            print(sys.exc_info()[1])
        except:
            traceback.print_exc()
            print("Uncaught exception. Entering post mortem debugging")
            print("Running 'cont' or 'step' will restart the program")
            t = sys.exc_info()[2]
            pdb.interaction(None, t)
            print("Post mortem debugger finished. The " + mainpyfile +
                  " will be restarted")

if __name__ == '__main__':
    main()
