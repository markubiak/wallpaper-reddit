class Blacklist:

    """
    Class wrapping blacklisting functionality to ignore
    bad or otherwise undesired wallpapers by URL.
    """


    def __init__(self, filename):

        """
        Initializes blacklist using textfile backing store.
        """

        self._fname = filename
        self.blacklist = []
        self.reload()


    def reload(self):

        """
        Reloads the blacklist store, updating self.blacklist.
        """

        with open(self._fname, 'r') as f:
            self.blacklist = f.read().split('\n')


    def add(self, url):

        """
        Adds the specified url to the blacklist and reloads.
        """

        with open(self._fname, 'a') as f:
            f.write(url + '\n')
        self.blacklist += [url]


    def is_blacklisted(self, url):

        """
        Check if specified url is blacklisted.
        """

        for link in self.blacklist:
            if link == url:
                return True
        return False

