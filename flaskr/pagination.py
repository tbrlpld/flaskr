from math import ceil


class Pagination(object):
    """Class to hold state of pagination"""

    def __init__(self, total_items, items_per_page, current_page):
        """
        Initialize Pagination object

        Pagination needs info about total number of items, items_per_page and
        the current page for initialization.

        If the `items_per_page` argument is not defined, the `ITEMS_PER_PAGE`
        setting is read from the current apps configuration.

        :param total_items: Total number of items which are being paginated.
        :type total_item: int

        :param items_per_page: Number of items which to display on one page.
        :type items_per_page: int

        :param current_page: Page number of the current page that is displayed
                             or requested.
        :type current_page: int
        """
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

    @property
    def item_offset(self):
        return (self.current_page - 1) * self.items_per_page
