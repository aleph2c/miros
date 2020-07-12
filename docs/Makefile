# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -d source/_doctrees/
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = ../docs
DIR           = $(shell pwd)
PICTURES      = $(DIR)/source/_static
GOALS         = html latex epub

.RECIPEPREFIX = >

#subsystem:
#> cd $(PICTURES) && $(MAKE)

# Put it first so that "make" without argument is like "make help".

.PHONY: help pictures Makefile
$(warning $(shell pwd))

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
$(GOALS): Makefile pictures
> @$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O); \


pictures:
> cd $(PICTURES); \
> make --file $(PICTURES)/pictures.mk; \
> cd - ; \

help:
> @$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


clean:
> rm -rf "$(BUILDDIR)"/html
> rm -rf "$(BUILDDIR)"/source/_doctrees
