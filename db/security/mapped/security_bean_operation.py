

class SecurityBeanOperation(object):
    """
    /**
     * Operations to convert a real entity to/from a bean and hence to/from the Hibernate database.
     * @param <S> the security
     * @param <H> the Hibernate bean
     */
    """    
    def getBeanClass(self):
        """
        /**
        * Returns the bean implementation class.
        * @return the Hibernate bean class
        */
        """
        pass
    
    def getSecurityClass(self):
        """
        /**
        * Returns the security implementation class.
        * @return the security class
        */
        """
        pass
    
    def getSecurityType(self):
        """
        /**
        * Returns the security type name.
        * @return the bean class
        */
        """
        pass
    
    def createBean(self, context, secMasterSession, security):
        """
        /**
        * Create a bean representation of the security. Does not need to set the base properties
        * of SecurityBean.
        * @param context  the context
        * @param secMasterSession  the DAO
        * @param security  the security
        * @return the created Hibernate bean
        */
        """
        pass
    
    def createSecurity(self, context, bean):
        """
        /**
        * Convert a bean representation to a security.
        * @param context  the context
        * @param bean  the Hibernate bean
        * @return the created security
        */
        """
        pass
    
    def resolve(self, context, secMasterSession, now, bean):
        """
        /**
        * Loads additional (deep) data for a security bean. For example to implement date constrained relationships
        * that Hibernate alone can't deal with. May update the supplied bean, and return it, or return a new bean.
        * @param context  the context
        * @param secMasterSession  the DAO
        * @param now  the current time
        * @param bean  the Hibernate bean
        * @return the resolved Hibernate bean
        */
        """
        pass
    
    def postPersistBean(self, context, secMasterSession, effectiveDate, bean):
        """
        /**
        * Additional persistence required after the main bean has been passed to Hibernate. Used with resolve to
        * @param context  the context
        * @param secMasterSession  the DAO
        * @param effectiveDate  the effective time
        * @param bean  the Hibernate bean
        * store data Hibernate alone can't deal with.
        */
        """
        pass