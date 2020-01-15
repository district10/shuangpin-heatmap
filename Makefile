all:
	@echo nothing special

lint:
	yapf -ir .

prepare:
	python3 -m pip install -r requirements.txt

update_svgs:
	python3 shuangpin_heatmap.py --dump-all-shuangpin-layout 1 --use-dvorak 0 --output-directory svgs/qwerty
	python3 shuangpin_heatmap.py --dump-all-shuangpin-layout 1 --use-dvorak 1 --output-directory svgs/dvorak

INPUT_TEXT ?= data/sample2.txt
update_heatmaps:
	python3 shuangpin_heatmap.py \
		--heatmap-mode 1 \
		--output-directory heatmaps < $(INPUT_TEXT)
test:
	python3 shuangpin_heatmap.py \
		--heatmap-mode 1 \
		--use-dvorak 1 \
		< $(INPUT_TEXT)
