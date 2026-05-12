from flask import Blueprint

def register_routes(app):
    from .auth_routes import auth_bp
    from .member_routes import member_bp
    from .trainer_routes import trainer_bp
    from .class_routes import class_bp
    from .event_routes import event_bp
    from .facility_routes import facility_bp
    from .plan_routes import plan_bp
    from .billing_routes import billing_bp
    from .dashboard_routes import dashboard_bp
    from .user_routes import user_bp
    from .report_routes import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(trainer_bp)
    app.register_blueprint(class_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(facility_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
