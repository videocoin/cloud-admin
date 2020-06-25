#!/bin/bash

readonly CHART_NAME=admin
readonly CHART_DIR=./deploy/helm

CONSUL_ADDR=${CONSUL_ADDR:=127.0.0.1:8500}
ENV=${ENV:=dev}
VERSION=$(git rev-parse --short HEAD)
GCP_PROJECT=${GCP_PROJECT:=videocoin-network}

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
    readonly STREAM_MANAGER_CONTRACT_ADDR=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/secrets/streamManagerContractAddr`
    readonly SYMPHONY_KEY=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/secrets/symphonyKey`
    readonly SYMPHONY_OAUTH2_CLIENTID=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/symphonyOauth2Clientid`
    readonly SYMPHONY_ADDR=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/symphonyAddr`
    readonly EMAIL_PASSWORD=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/secrets/emailPassword`
    readonly DEFAULT_FROM_EMAIL=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/defaultFromEmail`
    readonly EMAIL_USER=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/emailUser`
    readonly EMAIL_HOST=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/emailHost`
    readonly VALIDATION_EMAILS=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/validationEmails`
    readonly DJANGO_SETTINGS_MODULE=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/djangoSettingsModule`
    readonly STATIC_URL=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/staticUrl`
    readonly PRIVATE_STREAMS_RPC_ADDR=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/privateStreamsRpcAddr`
    readonly BROKER_URL=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/brokerUrl`
    readonly CELERY_RESULT_BACKEND=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/vars/celeryResultBackend`
    readonly SENTRY_DSN=`consul kv get -http-addr=${CONSUL_ADDR} config/${ENV}/services/${CHART_NAME}/secrets/sentryDsn`
}


function deploy() {
    log_info "Deploying ${CHART_NAME} version ${VERSION}"
    helm upgrade \
        --kube-context "${KUBE_CONTEXT}" \
        --install \
        --set image.repository="gcr.io/${GCP_PROJECT}/${CHART_NAME}" \
        --set image.tag=\\"#${VERSION}\\" \
        --set staticImage.repository="gcr.io/${GCP_PROJECT}/${CHART_NAME}-static" \
        --set staticImage.tag=\\"${VERSION}\\" \
        --set managerConfig.djangoSettingsModule="${DJANGO_SETTINGS_MODULE}" \
        --set managerConfig.staticUrl="${STATIC_URL}" \
        --set managerConfig.privateStreamsRpcAddr="${PRIVATE_STREAMS_RPC_ADDR}" \
        --set managerConfig.brokerUrl="${BROKER_URL}" \
        --set managerConfig.celeryResultBackend="${CELERY_RESULT_BACKEND}" \
        --set managerConfig.sentryDsn="${SENTRY_DSN}" \
        --set managerConfig.emailUser="${EMAIL_USER}" \
        --set managerConfig.emailHost="${EMAIL_HOST}" \
        --set managerConfig.defaultFromEmail="${DEFAULT_FROM_EMAIL}" \
        --set managerConfig.validationEmails="${VALIDATION_EMAILS}" \
        --set managerConfig.symphonyAddr="${SYMPHONY_ADDR}" \
        --set managerConfig.symphonyOauth2Clientid="${SYMPHONY_OAUTH2_CLIENTID}" \
        --set secrets.emailPassword="${EMAIL_PASSWORD}" \
        --set secrets.symphonyKey="${SYMPHONY_KEY}" \
        --set secrets.streamManagerContractAddr="${STREAM_MANAGER_CONTRACT_ADDR}" \
        --set secrets.databaseUrl="${DATABASE_URL}" \
        --set secrets.secretKey="${SECRET_KEY}" \
        --wait ${CHART_NAME} ${CHART_DIR}
}

function delete_jobs {
    log_info "Removing ${CHART_NAME} jobs"
    kubectl --context ${KUBE_CONTEXT} delete job ${CHART_NAME}-db-migrate
    true
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

get_vars
update_deps
deploy
delete_jobs

exit $?