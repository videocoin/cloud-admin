FROM golang:latest AS builder

LABEL maintainer="Videocoin" description="admin panel for db managment"

RUN apt update && apt upgrade -y
RUN apt install git curl -y

WORKDIR /go/src/github.com/VideoCoin/adminpanel


ADD . ./

RUN make build

FROM ubuntu:latest AS release

RUN apt update && apt upgrade -y
RUN apt install mysql-client ca-certificates -y

COPY --from=builder /go/src/github.com/VideoCoin/adminpanel/bin/admin ./admin

EXPOSE 9077

ENTRYPOINT [ "./admin" ]
