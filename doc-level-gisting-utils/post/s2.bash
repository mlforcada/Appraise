# To be done: IAA, recovering job050, adding partial jobs, adding new jobs

echo "\"File\",\"Percentage\",\"System\",\"Context\",\"Strategy\",\"Score\",\"Serial\",\"Informant\",\"Time\",\"Inf\"" >results.csv
cat results  | xargs -n 2 ./filter_results.py  >>results.csv
# cat results | grep -v 050 | xargs -n 2 ./filter_results.py >results.csv
# printf "Removing  1 item from job050 for the moment\n"
cat results.csv | sed 's/","/ /g' >results.bsv

printf "1. Results with no hint\n"
printf "=======================\n"

printf "Strategy  percentage  avg.   stdev   samples\n"
printf "[both]    [both]     "; cat results.bsv | grep NONE |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "+ent      [both]     "; cat results.bsv | grep NONE | fgrep "+ent" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "–ent      [both]     "; cat results.bsv | grep NONE | grep "[-]ent" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "[both]    10%%        "; cat results.bsv | grep NONE | grep " 0.10 " |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "[both]    20%%        "; cat results.bsv | grep NONE | grep " 0.20 " |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "+ent      10%%        "; cat results.bsv | grep NONE | fgrep "+ent" | grep " 0.10 " |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "–ent      10%%        "; cat results.bsv | grep NONE | grep "[-]ent" | grep " 0.10" | awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "+ent      20%%        "; cat results.bsv | grep NONE | fgrep "+ent" | grep " 0.20 " |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "–ent      20%%        "; cat results.bsv | grep NONE | grep "[-]ent" | grep " 0.20" | awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "\n"

printf "Welch t-tests:\n"

printf "Testing (+ent [both]) vs. (-ent  [both]) \n"
cat results.bsv | grep NONE | fgrep "+ent" | awk '{print $6}' >/tmp/a
cat results.bsv | grep NONE | grep "[-]ent" | awk '{print $6}' >/tmp/b	
python sigtest.py

printf "Testing (+ent 10%%) vs. (-ent 10%%) \n"
cat results.bsv | grep NONE | fgrep "+ent"| grep " 0.10" | awk '{print $6}' >/tmp/a
cat results.bsv | grep NONE | grep "[-]ent" | grep " 0.10" | awk '{print $6}' >/tmp/b	
python sigtest.py

printf "Testing (+ent 20%%) vs. (-ent 20%%) \n"
cat results.bsv | grep NONE | fgrep "+ent"| grep " 0.20" | awk '{print $6}' >/tmp/a
cat results.bsv | grep NONE | grep "[-]ent" | grep " 0.20" | awk '{print $6}' >/tmp/b	
python sigtest.py

printf "Testing ([both] 10%%) vs. ([both] 20%%) \n"
cat results.bsv | grep NONE | grep " 0.10 " | awk '{print $6}' >/tmp/a
cat results.bsv | grep NONE | grep " 0.20 " | awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing (+ent 10%%) vs. (+ent 20%%) \n"
cat results.bsv | grep NONE | fgrep "+ent"| grep " 0.10" | awk '{print $6}' >/tmp/a
cat results.bsv | grep NONE | grep "+ent" | grep " 0.20" | awk '{print $6}' >/tmp/b	
python sigtest.py

printf "Testing (-ent 10%%) vs. (-ent 20%%) \n"
cat results.bsv | grep NONE | grep "[-]ent"| grep " 0.10" | awk '{print $6}' >/tmp/a
cat results.bsv | grep NONE | grep "[-]ent" | grep " 0.20" | awk '{print $6}' >/tmp/b	
python sigtest.py


printf "2. Machine translation results\n"
printf "==============================\n"
printf "System  percentage context  avg.  stdev  samples\n"

# both percentages

printf "[all]   [both]     [both]  "; cat results.bsv | grep -v NONE |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Moses   [both]     [both]  "; cat results.bsv | grep moses |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Google  [both]     [both]  "; cat results.bsv | grep google |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Bing    [both]     [both]  "; cat results.bsv | grep bing |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Systran [both]     [both]  "; cat results.bsv | grep systran |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "[all]   [both]     +doc    "; cat results.bsv | grep -v NONE | fgrep "+doc" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Moses   [both]     +doc    "; cat results.bsv | grep moses | fgrep "+doc"|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Google  [both]     +doc    "; cat results.bsv | grep google | fgrep "+doc" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Bing    [both]     +doc    "; cat results.bsv | grep bing |fgrep "+doc" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Systran [both]     +doc    "; cat results.bsv | grep systran |fgrep "+doc" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'

printf "[all]   [both]     –doc    "; cat results.bsv | grep -v NONE | grep "[-]doc" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Moses   [both]     –doc    "; cat results.bsv | grep moses | grep "[-]doc"|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Google  [both]     –doc    "; cat results.bsv | grep google | grep "[-]doc" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Bing    [both]     –doc    "; cat results.bsv | grep bing | grep "[-]doc" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Systran [both]     –doc    "; cat results.bsv | grep systran | grep "[-]doc" |awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'

# 10%

printf "[all]   10%%         [both]  "; cat results.bsv | grep -v NONE |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Moses   10%%         [both]  "; cat results.bsv | grep moses |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Google  10%%         [both]  "; cat results.bsv | grep google |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Bing    10%%         [both]  "; cat results.bsv | grep bing |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Systran 10%%         [both]  "; cat results.bsv | grep systran |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'

printf "[all]   10%%         +doc    "; cat results.bsv | grep -v NONE | fgrep "+doc" |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Moses   10%%         +doc    "; cat results.bsv | grep moses | fgrep "+doc"|fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Google  10%%         +doc    "; cat results.bsv | grep google | fgrep "+doc" |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Bing    10%%         +doc    "; cat results.bsv | grep bing |fgrep "+doc" |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Systran 10%%         +doc    "; cat results.bsv | grep systran |fgrep "+doc" |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'

printf "[all]   10%%         –doc    "; cat results.bsv | grep -v NONE | grep "[-]doc" |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Moses   10%%         –doc    "; cat results.bsv | grep moses | grep "[-]doc"|fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Google  10%%         –doc    "; cat results.bsv | grep google | grep "[-]doc" |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Bing    10%%         –doc    "; cat results.bsv | grep bing | grep "[-]doc" |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Systran 10%%         –doc    "; cat results.bsv | grep systran | grep "[-]doc" |fgrep " 0.10 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'


# 20%

printf "[all]   20%%         [both]  "; cat results.bsv | grep -v NONE |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Moses   20%%         [both]  "; cat results.bsv | grep moses |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Google  20%%         [both]  "; cat results.bsv | grep google |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Bing    20%%         [both]  "; cat results.bsv | grep bing |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Systran 20%%         [both]  "; cat results.bsv | grep systran |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'

printf "[all]   20%%         +doc    "; cat results.bsv | grep -v NONE | fgrep "+doc" |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Moses   20%%         +doc    "; cat results.bsv | grep moses | fgrep "+doc"|fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Google  20%%         +doc    "; cat results.bsv | grep google | fgrep "+doc" |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Bing    20%%         +doc    "; cat results.bsv | grep bing |fgrep "+doc" |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Systran 20%%         +doc    "; cat results.bsv | grep systran |fgrep "+doc" |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'

printf "[all]   20%%         –doc    "; cat results.bsv | grep -v NONE | grep "[-]doc" |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Moses   20%%         –doc    "; cat results.bsv | grep moses | grep "[-]doc"|fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Google  20%%         –doc    "; cat results.bsv | grep google | grep "[-]doc" |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Bing    20%%         –doc    "; cat results.bsv | grep bing | grep "[-]doc" |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'
printf "Systran 20%%         –doc    "; cat results.bsv | grep systran | grep "[-]doc" |fgrep " 0.20 "|awk '{r=$6; s+=r; s2+=r*r} END{printf "%6.3f %6.3f %5d\n", s/NR, ((s2-s*s/NR)/NR)^2, NR}'


printf "Welch t-tests:\n\n"

printf "\nAny percentage\n\n"


printf "Testing ([Moses [both] [both]) vs. (Google [both]  [both]) \n"
cat results.bsv | grep moses |awk '{print $6}' >/tmp/a
cat results.bsv | grep google |awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Moses [both] [both]) vs. (Bing [both]  [both]) \n"
cat results.bsv | grep moses |awk '{print $6}' >/tmp/a
cat results.bsv | grep bing |awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Moses [both] [both]) vs. (Systran [both]  [both]) \n"
cat results.bsv | grep moses |awk '{print $6}' >/tmp/a
cat results.bsv | grep systran |awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Google [both] [both]) vs. (Bing [both]  [both]) \n"
cat results.bsv | grep google |awk '{print $6}' >/tmp/a
cat results.bsv | grep bing |awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Google [both] [both]) vs. (Systran [both]  [both]) \n"
cat results.bsv | grep google |awk '{print $6}' >/tmp/a
cat results.bsv | grep systran |awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Bing [both] [both]) vs. (Systran [both]  [both]) \n"
cat results.bsv | grep bing |awk '{print $6}' >/tmp/a
cat results.bsv | grep systran |awk '{print $6}' >/tmp/b
python sigtest.py


printf "\n10%%\n\n"

printf "Testing ([Moses [both] [both]) vs. (Google [both]  [both]) \n"
cat results.bsv | grep moses |grep " 0.10"|awk '{print $6}' >/tmp/a
cat results.bsv | grep google |grep " 0.10"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Moses [both] [both]) vs. (Bing [both]  [both]) \n"
cat results.bsv | grep moses |grep " 0.10"|awk '{print $6}' >/tmp/a
cat results.bsv | grep bing |grep " 0.10"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Moses [both] [both]) vs. (Systran [both]  [both]) \n"
cat results.bsv | grep moses |grep " 0.10"|awk '{print $6}' >/tmp/a
cat results.bsv | grep systran |grep " 0.10"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Google [both] [both]) vs. (Bing [both]  [both]) \n"
cat results.bsv | grep google |grep " 0.10"|awk '{print $6}' >/tmp/a
cat results.bsv | grep bing |grep " 0.10"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Google [both] [both]) vs. (Systran [both]  [both]) \n"
cat results.bsv | grep google |grep " 0.10"|awk '{print $6}' >/tmp/a
cat results.bsv | grep systran |grep " 0.10"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Bing [both] [both]) vs. (Systran [both]  [both]) \n"
cat results.bsv | grep bing |grep " 0.10"|awk '{print $6}' >/tmp/a
cat results.bsv | grep systran |grep " 0.10"|awk '{print $6}' >/tmp/b
python sigtest.py


printf "\n20%%\n\n"

printf "Testing ([Moses [both] [both]) vs. (Google [both]  [both]) \n"
cat results.bsv | grep moses |grep " 0.20"|awk '{print $6}' >/tmp/a
cat results.bsv | grep google |grep " 0.20"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Moses [both] [both]) vs. (Bing [both]  [both]) \n"
cat results.bsv | grep moses |grep " 0.20"|awk '{print $6}' >/tmp/a
cat results.bsv | grep bing |grep " 0.20"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Moses [both] [both]) vs. (Systran [both]  [both]) \n"
cat results.bsv | grep moses |grep " 0.20"|awk '{print $6}' >/tmp/a
cat results.bsv | grep systran |grep " 0.20"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Google [both] [both]) vs. (Bing [both]  [both]) \n"
cat results.bsv | grep google |grep " 0.20"|awk '{print $6}' >/tmp/a
cat results.bsv | grep bing |grep " 0.20"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Google [both] [both]) vs. (Systran [both]  [both]) \n"
cat results.bsv | grep google |grep " 0.20"|awk '{print $6}' >/tmp/a
cat results.bsv | grep systran |grep " 0.20"|awk '{print $6}' >/tmp/b
python sigtest.py

printf "Testing ([Bing [both] [both]) vs. (Systran [both]  [both]) \n"
cat results.bsv | grep bing |grep " 0.20"|awk '{print $6}' >/tmp/a
cat results.bsv | grep systran |grep " 0.20"|awk '{print $6}' >/tmp/b
python sigtest.py


printf "\nEffect of document context\n\n"

printf "Testing ([all] [both] +doc) vs. ([all] [both] –doc) \n"

cat results.bsv | grep -v NONE | grep "[-]doc" |awk '{print $6}' >/tmp/a
cat results.bsv | grep -v NONE | fgrep "+doc" |awk '{print $6}' >/tmp/b
python sigtest.py

printf "\nEffect of gap percentage \n\n"

cat results.bsv | grep -v NONE |fgrep " 0.10 "|awk '{print $6}' >/tmp/a
cat results.bsv | grep -v NONE |fgrep " 0.20 "|awk '{print $6}' >/tmp/b 
python sigtest.py



