# gitbook2pdf
gitbook2pdf dockerfile
## 使用
1. 安装docker
2. git clone https://github.com/pompey-chen/gitbook2pdf.git
3. cd gitbook2pdf
4. docker build -t gitbook2pdf .
5. gedit ～/.bashrc<br/>
   alias gitbook2pdf='docker run --rm -v /usr/share/fonts:/usr/share/fonts -v `pwd`:/app/output --network=host gitbook2pdf'
7. source ～/.bashrc
