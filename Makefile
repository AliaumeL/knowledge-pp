
main.pdf: main.tex generated.tex
	latexmk -xelatex -pdf main.tex

generated.tex: test.coltex
	python3 coltex.py > generated.tex

clean:
	latexmk -C
