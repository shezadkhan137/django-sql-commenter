from functools import partial
from django.utils.module_loading import import_string


def get_commenters(config):

    enabled_commenters = []

    for commenter_import_path, kwargs in config.iteritems():
        commenter = import_string(commenter_import_path)
        enabled_commenters.append(
            partial(commenter, **kwargs),
        )

    return enabled_commenters
