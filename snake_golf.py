def a():global e;e=r(1,s.width-3),r(1,s.height-4)
def p():s.clear();s.draw_box(0,1,s.width-1,s.height-1,"#");s.draw_char(e[0]+1,e[1]+2,f)
import lskd,time,TexUI;from random import randint as r;q,w,t,y,l,f="<",">","v","^","d","@";b=[w];s=TexUI.Display();c=[s.width//2,s.height//2];TexUI.clear_terminal();a();p();s.flush()
def u(x,z,y):c[x]+=z;b[:]=b[1:]+[y]
while 1:
    if lskd.on_press():l=lskd.translate(lskd.char.get(),l)
    p();s.draw_str(0,0,f"{len(b)}");o=ò=0;d=l if l in"wasd"and b[-1]!={"d":q,"a":w,"s":t,"w":y}[l]else d;u(*{"d":(0,1,w),"a":(0,-1,q),"s":(1,1,y),"w":(1,-1,t)}[d])
    for g in b[::-1]:h=s.get_char(c[0]+o,c[1]+ò);(b.insert(0,b[0]),a())if h==f else exit()if h!=" "else 0;s.draw_char(c[0]+o,c[1]+ò,"█");o+={w:-1,q:1}.get(g,0);ò+={y:-1,t:1}.get(g,0)
    s.flush(0,0);time.sleep(.1)
