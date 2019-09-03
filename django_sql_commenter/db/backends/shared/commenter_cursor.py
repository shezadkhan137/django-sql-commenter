# -*- coding: utf-8 -*-
import StringIO
import logging

from contextlib import contextmanager
from django.utils.encoding import smart_unicode

logger = logging.getLogger(__name__)


class CommentCursorWrapper(object):

    def __init__(self, commenters, cursor, *args, **kwargs):
        self._commenters = commenters or []
        self.cursor = cursor

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # Close instead of passing through to avoid backend-specific behavior
        # (#17671).
        self.close()

    @contextmanager
    def _comment_generator(self):
        comment_builder = StringIO.StringIO()
        comment_builder.write('\n\n/* TRACE INFO \n')
        try:
            yield comment_builder
        except Exception as e:
            logger.exception(e)
        finally:
            comment_builder.write('\n*/')

    def _formatter(self, comment_map):
        comment_list = []
        for key, value in comment_map.iteritems():
            comment_list.append('{key}={value} '.format(
                key=key,
                value=value,
            ))
        return '\n'.join(comment_list)

    def _get_comment(self):
        if not self._commenters:
            return ''

        with self._comment_generator() as comment:
            for commenter in self._commenters:
                comment.write(self._formatter(commenter()))

        return smart_unicode(comment.getvalue())

    def execute(self, query, args=None):
        comment = self._get_comment()
        query = query + comment
        return super(CommentCursorWrapper, self).execute(query, args)

    def executemany(self, query, args):
        comment = self._get_comment()
        query = query + comment
        return super(CommentCursorWrapper, self).executemany(query, args)
