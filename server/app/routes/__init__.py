"""Register all API blueprints with proper URL prefix ordering.

Blueprints are registered from most specific to most general to ensure
correct route matching. The catch-all <path:path> in misc_bp is last.
"""

from flask import Flask


def register_blueprints(app: Flask):
    # Auth & user endpoints
    from app.routes.auth import auth_bp
    from app.routes.save import save_bp
    from app.routes.economy import economy_bp
    from app.routes.rank import rank_bp
    from app.routes.union import union_bp
    from app.routes.exchange import exchange_bp
    from app.routes.amf_utils import amf_bp

    # Thrift & mall stubs
    from app.routes.thrift_routes import thrift_bp
    from app.routes.mall_routes import mall_bp

    # Misc (must be last — contains /<path:path> catch-all)
    from app.routes.misc import misc_bp

    # Register all
    app.register_blueprint(auth_bp)
    app.register_blueprint(save_bp)
    app.register_blueprint(economy_bp)
    app.register_blueprint(rank_bp)
    app.register_blueprint(union_bp)
    app.register_blueprint(exchange_bp)
    app.register_blueprint(amf_bp)
    app.register_blueprint(thrift_bp)
    app.register_blueprint(mall_bp)
    app.register_blueprint(misc_bp)
