

class Pagination(object):
    """Class to hold state of pagination"""

    def __init__(self, total_items, items_per_page, current_page):
        super(Pagination, self).__init__()
        self.total_items = total_items
        self.items_per_page = items_per_page
        self.current_page = current_page

    @property
    def has_previous(self):
        return self.current_page > 1
