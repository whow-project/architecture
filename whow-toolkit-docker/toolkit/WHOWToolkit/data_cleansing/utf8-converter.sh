#!/bin/bash

#parameter ./utf8-converter.sh folderpath

#example ./utf8-converter.sh /data/euring/v2/dirtydata /data/euring/v2/data


ICONVBIN='/usr/bin/iconv' # path to iconv binary



if [ $# -lt 2 ]
then
  echo "$0 dir from_charset to_charset"
  exit
fi

for f in $1/*
do
  if test -f $f
  then
    echo -e "\nConverting $f"
    /bin/mv $f $f.old
	CHARSET="$(file -I "$f.old"|awk -F "=" '{print $2}')"
        echo -e "$CHARSET"
	part2=$(basename "$f")
        	if [ "$CHARSET" != utf-8 ]; then
			$ICONVBIN -f "$CHARSET" -t utf8 $f.old > $2/$part2
			/bin/mv $f.old $f
		else
		    /bin/cp $f.old $2/$part2
		    /bin/mv $f.old $f
		fi
  else
    echo -e "\nSkipping $f - not a regular file";
  fi
  
done