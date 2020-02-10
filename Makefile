# Makefile based on Nicholas Marcopoli and Austin Sura's makefile
SHELL := /bin/bash

install:
	python3 -m venv milestone1
	source milestone1/bin/activate && pip install -r requirements.txt

test:
	@echo Make sure you have installed first
	@echo You will have to wait until a game is found and then the bot will keep picking the safest pokemon to switch into
	source milestone1/bin/activate && python run.py

clean:
	rm -rf milestone1
