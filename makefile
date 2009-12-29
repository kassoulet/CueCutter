cuecutter: cuecutter.py cuecutter-plain.svg
	python build.py
	
install: cuecutter
	install cuecutter /usr/local/bin
	install cuecutter.desktop /usr/share/applications
