---
nav-title: Internationalization
nav-pos: 4
---
# Internationalization of Apps (I18n)

## I18n for users

If you are a user and you miss support for your language then you can help us. First you need to make sure that
the language you are interested in is supported by the firmwares language tool. Currently supported are english, 
german, french and dutch. Please contact the developers if you'd like to see support for another language.

If your language is supported then you need to make sure that the app in question already supports multiple languages. To do so you need to take a look at the apps repository. E.g.
in case of the calculator app ```calc``` you need to look at:

https://github.com/ftCommunity/ftcommunity-apps/tree/master/packages/calc

Look out of files named ```<app>_XX.ts``` and ```<app>_XX.qm```. If these are present then the app itself already supports
translations. In case of the calculator there are e.g. ```calc_de.ts``` and ```calc_de.qm``` which are the german translations
of the app. If no such files are present then the app is not prepared for translations yet and you need to contact the app developer before you can proceed.

If the app is prepared for translation you can now take the ```calc_de.ts``` file and rename the language indicator to match your language (currently de for german, nl for dutch and fr for french). If you e.g. want to translate the calculator to dutch then rename ```calc_de.ts``` to ```calc_nl.ts```.

Now open that file in [linguist](https://code.google.com/archive/p/qtlinguistdownload/downloads). Go to settings and change the target language to your language. Finally use linguist to translate all the strings. Please try to keep strings the same length to make sure the translated strings still fit onto the screen.

Finally use a text editor to modify the ```manifest``` file. Add a new section for your language (e.g. [nl] for dutch) and create additional entries for the app name and the app description in your language.

Once you are done send the resulting ```<app>_XX.ts``` file and the modified ```manifest``` to the app developer. You can usually find the
email in the ```manifest``` file. The developer will then release a new version of his app including your
translations.

You might even test the new translations yourself as described below.

## I18n for app developers

PyQt and Qt provide mechanisms and tools for i18n of Qt and PyQt
applications. Some information about this can be found in the [PyQt documentation](http://pyqt.sourceforge.net/Docs/PyQt4/i18n.html).

On a Ubuntu Linux the necessary tools can be installed using the
following command:

```
sudo apt-get install pyqt4-dev-tools qt4-linguist-tools qt4-dev-tools
```

Windows versions of these tools are [also available](https://www.linux-apps.com/content/show.php/Qt+Linguist+Download?content=89360).

### Marking strings for translation

There are several ways of marking strings inside a PyQt application for
translation. The preferred way is to use ```QCoreApplication.translate()```. It's simply wrapped around any string that is going to be translated.

E.g.

```
function("some english string")
```

becomes

```
function(QCoreApplication.translate("context","some english string"))
```

"context" can be any string. Usually the function or class name containing
the string is being used. This helps to distinguish between different
occurances of the same string which may be translated differently in
a varying context. It is recommended to use english plain text as the
default texts. That way the application will be usable even if the
translation mechanism fails or the necessary files aren't present at all.

Once all strings are marked that way the ```pylupdate4``` tool is used
to extract them into a file. Assuming a german translation (usually
marked by 'de') is to be written for the about applications main
source file ```about.py``` the following command should be used:

```
pylupdate4 about.py -ts about_de.ts
```

The resulting xml file ```about_de.ts``` contains all the strings for
translation. This file can then be opened with the ```linguist```
application:

```
linguist about_de.ts
```

This is a powerful tool for handling translations. When run on a freshly
generated ```.ts``` file it will ask you for the source and target
languages. The source language will be english and the target language
is the one of the desired translation. In this case "german".

Now use linguist to do all the translations.

Once all translations are done the following command will convert them
in a smaller binary file:

```
lrelease about_de.ts
```

The resulting file is named ```about_de.qm``` and should be distributed with
the application itself in the same directory as the file containing the
source strings.

The application itself needs to load the appropriate translation file.
This can usually be achieved by placing the following lines right
after the QApplication instance is generated.

```
translator = QTranslator()
path = os.path.dirname(os.path.realpath(__file__))
translator.load(QLocale.system(), os.path.join(path, "about_"))
self.installTranslator(translator)
```

See e.g. the [```about```](https://github.com/ftCommunity/ftcommunity-TXT/tree/master/board/fischertechnik/TXT/rootfs/opt/ftc/apps/system/about) as an example.

## Modifying the manifest

The app name being displayed in the launcher can also be translated. A
language specific section can be added containing these. E.g. the following
lines can be appended to the about apps manifest for a german name and
a german description:

```
[de]
name: Über
desc: Über die Community-Firmware
```

Don't translate the category! This will be translated inside the launcher
automatically. Plase choose one of the following categories to allow for
automatic translation:

 * System
 * Models
 * Tools
 * Demos

Other categories will be ignored and the app will only show up in the 
"All" category only.

## Testing

The translation can be tested on a PC using the ```LC_ALL``` enviroment
variable. E.g.

```
export LC_ALL=de_DE.UTF-8
```

should cause the german translation to be used. Removing ```LC_ALL``` or
setting it to en_US should make the original english texts to appear again.

