ls | grep -E '*.uxf' | tr '.' ' ' | awk '{print $1}' | xargs -I '{}' cmd.exe /C umlet.exe -action=convert -format=svg -filename='{}'.uxf;
ls | grep -E '*.uxf' | tr '.' ' ' | awk '{print $1}' | xargs -I '{}' cmd.exe /C umlet.exe -action=convert -format=pdf -filename='{}'.uxf;
ls *.pdf | tr '.' ' ' | awk '{print $1}' | xargs -I '{}' mv '{}'.uxf.pdf '{}'.pdf;
ls *.pdf | tr '.' ' ' | awk '{print $1}' | xargs -I '{}' mv '{}'.uxf.svg '{}'.svg;


