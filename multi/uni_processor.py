###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing the uni-processor class."""

# Python module imports.
import threading, Queue
import sys, os

# relax module imports.
import multi
from multi.processor import Processor, Result_command, Result_string


class Uni_processor(Processor):
    """The uni-processor class."""

    def __init__(self, processor_size, callback):
        """Initialise the class.

        @param processor_size:  The number of processors.
        @type processor_size:   int
        @param callback:        The callback object.
        @type callback:         ?
        """
        super(Uni_processor, self).__init__(processor_size=1, callback=callback)

        if processor_size > 1:
            print('warning: uniprocessor can only support 1 processor you requested %d' % processor_size)
            print('continuing...\n')

        self.command_queue = []
        self.memo_map = {}

        self.slave_stdio_capture = self.std_stdio_capture(pre_strings=('', ''))


    def add_to_queue(self, command, memo=None):
        self.command_queue.append(command)
        if memo != None:
            command.set_memo_id(memo)
            self.memo_map[memo.memo_id()] = memo


    def exit(self):
        sys.exit()


    def get_intro_string(self):
        """Return the string to append to the end of the relax introduction string.

        @return:    The string describing this Processor fabric.
        @rtype:     str
        """

        # Return the string.
        return "Uni-processor"


    def get_name(self):
        # FIXME may need system dependent changes
        return '%s-%s' % (os.getenv('HOSTNAME'), os.getpid())


#    def on_master(self):
#        return True


    def processor_size(self):
        return 1


    def rank(self):
        return 0


    def return_object(self, result):

        local_save_stdout = sys.stdout
        local_save_stderr = sys.stderr
        self.restore_stdio()

        if isinstance(result, Exception):
            #FIXME: clear command queue
		    #       and finalise mpi (or restart it if we can!
            raise result
        elif isinstance(result, Result_command):
            memo = None
            if result.memo_id != None:
                memo = self.memo_map[result.memo_id]
            result.run(self, memo)
            if result.memo_id != None and result.completed:
                del self.memo_map[result.memo_id]

        elif isinstance(result, Result_string):
            sys.stdout.write(result.string)
        else:
            message = 'Unexpected result type \n%s \nvalue%s' %(result.__class__.__name__, result)
            raise Exception(message)
        sys.stdout = local_save_stdout
        sys.stderr = local_save_stderr


    def run(self):
        try:
            self.pre_run()
            self.callback.init_master(self)
            self.post_run()
        except Exception, e:
            self.callback.handle_exception(self, e)


    def run_queue(self):
        #FIXME: need a finally here to cleanup exceptions states for windows etc

        last_command = len(self.command_queue)-1
        for i, command  in enumerate(self.command_queue):
            completed = (i == last_command)

            self.capture_stdio(self.slave_stdio_capture)
            command.run(self, completed)
            self.restore_stdio()

        #self.run_command_queue()
        #TODO: add cheques for empty queues and maps if now warn
        del self.command_queue[:]
        self.memo_map.clear()
