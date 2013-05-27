#include <stdio.h>
#include <stdlib.h>
#include <wand/MagickWand.h>

//compilar con:
//cc `MagickWand-config --cflags --cppflags` filtro.c `MagickWand-config --ldflags --libs`

void filtro(char *input,char *output) {
	PixelWand *p_wand = NULL;
	PixelWand *c_wand = NULL;
	DrawingWand *d_wand = NULL;
	MagickWand *magick_wand;
	MagickBooleanType status;

	p_wand = NewPixelWand();
	c_wand = NewPixelWand();
	d_wand = NewDrawingWand();

	DrawSetFontSize(d_wand,45);
	PixelSetColor(p_wand,"black");
	PixelSetColor(c_wand,"red");
	DrawSetFillColor(d_wand,c_wand);
	MagickWandGenesis();

	magick_wand=NewMagickWand();
	status=MagickReadImage(magick_wand,input);
	MagickResizeImage(magick_wand,500,500,LanczosFilter,1.0);
	status=MagickSepiaToneImage(magick_wand,50000);
	status=MagickAnnotateImage(magick_wand,d_wand,50,90,0,"HAPPY BIRTHDAY");
	status=MagickBorderImage(magick_wand,p_wand,20,20);
	status=MagickWriteImage(magick_wand,output);
}



