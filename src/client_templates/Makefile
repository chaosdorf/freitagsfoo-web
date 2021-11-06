all: Makefile

../static/templates/%.min.js: %.handlebars
	../../node_modules/.bin/handlebars $< --output $@ --min

../static/templates/%.js: %.handlebars
	../../node_modules/.bin/handlebars $< --output $@
