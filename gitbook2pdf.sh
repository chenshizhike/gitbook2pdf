#!/bin/bash
#bash 脚本 调用 docker gitbook2pdf
#chmod a+x gitbook2pdf.sh
#cp gitbook2pdf.sh ~/.local/bin/gitbook2pdf

docker run --rm -v /usr/share/fonts:/usr/share/fonts -v `pwd`:/app/output --network=host gitbook2pdf $1

