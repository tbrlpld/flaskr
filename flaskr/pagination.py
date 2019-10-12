from math import ceil


class Pagination(object):
    """Class to hold state of pagination"""

    def __init__(self, total_items, items_per_page, current_page):
        super(Pagination, self).__init__()
        self.total_items = total_items
        self.items_per_page = items_per_page
        self.current_page = current_page

    @property
    def total_pages(self):
        return ceil(self.total_items / self.items_per_page)

    @property
    def has_previous(self):
        return self.current_page > 1

    @property
    def previous(self):
        if self.has_previous:
            return self.current_page - 1
        return None

    @property
    def has_next(self):
        return self.current_page < self.total_pages

    @property
    def next(self):
        if self.has_next:
            return self.current_page + 1
        return None
