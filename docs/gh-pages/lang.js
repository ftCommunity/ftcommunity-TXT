function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}

var Lang = {
    
    getCode: function() {
	return (getURLParameter('lang') || navigator.language || navigator.userLanguage).substr(0,2);
    },
    
    get: function(what) {
	var langCode = this.getCode();
	var translations = this[langCode];					// requested translations
	if (!translations) { translations = this['en']; }	// fallback
	var tmp = translations[what];

	tmp = tmp.replace(/{TXT}/g, '<a href="http://www.fischertechnik.de/desktopdefault.aspx/tabid-21/39_read-309/usetemplate-2_column_pano//"><b>fischertechnik TXT</b></a>');
	tmp = tmp.replace(/{CFW}/g, (langCode == "de")?'<b>Community-Firmware</b>':'<b>community firmware</b>');
	tmp = tmp.replace(/{RP424}/g, '<a href="http://www.fischertechnik.de/ResourceImage.aspx?raid=10274">RoboPro Version 4.2.4</a>');
        tmp = tmp.replace(/{ZIPLATEST}/g, 'https://github.com/ftCommunity/ftcommunity-TXT/releases/download/v0.9.2/ftcommunity-txt-0.9.2.zip');
	return tmp;
    },
    
    de: {
	about:		'Was ist das?',
	aboutText:	"<p>Die {CFW} ist ein freies und modernes Betriebssystem für Deinen {TXT}. " +
                        "Stark erweiterte Internet-Fähigkeiten inklusive eigenem App-Store " +
                        "sowie die Steuerung und Programmierung von Modellen über PC, Tablet " +
                        "oder Smartphone machen Deinen TXT fit für die Zukunft.</p>" +
                        "<p>Und das beste: Du musst Deinen TXT dafür nicht öffnen oder verändern, " +
                        "denn die {CFW} wird auf SD-Karte installiert und kann so jederzeit wieder "+
                        "entfernt werden.</p>",
	
	howto:		'So einfach geht es!',
	howtoText:	"Du brauchst:" +
                        "<ul>" +
                        "<li>Deinen {TXT}</li>" +
                        "<li>eine Micro-SD-Karte mit mindestens 2GB Kapazität</li>" +
                        "</ul>" +
                        "Die Installation erfolgt in vier einfachen Schritten:"+
                        "<ol>" +
                        '<li>Stelle sicher, dass Du mindestens {RP424} verwendest</li>' +
                        '<li>Schalte den Bootloader Deines TXT entsprechend der <a href="http://www.fischertechnik.de/ResourceImage.aspx?raid=10278">offiziellen fischertechnik-Anleitung</a> frei</li>' +
                        '<li>Kopiere den Inhalt des <a href="{ZIPLATEST}">Community-Firmware-ZIP-Archivs</a> auf Deine SD-Karte</li>' +
                        '<li>Stecke die SD-Karte in Deinen TXT und schalte ihn ein!</li>' +
                        '</ol>' +
	                'Weitere Informationen findest Du <a href="https://github.com/ftCommunity/ftcommunity-TXT/wiki/%5BDE%5D-Anleitung%3A-Einrichtung-der-ftcommunity-TXT-Firmware">in unserem Wiki</a> ' +
	                'und im <a href="https://forum.ftcommunity.de/viewforum.php?f=33">fischertechnik community forum</a>.'
    },
    
    en: {
	about:		'What is this?',
	aboutText:	"<p>The {CFW} is a free and modern operating system for your {TXT}. " +
                        "Heavily extended internet connectivity including an own app store " +
                        "as well as the ability to control and program models via PC, tablet " +
                        "or smart phone make your TXT fit for the future.</p>" +
                        "<p>And best of all: You don't even have to open or modify your TXT for this " +
                        "because the {CFW} is installed onto sd card and can that way be removed " +
                        "at any time.</p>",
	
	howto:		"It's so simple!",
	howtoText:	"You need:" +
                        "<ul>" +
                        "<li>your {TXT}</li>" +
                        "<li>a micro sd card with at least 2GB capacity</li>" +
                        "</ul>" +
                        "The installation happens in four simple steps:"+
                        "<ol>" +
                        '<li>Make sure that you are running at least {RP424}</li>' +
                        '<li>Enable the bootloader of your TXT by following the <a href="http://www.fischertechnik.de/ResourceImage.aspx?raid=10278">official fischertechnik instructions</a> (english version needed!)</li>' +
                        '<li>Copy the contents of the<a href="{ZIPLATEST}">community firmware ZIP archive</a> onto your sd card</li>' +
                        '<li>Insert the sd card into your TXT and switch it on!</li>' +
                        '</ol>' +
	                'More information can be found <a href="https://github.com/ftCommunity/ftcommunity-TXT/wiki/%5BEN%5D-Tutorial%3A-Setting-up-the-ftcommunity-TXT-Firmware">in our wiki</a> ' +
	                'and in the <a href="https://forum.ftcommunity.de/viewforum.php?f=33">fischertechnik community forum</a>.'
    },
    
}
