pandoc --top-level-division=chapter --listings --filter pandoc-fignos -t latex ../../Introduction.md | sed 's/\\chapter/\\chapter\*/' | sed 's/\\section/\\section\*/' > generated_tex/Introduction.tex
pandoc --top-level-division=chapter --listings --filter pandoc-fignos -o generated_tex/Chapter\ 1\:\ Let\'s\ Start\ with\ the\ Bootloader.tex ../../Chapter\ 1\:\ Let\'s\ Start\ with\ the\ Bootloader.md
pandoc --top-level-division=chapter --listings --filter pandoc-fignos -o generated_tex/Chapter\ 2\:\ An\ Overview\ of\ x86\ Architecture.tex ../../Chapter\ 2\:\ An\ Overview\ of\ x86\ Architecture.md
pandoc --top-level-division=chapter --listings --filter pandoc-fignos -o generated_tex/Chapter\ 3\:\ The\ Progenitor\ of\ 539kernel.tex ../../Chapter\ 3\:\ The\ Progenitor\ of\ 539kernel.md
pandoc --top-level-division=chapter --listings --filter pandoc-fignos -o generated_tex/Chapter\ 4\:\ Process\ Management.tex ../../Chapter\ 4\:\ Process\ Management.md
pandoc --top-level-division=chapter --listings --filter pandoc-fignos -o generated_tex/Chapter\ 5\:\ Memory\ Management.tex ../../Chapter\ 5\:\ Memory\ Management.md
pandoc --top-level-division=chapter --listings --filter pandoc-fignos -o generated_tex/Chapter\ 6\:\ Filesystems.tex ../../Chapter\ 6\:\ Filesystems.md
pandoc --top-level-division=chapter --listings --filter pandoc-fignos -o generated_tex/Chapter\ 7\:\ What\'s\ Next\?.tex ../../Chapter\ 7\:\ What\'s\ Next\?.md
pandoc --top-level-division=chapter --listings --filter pandoc-fignos -t latex ../../References.md | sed 's/\\chapter/\\chapter\*/' | sed 's/\\section/\\section\*/' > generated_tex/References.tex

# To Generate PDFs Directly from Pandoc.
# pandoc --filter pandoc-fignos --listings -H tex_setup/listings-setup.tex -o Introduction.tex ../../Introduction.md
