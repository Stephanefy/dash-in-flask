import dash
import dash_bootstrap_components as dbc

from flask import Flask
from flask_moment import Moment
from flask.helpers import get_root_path
from flask_login import login_required
from flask_assets import Environment, Bundle

from config import Config



def create_app():
    server = Flask(__name__,instance_relative_config=False)
    assets = Environment(server)
    moment = Moment(server)
    server.config.from_object(Config)


    style_bundle = Bundle(
    'src/less/*.less',
    filters='less,cssmin',
    output='dist/css/style.min.css',
    extra={'rel': 'stylesheet/css'}
    )

    js_bundle = Bundle(
    'src/js/main.js',
    filters='jsmin',
    output='dist/js/main.min.js'
)   

    assets.register('main_styles', style_bundle)  # Register style bundle
    assets.register('main_js', js_bundle) # Register JS bundle
    style_bundle.build()  # Build LESS styles
    js_bundle.build() #build js

    from app.dashapp1.layout import layout as layout1
    from app.dashapp1.callbacks import register_callbacks as register_callbacks1
    register_dashapp(server, 'Tableau de bord dynamique', 'dashboard', layout1, register_callbacks1)

    from app.dashapp2.layout import layout as layout2
    from app.dashapp2.callbacks import register_callbacks as register_callbacks2
    register_dashapp(server, 'Analyse des données', 'analyse', layout2, register_callbacks2)


    register_extensions(server)
    register_blueprints(server)

    return server


def register_dashapp(app, title, base_pathname, layout, register_callbacks_fun):
    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
    external_stylesheets=[dbc.themes.BOOTSTRAP,"/static/css/dashboard/main.css","/static/css/dashboard/header.css"]



    my_dashapp = dash.Dash(__name__,
                           server=app,
                           url_base_pathname=f'/{base_pathname}/',
                           assets_folder=get_root_path(__name__) + f'/{base_pathname}/assets/',
                           meta_tags=[meta_viewport],
                           external_stylesheets=external_stylesheets,
                           update_title= 'chargement...')
    # Push an application context so we can use Flask's 'current_app'
    with app.app_context():
        my_dashapp.index_string ='''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
            </head>
            <body>
                <header class="template-header">
                    <nav class="nav">
                        <div class="logo-wrapper">
                        <a href="/"><img class="logo" src="/static/img/logo-agensit.png" alt="logo"></a>
                        </div>
                        <div class="nav-items">
                        <a href="/" class="link">Retourner à l'accueil</a>
                    </nav>
                </header>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
        my_dashapp.title = title
        my_dashapp.layout = layout
        register_callbacks_fun(my_dashapp)
    _protect_dashviews(my_dashapp)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(dashapp.server.view_functions[view_func])


def register_extensions(server):
    from app.extensions import db
    from app.extensions import login
    from app.extensions import migrate

    db.init_app(server)
    login.init_app(server)
    login.login_view = 'main.login'
    migrate.init_app(server, db)


def register_blueprints(server):
    from app.webapp import server_bp

    server.register_blueprint(server_bp)
