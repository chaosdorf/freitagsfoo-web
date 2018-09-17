all: ../static/templates/host_check.js ../static/templates/talks.js

../static/templates/%.js: %.handlebars
	../../node_modules/.bin/handlebars $< -f $@
