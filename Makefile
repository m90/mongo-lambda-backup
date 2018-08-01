test:
	@pytest

package: setup.py
	@rm -rf dist/
	@python setup.py sdist bdist_wheel

publish: package
	@twine upload dist/*

format:
	@black ./mongo_lambda_backup/.
