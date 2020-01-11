# shuangpin-heatmap

TODO:
-   generate keyboard svg basemap
-   text -> pinyin -> shuangpin -> count -> heatmap

## References

-   https://github.com/hankcs/HanLP
-   https://github.com/mozillazg/python-pinyin
-   http://lingua.mtsu.edu/chinese-computing/statistics/bigram/list.php?nowstage=1&nowpage=1&Corpus=GF&BiFreq=50&MI=3.5
-   [双拼自然码 dvorak (mod) layout](http://www.keyboard-layout-editor.com/##@_name=dvorak%20mod&pcb:false%3B&@=~%0A%60&=!%0A1&=%2F@%0A2&=%23%0A3&=$%0A4&=%25%0A5&=%5E%0A6&=%2F&%0A7&=*%0A8&=(%0A9&=)%0A0&=%2F_%0A-&=+%0A%2F=&_w:2%3B&=Backspace%3B&@_w:1.5%3B&=Tab&=%2F:%0A%2F%3B&=%3C%0A,&=%3E%0A.&=K%0A%0Ak%0A%0A%0A%0A%0Aao&=Y%0A%0Ay%0Auai%0A%0A%0A%0Aing&=F%0A%0Af%0A%0A%0A%0A%0Aen&=G%0A%0Ag%0A%0A%0A%0A%0Aeng&=C%0A%0Ac%0A%0A%0A%0A%0Aiao&=L%0A%0Al%0A%0A%0A%0A%0Aai&=Z%0A%0Az%0A%0A%0A%0A%0Aei&=%7B%0A%5B&=%7D%0A%5D&_w:1.5%3B&=%7C%0A%5C%3B&@_w:1.75%3B&=Control&=A%0A%0A%0A%0A%0A%0A%0Aa&=O%0A%0A%0Aou%0A%0A%0A%0Ao&=E%0A%0A%0A%0A%0A%0A%0Ae&_n:true%3B&=I%0A%0Ach%0A%0A%0A%0A%0Ai&=U%0A%0Ash%0A%0A%0A%0A%0Au&=D%0A%0A%0Auang%0A%0A%0A%0Aiang&_n:true%3B&=R%0A%0Ar%0A%0A%0A%0A%0Auan&=T%0A%0At%0Ave%0A%0A%0A%0Aue&=S%0A%0A%0Aong%0A%0A%0A%0Aiong&=N%0A%0An%0A%0A%0A%0A%0Ain&=%22%0A'&_w:2.25%3B&=Enter%3B&@_w:2.25%3B&=Shift&=P%0A%0Ap%0A%0A%0A%0A%0Aun&=Q%0A%0Aq%0A%0A%0A%0A%0Aiu&=J%0A%0Aj%0A%0A%0A%0A%0Aan&=H%0A%0Ah%0A%0A%0A%0A%0Aang&=X%0A%0Ax%0A%0A%0A%0A%0Aie&=B%0A%0Ab%0A%0A%0A%0A%0Aou&=M%0A%0Am%0A%0A%0A%0A%0Aian&=W%0A%0Aw%0Aua%0A%0A%0A%0Aia&_w2:1.5%3B&=V%0A%0Azh%0Av%0A%0A%0A%0Aui&=%3F%0A%2F%2F&_w:2.75%3B&=Shift%3B&@_w:1.25%3B&=Ctrl&_w:1.25%3B&=Win&_w:1.25%3B&=Alt&_a:7&w:6.25%3B&=&_a:4&w:1.25%3B&=Alt&_w:1.25%3B&=Win&_w:1.25%3B&=Menu&_w:1.25%3B&=Ctrl)