.PHONY: build deploy-test deploy

build: setup.cfg
	python3 -m build

deploy-test: setup.cfg
	python3 -m twine upload --repository testpypi dist/* -u "__token__" -p $(shell cat token-test)


deploy: setup.cfg
	python3 -m twine upload --repository pypi dist/* -u "__token__" -p $(shell cat token)


