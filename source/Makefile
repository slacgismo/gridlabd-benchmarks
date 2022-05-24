# Makefile

ica_test.csv: $(shell ls R*.glm) Makefile ica_test.py
	python3 ica_test.py

clean:
	rm -f R[1-5]-{12470,25000,35000}-[1-5].{csv,json}
