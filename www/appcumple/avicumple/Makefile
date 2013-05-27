
all: _filtro.so

filtro_wrap.c : filtro.i
	swig -python filtro.i

filtro_wrap.o : filtro_wrap.c
	gcc -fPIC -lMagickWand -lMagickCore -I /usr/include/ImageMagick/  -c filtro.c filtro_wrap.c -I /usr/include/python2.7/

_filtro.so : filtro_wrap.o
	gcc -shared filtro.o filtro_wrap.o -lMagickWand -lMagickCore -I /usr/include/ImageMagick/ -Xlinker -rpath /usr/lib -o _filtro.so

clean:
	rm filtro_wrap.c *.o *.so
