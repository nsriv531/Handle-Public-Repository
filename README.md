# Workshop

## Local Development Setup

### Code checkout and configuration
1. Checkout the code from GitHub: `git clone git@github.com:Handle-Software/workshop.git && cd workshop`
2. Make a local copy of the .env file: `cp ./conf/.env.dev .env`
3. Make a local copy of the local_settings.py file: `cp ./src/app/local_settings.template.py ./src/local_settings.py`

### Local Python installation
- Install PyEnv: https://github.com/pyenv/pyenv, https://realpython.com/intro-to-pyenv/
- Install Pip: `pip install --upgrade pip;`
- Install Pipenv: `pip install pipenv;`
- Activate the Python environment: run `pipenv shell` in the project root directory (same directory as Pipfile)
- Install Python Requirements `pip install -r ./src/requirements.txt`

### Local Node and NPM installation
- Install NVM for managing node environments and install `v20.5.0`
  - If fresh installing curl & nvm, don't use the snap package manager - it will cause issues with the nvm installation.
    - `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash`
    - `source ~/.bashrc`
    - `chmod -R 700 ~/.nvm`
    - `nvm install v20.5.0`
    - `nvm use v20.5.0`
    - `nvm alias default v20.5.0`
- Install these libraries globally:
  `npm install -g eslint` # https://eslint.org/
  `npm install -g standard` # https://standardjs.com/
- Install the javascript requirements by running `npm ci` in the same directory as the `package-lock.json` file (./src)

### Run development servers
- To run the Django development server, [runserver](https://docs.djangoproject.com/en/4.2/ref/django-admin/#runserver), which will auto-reload on any detected Python changes, run `./src/manage.py runserver`
    - May need to run `redis-server --daemonize yes` in console to localhost the redis server as a daemon. # https://pypi.org/project/django-redis/
- To run the [Vite](https://vitejs.dev/) frontend development server, which will handle hot reloading of javascript and SCSS and any configured plugins or frontend frameworks, run `cd ./src/static; npm run vite-dev`

## Next steps
* TODO: Instructions for containerized development.
* TODO: Instructions for production servers.
* TODO: Instructions for CI/CD with GitHub Actions.