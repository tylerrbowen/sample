from position.postion_source import PositionSource
from portfolio.portfolio_node_base import SimplePortfolioNode
from portfolio.portfolio_base import SimplePortfolio
from position.manageable.position_search_request import PositionSearchRequest
from source.change_manager_base import PassthroughChangeManager
from source.change_manager_base import DummyChangeManager


class AbstractMasterPositionSource(PositionSource):
    def __init__(self,
                 portfolio_master):
        super(AbstractMasterPositionSource, self).__init__()
        self._portfollio_master = portfolio_master

    def positions(self, position_search):
        pass

    def change_providers(self):
        pass

    def change_manager(self):
        change_providers = self.change_providers()
        if not change_providers:
            return PassthroughChangeManager(self.change_providers())
        else:
            return DummyChangeManager.INSTANCE()

    def get_portfolio(self,
                      unique_id,
                      version_correction):
        man_prt = self.get_portfolio_master().get(unique_id).get_portfolio()
        prt = SimplePortfolio(man_prt.get_unique_id(), man_prt.get_name())
        self.convert_node(man_prt.get_root_node(), prt.get_root_node(), version_correction)
        self.copy_attributes(man_prt, prt)

    def convert_node(self, man_node, source_node, version_correction):
        position_search = PositionSearchRequest()
        position_cache = dict()
        position_count = self.populate_position_search_request(position_search, man_node)
        if position_count > 0:
            position_search.set_version_correction(version_correction)
            positions = self.positions(position_search)
            if positions:
                for position in positions:
                    position_cache[position.get_unique_id().get_object_id()] = position
        else:
            position_cache = None
        self.convert_node(man_node, source_node, position_cache)

    def copy_attributes(self, man_prt, prt):
        if man_prt.get_attributes():
            for key, value in man_prt.get_attributes().iteritems():
                prt.add_attribute(key, value)

    def populate_position_search_request(self, position_search, node):
        count = 0
        for position_id in node.get_position_ids():
            position_search.add_position_object_id(position_id)
            count += 1
        for child in node.get_child_nodes():
            count += self.populate_position_search_request(position_search, child)
        return count

    def convert_node(self, man_node, source_node, position_cache):
        node_id = man_node.get_unique_id()
        source_node.set_unique_id(node_id)
        source_node.set_name(man_node.get_name())
        source_node.set_parent_node_id(man_node.get_parent_node_id())
        if len(man_node.get_position_ids()) > 0:
            for position_id in man_node.get_position_ids():
                found_position = position_cache.get(position_id)
                if not found_position:
                    source_node.add_position(found_position)
                else:
                    print 'Position {} not found'
        for child in man_node.get_child_nodes():
            child_node = SimplePortfolioNode()
            self.convert_node(child, child_node, position_cache)
            source_node.add_child_node(child_node)

    def get_portfolio(self, object_id, version_correction):
        man_prt = self.get_portfolio_master().get(object_id, version_correction).get_portfolio()
        prt = SimplePortfolio(man_prt.get_unique_id(), man_prt.get_name())
        self.convert_node(man_prt.get_root_node(), prt.get_root_node(), version_correction)
        self.copy_attributes(man_prt, prt)
        return prt

    def get_portfolio_node(self, unique_id, version_correction):
        man_node = self.get_portfolio_master().get_node(unique_id)
        if not man_node:
            raise Exception
        node = SimplePortfolioNode()
        self.convert_node(man_node, node, version_correction)
        return node

    def get_portfolio_master(self):
        return self._portfollio_master






