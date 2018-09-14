all: ../static/templates/host_check.js

../static/templates/%.js: %.handlebars
	handlebars $< -f $@
