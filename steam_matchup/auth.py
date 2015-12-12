import urlparse

from pyramid.httpexceptions import HTTPTemporaryRedirect


def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """

    config.add_route('auth: openid', '/')
    from pyramid_openid import verify_openid
    config.add_view(route_name='auth: openid', view=verify_openid)


def on_success(context, request, openid_data):
    identity_url = openid_data['identity_url']
    url_parts = urlparse.urlparse(identity_url)

    response = HTTPTemporaryRedirect('/')
    response.set_cookie(
        'profile_id', url_parts.path.split('/')[-1],
    )

    return response
