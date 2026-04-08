from flask import Flask


def create_app():
    app = Flask(__name__)

    from routes.home import home_bp
    from routes.timeline import timeline_bp
    from routes.projects import projects_bp
    from routes.sunsets import sunsets_bp
    from routes.books import books_bp
    from routes.hobbies import hobbies_bp
    from routes.family import family_bp
    from routes.contact import contact_bp
    from routes.settings import settings_bp
    from routes.visits import visits_bp
    from routes.api import api_bp
    from routes.puzzle import puzzle_bp
    from routes.skills import skills_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(sunsets_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(hobbies_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(visits_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(puzzle_bp)
    app.register_blueprint(skills_bp)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
