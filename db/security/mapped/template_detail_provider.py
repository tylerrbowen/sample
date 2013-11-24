from db.security.security_master_detail_provider import SecurityMasterDetailProvider
from utils.exceptions.portfolio_system_runtime_exception import PortfolioSystemRuntimeException
from operation_context import OperationContext


class TemplateSecurityMasterDetailProvider(SecurityMasterDetailProvider):
    """/**
     * Provides access to persist the full bean structure of the security.
     * This supports the default {@link DbSecurityMaster} implementations.
    """
    BEAN_OPERATIONS_BY_SECURITY = dict()
    BEAN_OPERATIONS_BY_BEAN = dict()
    BEAN_OPERATIONS_BY_TYPE = dict()
    
    def __init__(self, db_connector):
        """
        db_connector: DbConnector: The database connector.
        _operation_context: OperationContext: The operation context for management additional resources.
        """
        self._db_connector = db_connector
        self._operation_context = OperationContext()
    
    @classmethod
    def loadBeanOperation(cls, beanOperation):
        if beanOperation.getSecurityClass() in cls.BEAN_OPERATIONS_BY_SECURITY:
            raise PortfolioSystemRuntimeException(beanOperation.getSecurityClass() + " is already registered in BEAN_OPERATIONS_BY_SECURITY")
        cls.BEAN_OPERATIONS_BY_SECURITY[beanOperation.getSecurityClass()] = beanOperation
        if beanOperation.getBeanClass() in cls.BEAN_OPERATIONS_BY_SECURITY:
            raise PortfolioSystemRuntimeException(beanOperation.getBeanClass() + " is already registered in BEAN_OPERATIONS_BY_SECURITY")
        cls.BEAN_OPERATIONS_BY_SECURITY[beanOperation.getBeanClass()] = beanOperation
        if beanOperation.getSecurityType() in cls.BEAN_OPERATIONS_BY_SECURITY:
            raise PortfolioSystemRuntimeException(beanOperation.getSecurityType() + " is already registered in BEAN_OPERATIONS_BY_SECURITY")
        cls.BEAN_OPERATIONS_BY_SECURITY[beanOperation.getSecurityType()] = beanOperation
    
    @classmethod
    def getBeanOperation(cls, map, clazz):
        beanOperation = map.get(clazz)
        if beanOperation is not None:
            return beanOperation
        if clazz.getSuperclass() is None:
            return None
        beanOperation = cls.getBeanOperation(map, clazz.getSuperclass())
        if beanOperation is not None:
            map[clazz] = beanOperation
        return beanOperation
    
    @classmethod
    def getBeanOperation(cls, security):
        beanOperation = cls.getBeanOperation(cls.BEAN_OPERATIONS_BY_SECURITY, security.getClass())
        if beanOperation is None:
            raise PortfolioSystemRuntimeException("can't find BeanOperation for " + security.__str__())
        return beanOperation
    
    @classmethod
    def getBeanOperation(cls, operation_type):
        beanOperation = cls.BEAN_OPERATIONS_BY_TYPE.get(type.toUpperCase(Locale.ENGLISH))
        if beanOperation is None:
            if '_' in type:
                beanOperation = cls.BEAN_OPERATIONS_BY_TYPE.get(type.substring(type.indexOf('_') + 1))
            if type.__eq__("SWAPTION"):
                beanOperation = cls.BEAN_OPERATIONS_BY_TYPE.get("OPTION")
            if beanOperation is None:
                beanOperation = cls.BEAN_OPERATIONS_BY_TYPE.get("OPTION")
        return beanOperation
    
    loadBeanOperation(EquitySecurityBeanOperation.INSTANCE);
    loadBeanOperation(EquityOptionSecurityBeanOperation.INSTANCE);    
    
    def init(self, master):
        self._db_connector = master.getDbConnector()
        
    def getOperationContext(self):
        """
        /**
        * Gets the context for additional resources.
        * @return the context
        */
        """
        return self._operationContext

    
    def get_mapping_template(self):
        """
        /**
        * Gets the Hibernate Spring template.
        * @return the template
        */
        """
        return self._dbConnector.get_mapping_template()
    
    def get_dialect(self):
        """
        /**
        * Gets the database dialect.
        * @return the dialect
        */
        """
        return self.dbConnector.get_dialect()
    
    def get_template_master_session(self, session):
        """
        /**
        * Gets the session DAO.
        * @param session  the session
        * @return the DAO
        */
        """
        return TemplateSecurityMasterSession(session)
    
    def load_security_detail(self, base):
        pass
    
    def storeSecurityDetail(self, security):
        pass
    
    def extendSearch(self, request, args):
        pass
    
    # //-------------------------------------------------------------------------
    # @Override
    # public ManageableSecurity loadSecurityDetail(final ManageableSecurity base) {
    # s_logger.debug("loading detail for security {}", base.getUniqueId());
    # return getHibernateTemplate().execute(new HibernateCallback<ManageableSecurity>() {
      # @SuppressWarnings({"unchecked", "rawtypes" })
      # @Override
      # public ManageableSecurity doInHibernate(Session session) throws HibernateException, SQLException {
        # final SecurityBeanOperation beanOperation = getBeanOperation(base.getSecurityType());
        # HibernateSecurityMasterDao secMasterSession = getHibernateSecurityMasterSession(session);
        # SecurityBean security = secMasterSession.getSecurityBean(base, beanOperation);
        # if (security == null) {
          # s_logger.warn("no detail found for security {}", base.getUniqueId());
          # return base;
        # }
        # security = beanOperation.resolve(getOperationContext(), secMasterSession, null, security);
        # final ManageableSecurity result = (ManageableSecurity) beanOperation.createSecurity(getOperationContext(), security);
        # if (result == null) {
          # throw new IllegalStateException("Unable to convert security from database: " + base.getUniqueId() + " " + base.getSecurityType());
        # }
        # if (Objects.equal(base.getSecurityType(), result.getSecurityType()) == false) {
          # throw new IllegalStateException("Security type returned by Hibernate load does not match");
        # }
        # result.setUniqueId(base.getUniqueId());
        # result.setName(base.getName());
        # result.setExternalIdBundle(base.getExternalIdBundle());
        # result.setAttributes(base.getAttributes());
        # return result;
      # }
    # });
    # }

    # @Override
    # public void storeSecurityDetail(final ManageableSecurity security) {
    # s_logger.debug("storing detail for security {}", security.getUniqueId());
    # if (security.getClass() == ManageableSecurity.class) {
      # return;  // no detail to store
    # }
    # getHibernateTemplate().execute(new HibernateCallback<Object>() {
      # @SuppressWarnings({"unchecked", "rawtypes" })
      # @Override
      # public Object doInHibernate(final Session session) throws HibernateException, SQLException {
        # final HibernateSecurityMasterDao secMasterSession = getHibernateSecurityMasterSession(session);
        # final SecurityBeanOperation beanOperation = getBeanOperation(security);
        # final Date now = new Date();
        # final OperationContext operationContext = getOperationContext();
        # operationContext.setSession(session);
        # secMasterSession.createSecurityBean(operationContext, beanOperation, now, security);
        # return null;
      # }
    # });
    # }

    # @Override
    # public void extendSearch(SecuritySearchRequest request, DbMapSqlParameterSource args) {
    # if (request instanceof BondSecuritySearchRequest) {
      # BondSecuritySearchRequest bondRequest = (BondSecuritySearchRequest) request;
      # if (bondRequest.getIssuerName() != null || bondRequest.getIssuerType() != null) {
        # args.addValue("sql_search_bond_join", Boolean.TRUE);
      # }
      # if (bondRequest.getIssuerName() != null) {
        # args.addValue("bond_issuer_name", getDialect().sqlWildcardAdjustValue(bondRequest.getIssuerName()));
      # }
      # if (bondRequest.getIssuerType() != null) {
        # args.addValue("bond_issuer_type", getDialect().sqlWildcardAdjustValue(bondRequest.getIssuerName()));
      # }
    # }
    # }

    # }
