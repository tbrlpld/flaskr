from math import ceil


class Pagination(object):
    """Class to hold state of pagination"""

    def __init__(self, total_items, items_per_page, current_page):
        """
        Initialize Pagination object

        Pagination needs info about total number of items, items_per_page and
        the current page for initialization.

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
        """Return total number or pages"""
        return ceil(self.total_items / self.items_per_page)

    @property
    def has_previous(self):
        """Check if the current page has a previous page"""
        return self.current_page > 1

    @property
    def previous(self):
        """Return page number of the previous page"""
        if self.has_previous:
            return self.current_page - 1
        return None

    @property
    def has_next(self):
        """Check if the current page has a next page"""
        return self.current_page < self.total_pages

    @property
    def next(self):
        """Return page number of the current page"""
        if self.has_next:
            return self.current_page + 1
        return None

    @property
    def item_offset(self):
        """
        Return offset for grabbing items

        Depending on the current page, the items displayed do not start with
        the first item in the item set. The number of items to skip in the set
        is returned by this method.

        The items are assumed to be indexed from 1. E.g. if the current page is
        2 and there are 5 items per page, the first five should be skipped.
        The returned offset in that case would be 5.
        """
        return (self.current_page - 1) * self.items_per_page
