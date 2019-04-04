FROM scratch
ADD bin/admin-panel_*_linux_amd64 /admin-panel
CMD ["/admin-panel"]
