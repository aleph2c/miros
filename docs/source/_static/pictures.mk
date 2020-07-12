# You can set these variables from the command line, and also
# from the environment for the first two.
$(warning picture make file)

WINDOWS_UMLET_PATH = "Umlet.exe"
CC=Umlet.exe
UXF = $(shell find . -name "*.uxf")
SVG = $(patsubst %.uxf, %.svg,$(UXF))
PDF = $(patsubst %.uxf, %.pdf,$(UXF))

#$(warning uxf_files $(UXF))
#$(warning svg_files $(SVG))

.RECIPEPREFIX = >

all : $(SVG) $(PDF)

%.svg: %.uxf
> echo $<; \
> cmd.exe /C $(CC) -action=convert -format=svg -filename=$<;

%.pdf: %.uxf
> echo $<; \
> cmd.exe /C $(CC) -action=convert -format=pdf -filename=$<;
