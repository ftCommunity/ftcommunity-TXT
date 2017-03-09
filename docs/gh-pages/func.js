var Builder = {

	addBlock: function(block) {
	
		var outer = document.createElement('DIV');
		outer.className = 'blockDesc';
		
		var imgs = document.createElement('DIV');
		imgs.className = 'images';
		
		var title = document.createElement('DIV');
		title.className = 'title';
		
		var langCode = Lang.getCode();
		imgs.appendChild(this.getImg(langCode, block));
		
		var text = document.createElement('DIV');
		text.className = 'text';
		text.innerHTML = Lang.get(block);
		
		
		outer.appendChild(imgs);
		outer.appendChild(text);
		var blockDescs = document.getElementById('blockDescs');
		blockDescs.appendChild(title);
		blockDescs.appendChild(outer);
	
	},
	
	setText: function(what, objID) {
		document.getElementById(objID).innerHTML = Lang.get(what);
	},

	getImg: function(lang, block) {
		var img = document.createElement('IMG');
		img.src=('www/' + lang + '/' + block + '.png');
		img.className = 'img';
		return img;
	},
	

};