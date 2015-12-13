from pyramid.config import Configurator


def main(global_config, **settings):
    settings.update(global_config)
    config = Configurator(
            settings=settings,
    )

    config.include('.api', route_prefix='/api')
    config.include('.auth', route_prefix='/auth')

    _static_routes(config)

    _session(config)

    app = config.make_wsgi_app()
    return app


def _static_routes(config):
    from pyramid.static import static_view
    config.add_route('catchall_static', '/*subpath')
    config.add_view(
            route_name='catchall_static',
            view=static_view('steam_matchup:static/angular', use_subpath=True),
    )


def _session(config):
    from pyramid.session import SignedCookieSessionFactory
    session_factory = SignedCookieSessionFactory('sup3rs3cr3t')
    config.set_session_factory(session_factory)

