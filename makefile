build-layer:
	mkdir -p "layer/python"
	python -m pip install -r ./scraper/requirements.txt -t "layer/python"
