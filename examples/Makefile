
main.pdf: main.tex generated.tex
	latexmk -xelatex -pdf main.tex

generated.tex: test.coltex
	kwpp coltex.py > generated.tex

clean:
	latexmk -C
