FROM golang:latest AS builder

LABEL maintainer="videocoin" description="admin panel for db managment"

RUN apt update && apt upgrade -y
RUN apt install git curl -y

WORKDIR /go/src/github.com/videocoin/cloud-admin


ADD . ./

RUN make build

FROM ubuntu:latest AS release

RUN apt update && apt upgrade -y
RUN apt install mysql-client ca-certificates -y

COPY --from=builder /go/src/github.com/videocoin/cloud-admin/bin/admin ./admin

EXPOSE 9077

ENTRYPOINT [ "./admin" ]
