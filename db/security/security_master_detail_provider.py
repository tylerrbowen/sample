
class SecurityMasterDetailProvider(object):

    def init(self, master):
        """
        Initializes the detail provider with the same database source as the master.
        @param master  the security master, not null
        """
        pass

    def loadSecurityDetail(self, base):
        """
        Loads the security based on the supplied base.
            * The caller will already have loaded the contents of {@code ManageableSecurity}
            * but will not have created a class of the correct type. The implementation
            * must load the full detail and copy the data from the base object to the result.
            *
            * @param base  the base security, not null
            * @return the loaded security, not null
        """
        pass

    def storeSecurityDetail(self, security):
        """
        Stores the specified security.
        The caller will already have stored the contents of {@code ManageableSecurity}
        so the implementation only needs to store details of the subclass.
        @param security  the security to store, not null
        """
        pass

    def extendSearch(self, request, args):
        """
        Extends the search based on subclasses of the search request.
        The implementation should check if the request is of a known additional type
        and process it. The arguments should be updated as appropriate.
        A no-op implementation will do nothing.
        @param request  the request to search for, not null
        @param args  the search arguments, not null
        """
        pass