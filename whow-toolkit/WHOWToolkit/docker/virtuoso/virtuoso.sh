#!/bin/bash

echo "Deploying Virtuoso for CROME"



SETTINGS_DIR=/settings
mkdir -p $SETTINGS_DIR

cd /data

mkdir -p dumps

if [ ! -f ./virtuoso.ini ];
then
  mv /virtuoso.ini . 2>/dev/null
fi

chmod +x /clean-logs.sh
mv /clean-logs.sh . 2>/dev/null

original_port=`crudini --get virtuoso.ini HTTPServer ServerPort`
# NOTE: prevents virtuoso to expose on port 8890 before we actually run
#		the server
crudini --set virtuoso.ini HTTPServer ServerPort 27015

if [ ! -f "$SETTINGS_DIR/.config_set" ];
then
  echo "Converting environment variables to ini file"
  printenv | grep -P "^VIRT_" | while read setting
  do
    section=`echo "$setting" | grep -o -P "^VIRT_[^_]+" | sed 's/^.\{5\}//g'`
    key=`echo "$setting" | sed -E 's/^VIRT_[^_]+_(.*)=.*$/\1/g'`
    value=`echo "$setting" | grep -o -P "=.*$" | sed 's/^=//g'`
    echo "Registering $section[$key] to be $value"
    crudini --set virtuoso.ini $section $key "$value"
  done
  echo "`date +%Y-%m%-dT%H:%M:%S%:z`" >  $SETTINGS_DIR/.config_set
  echo "Finished converting environment variables to ini file"
fi

if [ ! -f ".backup_restored" -a -d "backups" -a ! -z "$BACKUP_PREFIX" ] ;
then
    echo "Start restoring a backup with prefix $BACKUP_PREFIX"
    cd backups
    virtuoso-t +restore-backup $BACKUP_PREFIX +configfile /data/virtuoso.ini
    if [ $? -eq 0 ]; then
        cd /data
        echo "`date +%Y-%m-%dT%H:%M:%S%:z`" > .backup_restored
    else
        exit -1
    fi
fi

if [ ! -f ".dba_pwd_set" ];
then
  touch /sql-query.sql
  if [ "$DBA_PASSWORD" ]; then echo "user_set_password('dba', '$DBA_PASSWORD');" >> /sql-query.sql ; fi
  if [ "$SPARQL_UPDATE" = "true" ]; then echo "GRANT SPARQL_UPDATE to \"SPARQL\";" >> /sql-query.sql ; fi
  virtuoso-t +wait && isql-v -U dba -P dba < /dump_nquads_procedure.sql && isql-v -U dba -P dba < /sql-query.sql
  kill "$(ps aux | grep '[v]irtuoso-t' | awk '{print $2}')"
  echo "`date +%Y-%m-%dT%H:%M:%S%:z`" >  .dba_pwd_set
fi

pwd="dba" ;
for D in /usr/local/virtuoso-opensource/share/virtuoso/vad/*;
do
	if [ -d "${D}" ];
	then
    	if [ ! -f "${D}/.data_loaded" ] ;
    	then
    		f=$(basename ${D})
			name=${f%.*}
    		echo "Loading ${D}" ;
    		echo "Files in ${D}: ";
    		ls ${D}
    		echo "ld_dir_all('${D}', '*.*', '$name');" > /load_data.sql
			echo "rdf_loader_run();" >> /load_data.sql
			echo "exec('checkpoint');" >> /load_data.sql
			echo "WAIT_FOR_CHILDREN; " >> /load_data.sql
			echo "$(cat /load_data.sql)"
			virtuoso-t +wait && isql-v -U dba -P "$pwd" < /load_data.sql
			kill $(ps aux | grep '[v]irtuoso-t' | awk '{print $2}')
			echo "`date +%Y-%m-%dT%H:%M:%S%:z`" > ${D}/.data_loaded
    	fi
    fi
done



crudini --set virtuoso.ini HTTPServer ServerPort ${VIRT_HTTPServer_ServerPort:-$original_port}

exec virtuoso-t +wait +foreground
