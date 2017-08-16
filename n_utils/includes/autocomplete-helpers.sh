#!/bin/bash

cache () {
  if ! [ -d .cache ]; then
      mkdir -p .cache
  fi
  #Delete cached files older than 5 minutes
  find .cache -mindepth 1 -mmin +5 -exec rm -f {} \;
  args="${*}"
  cachefile=.cache/"${args//[\"\'\ -\*]/_}"
  if [ -e "$cachefile" ]; then
    cat $cachefile
  else
    "$@" | tee $cachefile
  fi
}
get_bakeable_images() {
  if [ -r infra.properties -o -r infra-master.properties ]; then
    echo $(find . -mindepth 2 -maxdepth 2 -name 'image' -a -type d | cut -d '/' -f 2)
  fi
}
get_stack_dirs() {
  if [ -r infra.properties -o -r infra-master.properties ]; then
    echo $(find . -mindepth 2 -maxdepth 2 -name 'infra*.properties' | cut -d '/' -f 2 | sort -u)
  fi
}
get_stacks() {
  if [ -r infra.properties -o -r infra-master.properties ]; then
    echo $(find $1 -mindepth 1 -maxdepth 1 -name 'stack-*' | sed 's/.*stack-\(.*\)/\1/g')
  fi
}
get_imageids() {
  if [ -r infra.properties -o -r infra-master.properties ]; then
    source source_infra_properties.sh $1
    if [ -d "$1/image" ] && [ -r "$1/infra.properties" -o -r "$1/infra-$GIT_BRANCH.properties" ]; then
      echo $(cache aws ec2 describe-images --filters "Name=name,Values=[${2}*]" --query "Images[*].{ID:ImageId}" | jq -r .[].ID)
    fi
  fi
}
get_dockers() {
  if [ -r infra.properties -o -r infra-master.properties ]; then
    echo $(find $1 -mindepth 1 -maxdepth 1 -name 'docker-*' | sed 's/.*docker-\(.*\)/\1/g')
  fi
}
