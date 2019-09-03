# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.backends.dummy import base

from django_sql_commenter.db.backends.shared import (
    CommentCursorWrapper,
    get_commenters
)


class DatabaseWrapper(base.DatabaseWrapper):

    def create_cursor(self, name=None):
        cursor = super(DatabaseWrapper, self).create_cursor(name)
        return CommentCursorWrapper(
            get_commenters(settings.SQL_COMMENTER_CONFIG),
            cursor,
        )
