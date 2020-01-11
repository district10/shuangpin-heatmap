all:
	@echo nothing special

lint:
	yapf -ir .

prepare:
	python3 -m pip install -r requirements.txt
