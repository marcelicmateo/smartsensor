all: ads1256_test clean

ads1256_test:ads1256_test.o
	gcc ads1256_test.c -o ads1256_test -lbcm2835


.PHONY: clean
clean:
	rm ads1256_test.o

