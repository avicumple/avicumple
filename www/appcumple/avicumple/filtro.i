%module filtro

%{
#define SWIG_FILE_WITH_INIT
#include "filtro.h"
%}

void filtro(char *input,char *output);
