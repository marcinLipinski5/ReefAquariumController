del .coverage
rmdir /s /q %cd%\htmlcov
python -m coverage run -m unittest
python -m coverage report
python -m coverage html
