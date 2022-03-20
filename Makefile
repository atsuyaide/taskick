PACKAGE = taskick
VERSION = 0.1.4

.PHONY: build-package
build-package: ## Generate setup.py by poetry command for shared package
	poetry build
	tar zxvf dist/$(PACKAGE)-${VERSION}.tar.gz -C ./dist
	cp dist/$(PACKAGE)-${VERSION}/setup.py setup.py
	rm -rf dist
