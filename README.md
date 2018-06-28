# GVX admin

GenVarXplorer administration interface.

Manage:

- users
- protocols (projects)
- templates and configuration files

## Requirements

- Python >= 3.5
- Python libs:

```bash
pip install -r requirements.txt
```

## Installations

- Install [JSON editor](https://github.com/josdejong/jsoneditor):

```bash
npm init
```

Default prompts can be accepted.

```bash
npm install jsoneditor
```

### Get alternate version of JSONeditor

The Release v5.18.0 has a bug [JSON editor](https://github.com/josdejong/jsoneditor/issues/544).

To get version in developpement we can install JSONeditor with:

```bash
npm install https://github.com/josdejong/jsoneditor.git#develop
```

## Configuration

Configure options in a *gvx_admin.cfg* by setting options as declared in the *BaseConfig* class of the *gvx_admin.py* file.

```python
DEBUG = False
PORT = 5000
HOST = "localhost"
SECRET_KEY = '123456789'
SQLALCHEMY_DATABASE_URI = 'sqlite:///gvx_users.sqlite'
SQLALCHEMY_ECHO = True
SQLALCHEMY_BINDS = {
    'samples': 'sqlite:///gvx_samples_catalog.sqlite'
}
HTML_TEMPLATE_PATH = ''
JSON_CONFIG_PATH = ''
BAM_FILES_PATH = ''
EXPORT_PATH = ''
LINKED_DATA_PATH = ''
HTML_DATA_TYPES = (
    'qc',
    'var',
    'cst',
    'cnv',
    'fus'
)
DEFAULT_CONFIG_SRC = [
    ("", ""),
    ("default", "default")
]
DEFAULT_TEMPLATE_SRC = [
    ("", ""),
    ("default", "default")
]
PROTOCOLS_DB_PATH = 'sqlite:///{table_name}.sqlite'
```

## Usage

```bash
python gvxadmin.py
```

Then go the web interface url (edit according to your configuration file)

    http://localhost:5000/admin


