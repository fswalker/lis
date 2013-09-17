from multiprocessing import Process, Pipe

class Algorithm:
    """
        The class delivers functionality for performing calculations on db
        in order to group lanterns from db into collinear sets.
        It is instantiated for exactly one specific problemid to make calculations.
    """
    def __init__(self, problemid):
        self._problemid = problemid
        self._client, self._server = Pipe(False)

    def _group_lanterns(self):
        """ private
            Method used to perform calculations in db for grouping lanterns.
            After each step it sends the progress via connection in self.server.
        """
        try:
            self._server.send([10, ''])
            self._server.send([90, ''])
            #raise Exception
        except:
            self._server.send([90, 'danger'])
            return False;
        finally:
            self._server.close()
        return True

    def run(self):
        """ public
            Used to run calculations.
        """
        self._process = Process(target = self._group_lanterns, args = ())
        self._process.start()

    def status(self):
        """ public
            Checks if there are any messages from process performing calculations about the progress.
        """
        if self._client.poll():
            return self._client.recv()
        else:
            return False
