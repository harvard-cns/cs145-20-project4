all: 
	cd src; $(MAKE); cd ..;
	rm -rf bin
	mkdir bin
	cp src/client bin/tg-client
	cp src/server bin/tg-server

clean: 
	cd src; $(MAKE) clean; cd ..;
	rm -rf bin

