SHELL := /bin/bash

# Referenced from Nicholas Marcopoli and Austin Sura
install: .installed

test: .installed
	source milestone2/bin/activate && python run.py

build: .installed
	@echo To watch the bot play, go to https://play.pokemonshowdown.com/
	@echo and log in as the user \"totallynotabottt\" with password \"notabot\"
	@echo Otherwise, you can just watch the bot play from the terminal.
	@echo -e "\n"
	@read -n1 -r -p "Press any key to continue running the bot..."
	source milestone2/bin/activate && python run.py

clean:
	rm -rf milestone2

.installed:
	python3 -m venv milestone2
	source milestone2/bin/activate && pip install -r requirements.txt
	@echo "installed" > .installed

.PHONY: install test build clean
