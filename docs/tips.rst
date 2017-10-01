Recipes
=======

Adding a new language locally
-----------------------------

If you're translating a new language you'll need to translate the existing tg-react messages:

1. Make a new folder where you want to store the internationalization resources. Add this path to your LOCALE_PATHS setting.
2. Now create a subfolder for the language you want to translate. The folder should be named using locale name notation. For example: de, pt_BR, es_AR.
3. Now copy the base translations file from the tg-react source code into your translations folder.
4. Edit the django.po file you've just copied, translating all the messages.
5. Run manage.py compilemessages -l pt_BR to make the translations available for Django to use. You should see a message like processing file django.po in <...>/locale/pt_BR/LC_MESSAGES.
6. Restart your development server to see the changes take effect.

Changing the built-in translations
----------------------------------

Follow the process described in `Adding a new language locally`_ but instead of creating a new directory use the name of an
existing one.
