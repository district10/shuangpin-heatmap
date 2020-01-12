all:
	@echo nothing special

lint:
	yapf -ir .

prepare:
	python3 -m pip install -r requirements.txt

update_svgs:
	python3 shuangpin_heatmap.py --dump-all-shuangpin-layout 1 --use-dvorak 0 --output-directory svgs/qwerty
	python3 shuangpin_heatmap.py --dump-all-shuangpin-layout 1 --use-dvorak 1 --output-directory svgs/dvorak
