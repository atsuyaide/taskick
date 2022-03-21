PACKAGE = taskick

.PHONY: build-package
build-package: ## Generate setup.py by poetry command for shared package
	rm -rf dist
	poetry build
	tar zxvf dist/$(PACKAGE)-*.tar.gz -C ./dist
	cp dist/$(PACKAGE)-*/setup.py setup.py
	rm -rf dist
