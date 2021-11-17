# Creating translations

This folder is preserved for translations for the generated aqstat plots.

To create or update the main `aqstat.pot` file, run Python's `pygettext.py` script,
located at `<python dir>\Tools\i18n\pygettext.py`. For example:

```
python c:\Users\ubi\AppData\Local\Programs\Python\Python39\Tools\i18n\pygettext.py --no-location -d aqstat ..\.
```

To edit translations, use e.g. [Poedit](https://poedit.net/).