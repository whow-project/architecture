#!/bin/bash

#parameter ./utf8-converter.sh sourcefolderpath destinationfolderpath

#example ./utf8-converter.sh /data/euring/v2/dirtydata  /data/euring/v2/data

#NEEDED: iconv and dos2unix

ICONVBIN='/usr/bin/iconv' # path to iconv binary

# Detect the platform (similar to $OSTYPE)
OS="`uname`"
case $OS in
  'Linux')
    OS='Linux'
    alias ls='ls --color=auto'
    ;;
  'FreeBSD')
    OS='FreeBSD'
    alias ls='ls -G'
    ;;
  'WindowsNT')
    OS='Windows'
    ;;
  'Darwin') 
    OS='Mac'
    ;;
  'SunOS')
    OS='Solaris'
    ;;
  'AIX') ;;
  *) ;;
esac

echo $OS


if [ $# -lt 2 ]
then
  echo "$0 dir from_charset to_charset"
  exit
fi
if [[ "$OSTYPE" =~ ^linux ]]; then
   apt install dos2unix 
fi
for f in $1/*
do
  if test -f $f
  then
    echo -e "\nConverting $f"
    /bin/mv $f $f.old
	if [[ "$OSTYPE" =~ ^linux ]]; then
            CHARSET="$(file -bi "$f.old"|awk -F "=" '{print $2}')"
        else
            CHARSET="$(file -I "$f.old"|awk -F "=" '{print $2}')"
        fi
        echo -e "$CHARSET"
	part2=$(basename "$f")
        	if [ "$CHARSET" != utf-8 ]; then
		     if [[ "$OSTYPE" =~ ^linux ]]; then
                                $ICONVBIN -f "$CHARSET" -t utf8 $f.old -o $2/$part2
                     else
                                $ICONVBIN -f "$CHARSET" -t utf8 $f.old > $2/$part2
                     fi
			/bin/mv $f.old $f
			/bin/dos2unix -ascii $f

		else
		    /bin/cp $f.old $2/$part2
		    /bin/mv $f.old $f
		fi
  else
    echo -e "\nSkipping $f - not a regular file";
  fi
  
done
