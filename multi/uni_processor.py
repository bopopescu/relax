################################################################################
#                                                                              #
# Copyright (C) 2007  Gary S Thompson (see https://gna.org/users/varioustoxins #
#                                      for contact details)                    #
#                                                                              #
#                                                                              #
# This file is part of the program relax.                                      #
#                                                                              #
# relax is free software; you can redistribute it and/or modify                #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation; either version 2 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# relax is distributed in the hope that it will be useful,                     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with relax; if not, write to the Free Software                         #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    #
#                                                                              #
################################################################################
import threading, Queue
import sys
import multi
import time,datetime

from multi.processor import Result_command,Result_string

#FIXME need to subclass
class Uni_processor(object):
    def __init__(self,relax_instance):
        self.relax_instance= relax_instance

        self.command_queue=[]
        self.memo_map={}



    def add_to_queue(self,command,memo=None):
        self.command_queue.append(command)
        if memo != None:
            command.set_memo_id(memo)
            self.memo_map[memo.memo_id()]=memo

    def run_queue(self):
        #FIXME: need a finally here to cleanup exceptions states
        for command in self.command_queue:
            print command


        self.run_command_queue()
        #TODO: add cheques for empty queuese and maps if now warn
        del self.command_queue[:]
        self.memo_map.clear()

    def run_command_queue(self):
    		for command in self.command_queue:
    			command.run(self)

    def run(self):
        start_time =  time.clock()
        self.relax_instance.run()
        end_time = time.clock()
        time_diff= end_time - start_time
        time_delta = datetime.timedelta(seconds=time_diff)
        print 'overall runtime: ' + time_delta.__str__() + '\n'





    def return_object(self,result):
        if isinstance(result, Exception):
		    #FIXME: clear command queue
		    #       and finalise mpi (or restart it if we can!
		    raise result



        if isinstance(result, Result_command):
            memo=None
            if result.memo_id != None:
                memo=self.memo_map[result.memo_id]
                result.run(self.relax_instance,self,memo)
            if result.memo_id != None and result.completed:
            		del self.memo_map[result.memo_id]

	    elif isinstance(result, Result_string):
	        #FIXME can't cope with multiple lines
	        print result.rank,result.string
	    else:
	        message = 'Unexpected result type \n%s \nvalue%s' %(result.__class__.__name__,result)
	        raise Exception(message)



if __name__ == '__main__':
    test =Uni_processor(None)
    print test

