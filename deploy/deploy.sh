#!/bin/bash
docker run -it --rm -a stdout --entrypoint cat dfe2d3ff8875 /etc/sentry/sentry.conf.py


readonly CHART_NAME=admin
readonly CHART_DIR=./deploy/helm

CONSUL_ADDR=${CONSUL_ADDR:=127.0.0.1:8500}
ENV=${ENV:=snb}
VERSION=$(git rev-parse --short HEAD)

function log {
  local readonly level="$1"
  local readonly message="$2"
  local readonly timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  >&2 echo -e "${timestamp} [${level}] [$SCRIPT_NAME] ${message}"
}

function log_info {
  local readonly message="$1"
  log "INFO" "$message"
}

function log_warn {
  local readonly message="$1"
  log "WARN" "$message"
}

function log_error {
  local readonly message="$1"
  log "ERROR" "$message"
}

function update_deps() {
    log_info "Syncing dependencies..."
    helm dependencies update --kube-context ${KUBE_CONTEXT} ${CHART_DIR}
}

function has_jq {
  [ -n "$(command -v jq)" ]
}

function has_consul {
  [ -n "$(command -v consul)" ]
}

function has_helm {
  [ -n "$(command -v helm)" ]
}

function get_vars() {
    log_info "Getting variables..."
    readonly KUBE_CONTEXT=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/common/kube_context`
    readonly DATABASE_URL=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/secrets/databaseUrl`
    readonly SECRET_KEY=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/secrets/secretKey`
    readonly DJANGO_SETTINGS_MODULE=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/djangoSettingsModule`
    readonly STATIC_URL=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/staticUrl`

    readonly SENTRY_DSN=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/secrets/sentryDsn`
}

function get_vars_ci() {
    log_info "Getting ci variables..."
    readonly KUBE_CONTEXT=`curl --silent --user ${CONSUL_AUTH} http://consul.${ENV}.videocoin.network/v1/kv/config/${ENV}/common/kube_context?raw`
    readonly DATABASE_URL=`curl --silent --user ${CONSUL_AUTH} http://consul.${ENV}.videocoin.network/v1/kv/config/${ENV}/services/${CHART_NAME}/secrets/databaseUrl?raw `
    readonly SECRET_KEY=`curl --silent --user ${CONSUL_AUTH} http://consul.${ENV}.videocoin.network/v1/kv/config/${ENV}/services/${CHART_NAME}/secrets/secretKey?raw `

    readonly DJANGO_SETTINGS_MODULE=`curl --silent --user ${CONSUL_AUTH} http://consul.${ENV}.videocoin.network/v1/kv/config/${ENV}/services/${CHART_NAME}/vars/djangoSettingsModule?raw`
    readonly STATIC_URL=`curl --silent --user ${CONSUL_AUTH} http://consul.${ENV}.videocoin.network/v1/kv/config/${ENV}/services/${CHART_NAME}/vars/staticUrl?raw`

    readonly SENTRY_DSN=`curl --silent --user ${CONSUL_AUTH} http://consul.${ENV}.videocoin.network/v1/kv/config/${ENV}/services/${CHART_NAME}/secrets/sentryDsn?raw`
}

function deploy() {
    log_info "Deploying ${CHART_NAME} version ${VERSION}"
    helm upgrade \
        --kube-context "${KUBE_CONTEXT}" \
        --install \
        --timeout 60 \
        --set image.tag=\\"#${VERSION}\\" \
        --set adminStaticImage.tag=\\"${VERSION}\\" \
        --set managerConfig.djangoSettingsModule="${DJANGO_SETTINGS_MODULE}" \
        --set managerConfig.staticUrl="${STATIC_URL}" \
        --set managerConfig.sentryDsn="${SENTRY_DSN}" \
        --set secrets.databaseUrl="${DATABASE_URL}" \
        --set secrets.secretKey="${SECRET_KEY}" \
        --wait ${CHART_NAME} ${CHART_DIR}
}

if ! $(has_jq); then
    log_error "Could not find jq"
    exit 1
fi

if ! $(has_consul); then
    log_error "Could not find consul"
    exit 1
fi

if ! $(has_helm); then
    log_error "Could not find helm"
    exit 1
fi

if [ "${CI_ENABLED}" = "1" ]; then
  get_vars_ci
else
  get_vars
fi

update_deps
deploy

exit $?