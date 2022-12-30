import os
import webbrowser

import click
from flask.cli import pass_script_info, show_server_banner, DispatchingApp, SeparatedPathType
from flask.helpers import get_debug_flag, get_env
from utils.config import Config


def is_port_in_use(host, port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


@click.command("run", short_help="Run a development server.")
@click.option(
    "--host", "-h",
    default=Config.HOST,
    required=not Config.HOST,
    callback=Config.validate_and_setup_host,
    help="The interface to bind to."
)
@click.option(
    "--port", "-p",
    default=Config.PORT,
    required=not Config.PORT,
    callback=Config.validate_and_setup_port,
    help="The port to bind to."
)
@click.option(
    "--aaz-path", '-a',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.AAZ_PATH,
    required=not Config.AAZ_PATH,
    callback=Config.validate_and_setup_aaz_path,
    expose_value=False,
    help="The local path of aaz repo."
)
@click.option(
    "--swagger-path", '-s',
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_PATH,
    callback=Config.validate_and_setup_swagger_path,
    expose_value=False,
    help="The local path of azure-rest-api-specs repo. Official repo is https://github.com/Azure/azure-rest-api-specs"
)
@click.option(
    "--swagger-module-path", "--sm",
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_MODULE_PATH,
    callback=Config.validate_and_setup_swagger_module_path,
    expose_value=False,
    help="The local path of swagger in module level. It can be substituted for --swagger-path."
)
@click.option(
    "--module", '-m',
    default=Config.DEFAULT_SWAGGER_MODULE,
    callback=Config.validate_and_setup_default_swagger_module,
    expose_value=False,
    help="The default swagger module. It is required when using --swagger-module-path."
)
@click.option(
    "--resource-provider", "--rp",
    default=Config.DEFAULT_RESOURCE_PROVIDER,
    callback=Config.validate_and_setup_default_resource_provider,
    expose_value=False,
    help="The default swagger resource provider."
)
@click.option(
    "--cli-path", '-c',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.CLI_PATH,
    required=not Config.CLI_PATH,
    callback=Config.validate_and_setup_cli_path,
    expose_value=False,
    help="The local path of azure-cli repo. Official repo is https://github.com/Azure/azure-cli"
)
@click.option(
    "--cli-extension-path", '-e',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.CLI_EXTENSION_PATH,
    required=not Config.CLI_EXTENSION_PATH,
    callback=Config.validate_and_setup_cli_extension_path,
    expose_value=False,
    help="The local path of azure-cli-extension repo. Official repo is https://github.com/Azure/azure-cli-extensions"
)
@click.option(
    "--workspaces-path", '-w',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.AAZ_DEV_WORKSPACE_FOLDER,
    required=not Config.AAZ_DEV_WORKSPACE_FOLDER,
    callback=Config.validate_and_setup_aaz_dev_workspace_folder,
    expose_value=False,
    help="The folder to load and save workspaces."
)
@click.option(
    "--reload/--no-reload",
    default=None,
    help="Enable or disable the reloader. By default the reloader "
         "is active if debug is enabled.",
)
@click.option(
    "--debugger/--no-debugger",
    default=None,
    help="Enable or disable the debugger. By default the debugger "
         "is active if debug is enabled.",
)
@click.option(
    "--eager-loading/--lazy-loading",
    default=None,
    help="Enable or disable eager loading. By default eager "
         "loading is enabled if the reloader is disabled.",
)
@click.option(
    "--with-threads/--without-threads",
    default=True,
    help="Enable or disable multithreading.",
)
@click.option(
    "--extra-files",
    default=None,
    type=SeparatedPathType(),
    help=(
            "Extra files that trigger a reload on change. Multiple paths"
            f" are separated by {os.path.pathsep!r}."
    ),
)
@click.option(
    "--quiet", '-q',
    is_flag=True,
    default=False,
    is_eager=True,
    help="Without open web browser page."
)
@pass_script_info
def run_command(
        info, host, port, reload, debugger, eager_loading, with_threads, extra_files, quiet
):
    """Run a local development server.

    This server is for development purposes only. It does not provide
    the stability, security, or performance of production WSGI servers.

    The reloader and debugger are enabled by default if
    FLASK_ENV=development or FLASK_DEBUG=1.
    """
    debug = get_debug_flag()

    if reload is None:
        reload = debug

    if debugger is None:
        debugger = debug

    show_server_banner(get_env(), debug, info.app_import_path, eager_loading)
    app = DispatchingApp(info.load_app, use_eager_loading=eager_loading)

    if is_port_in_use(host, port):
        raise ValueError(f"The port '{port}' already been used in '{host}', please specify a new port in '--port' argument.")

    from werkzeug.serving import run_simple

    if quiet:
        print(f'Please open http://{host}:{port}/')
    else:
        webbrowser.open_new(f'http://{host}:{port}/')

    run_simple(
        host,
        port,
        app,
        use_reloader=reload,
        use_debugger=debugger,
        threaded=with_threads,
        extra_files=extra_files,
    )
