# You can set these variables from the command line, and also
# from the environment for the first two.
$(warning picture make file)

# 1) make sure umlet.sh is in your path
# 2) replace line 31 of umlet.sh with:
# if [! -z "${UMLET_HOME}" ] ; then
CC=umlet.sh
UXF = $(shell find . -name "*.uxf")
SVG = $(patsubst %.uxf, %.svg,$(UXF))
PDF = $(patsubst %.uxf, %.pdf,$(UXF))

#$(warning uxf_files $(UXF))
#$(warning svg_files $(SVG))

.RECIPEPREFIX = >

all : $(SVG) $(PDF)

%.svg: %.uxf
> echo $<; \
> DISPLAY= $(CC) -action=convert -format=svg -filename=$<;

%.pdf: %.uxf
> echo $<; \
> DISPLAY= $(CC) -action=convert -format=pdf -filename=$<;
