#!/usr/bin/env bash

USAGE="usage: $0 language(fr|en)"
ROOT_DIR=$(dirname "$0")/..

if test "$#" != "1"; then
  echo "$USAGE"
  exit 1
fi

LANGUAGE=$1
DOMAIN_FILENAME="${ROOT_DIR}/domain.yml"

# domain.yml
echo "language: &language ${LANGUAGE}
" > "${DOMAIN_FILENAME}"

cat "${ROOT_DIR}/domain/domain.core.yml" \
    "${ROOT_DIR}/domain/domain.${LANGUAGE}.yml" \
    >> "${DOMAIN_FILENAME}"

# config.yml
cat "${ROOT_DIR}/config/config.${LANGUAGE}.yml" \
    "${ROOT_DIR}/config/config.core.yml" \
    > "${ROOT_DIR}/config.yml"

# data/nlu.md
cat "${ROOT_DIR}/data/nlu.${LANGUAGE}.md" \
    > "${ROOT_DIR}/data/nlu.md"
