"""Generate the walle-emoji GIF pack.

Every emoji is drawn procedurally on a 32x32 pixel grid, scaled 4x to 128x128,
and saved as a looping GIF with a transparent background.

Usage:  python generate.py <output-dir>      (requires Pillow)
"""
import os, sys
from PIL import Image
out=sys.argv[1] if len(sys.argv)>1 else 'gifs'
os.makedirs(out,exist_ok=True)
PAL=[(255,0,255),(16,16,16),(216,210,202),(70,66,64),(150,145,140),(112,106,102),(250,200,60),(232,160,40),(190,50,30),
     (70,200,100),(240,90,130),(110,180,250),(230,60,50),(200,225,255),(160,100,58),(112,68,40),(40,140,60),(170,165,70),(255,40,190),(0,200,230),(40,220,90),(150,80,255),(255,255,255)]
T,K,W,D,L,M,Y,O,RD,GREEN,PINK,BLUE,XRED,ICE,BROWN,DBROWN,DGREEN,WILT,MAG,CYAN,NEON,PURP,WHITE=range(23)
CH={'#':K,'w':W,'d':D,'l':L,'m':M,'y':Y,'o':O,'r':RD}
N=32; SCALE=4; OX=5; OY=10
R=lambda v:int(round(v))
def parse(rows,c0,r0):
    return {(c0+i,r0+j):CH[ch] for j,row in enumerate(rows) for i,ch in enumerate(row.split()) if ch!='.'}
BODY=parse([
 ". # # # # # # # # # # # # # .",
 "# y y y y y y y y y y y y y #",
 "# y d m m l l o o o o d d o #",
 "# y y y y y y y y y y y y y #",
 ". # y y y y y y y y y y y # .",
 ". . # y y y y y y y y y # . .",
 ". . # y y y y y r r r y # . .",
 ". . # o y y y y y y y y # . .",
 ". . . # # # # # # # # # . . ."],3,10)
def tread(side,phase):
    b=lambda a,z:[(c,'b') for c in range(a,z+1)]
    rows={13:[(2,'#')],14:[(1,'#')]+b(2,3),15:[(0,'#')]+b(1,4),16:[(0,'#')]+b(1,4),17:[(0,'#')]+b(1,4),
          18:[(0,'#')]+b(1,5)+[(6,'#')],19:[(0,'#')]+b(1,5)+[(6,'#')],20:[(c,'#') for c in range(1,7)]}
    p={}
    for r,cells in rows.items():
        for c,ch in cells:
            p[(c if side<0 else 20-c,r)]=K if ch=='#' else (M if (r+phase)%2==0 else D)
    return p
HEART5=["##.##","#####",".###.","..#.."]
def head(eyes,look,pdy):
    p={}
    for cx0 in (2,10):
        for r in range(8):
            for c in range(cx0,cx0+9):
                lc=c-cx0; ds=(lc+r,lc+7-r,8-lc+r,8-lc+7-r)
                if (cx0==2 and lc==8 and r==0) or (cx0==10 and lc==0 and r==0) or min(ds)<2: continue
                p[(c,r)]=K if (r in (0,7) or lc in (0,8) or min(ds)==2) else W
        pc=cx0+3+look
        if eyes=='closed':
            for r in range(1,5):
                for c in range(cx0+1,cx0+8):
                    if p.get((c,r))==W: p[(c,r)]=L
            for c in range(cx0+2,cx0+7): p[(c,5)]=K
        elif eyes in ('open','sad'):
            for r in range(2,6):
                for c in range(pc,pc+4): p[(c,r+pdy)]=K
            p[(pc+1,3+pdy)]=L; p[(pc+2,3+pdy)]=D; p[(pc+1,4+pdy)]=D; p[(pc+2,4+pdy)]=D
            if eyes=='sad':
                for c in range(cx0+1,cx0+8):
                    for r in (1,2,3):
                        if p.get((c,r)) in (W,L,D) or (p.get((c,r))==K and cx0+1<c<cx0+7 and r>1): p[(c,r)]=L if r<3 else K
                    if p.get((c,3))==L: p[(c,3)]=K
                p[(pc+1,4)]=D; p[(pc+2,4)]=D
        elif eyes=='happy':
            for c,r in ((pc,4),(pc+1,3),(pc+2,3),(pc+3,4)): p[(c,r)]=K
        elif eyes=='heart':
            for j,row in enumerate(HEART5):
                for i,ch in enumerate(row):
                    if ch=='#': p[(cx0+2+i,2+j)]=PINK
        elif eyes!='none':
            for c in range(pc,pc+4): p[(c,4+pdy)]=K
    p[(10,7)]=K
    return p
def bres(a,b):
    x0,y0,x1,y1=R(a[0]),R(a[1]),R(b[0]),R(b[1]); pts=[]
    dx=abs(x1-x0); dy=-abs(y1-y0); sx=1 if x0<x1 else -1; sy=1 if y0<y1 else -1; err=dx+dy
    while True:
        pts.append((x0,y0))
        if x0==x1 and y0==y1: break
        e2=2*err
        if e2>=dy: err+=dy; x0+=sx
        if e2<=dx: err+=dx; y0+=sy
    return pts
def outlined(p):
    o={}
    for (x,y) in p:
        for ax in (-1,0,1):
            for ay in (-1,0,1): o[(x+ax,y+ay)]=K
    o.update(p); return o
def glyph(rows,x,y,c,ol=True):
    g={(x+i,y+j):c for j,row in enumerate(rows) for i,ch in enumerate(row) if ch=='#'}
    return outlined(g) if ol else g

def pose(bx=0,by=0,lean=0,hx=0,hy=0,kh=0,droop=0,look=0,pdy=0,eyes='open',La=None,Ra=None):
    return dict(bx=bx,by=by,lean=lean,hx=hx,hy=hy,kh=kh,droop=droop,look=look,pdy=pdy,eyes=eyes,La=La,Ra=Ra)
def P(base,**kw): q=dict(base); q.update(kw); return q

def draw(p,phase=0,back=None,front=None):
    im=Image.new('P',(N,N),T); im.putpalette([v for c in PAL for v in c]); px=im.load()
    def raw(d):
        for (x,y),c in d.items():
            if 0<=x<N and 0<=y<N: px[x,y]=c
    if back: raw(back)
    lean=p['lean']
    def bdy(x):
        if lean<0: return -R(-lean*x/20)
        if lean>0: return -R(lean*(20-x)/20)
        return 0
    bx=R(p['bx']); by=R(p['by'])
    def put(part,ox,oy,shear=None):
        raw({(x+ox+OX,y+oy+OY+R(p.get('gy',0))+(shear(x) if shear else 0)):c for (x,y),c in part.items()})
    for sgn,arm in ((-1,p['La']),(1,p['Ra'])):
        if arm is None: continue
        e,h=arm; sx=3 if sgn<0 else 17; s0=(sx,12+by+bdy(sx)); el=(s0[0]+e[0],s0[1]+e[1]); ha=(s0[0]+h[0],s0[1]+h[1])
        a={q:Y for q in bres(s0,el)+bres(el,ha)}; a[(R(el[0]),R(el[1]))]=O
        gx,gy=R(ha[0]),R(ha[1]); ddx=ha[0]-el[0]; ddy=ha[1]-el[1]
        if abs(ddy)>=abs(ddx): s=-1 if ddy<0 else 1; claw=[(0,0),(-1,0),(1,0),(-1,s),(1,s)]
        else: s=-1 if ddx<0 else 1; claw=[(0,0),(0,-1),(0,1),(s,-1),(s,1)]
        for cx,cy in claw: a[(gx+cx,gy+cy)]=M
        put(outlined(a),bx,0)
    put(tread(-1,phase),bx,0,bdy); put(tread(1,phase),bx,0,bdy); put(BODY,bx,by,bdy)
    hx=R(p['hx']); hy=R(p['hy'])+bdy(10); kh=p['kh']; dr=p['droop']
    nb=(10+bx,9+by+bdy(10)); nt=(10+hx,7+hy)
    nk={q:D for q in bres(nb,nt)}
    for c in (9,10,11): nk[(c+bx,nb[1])]=M
    put(outlined(nk),0,0)
    put(head(p['eyes'],R(p['look']),R(p['pdy'])),hx,hy,lambda x:(1 if (kh>0 and x>=11) or (kh<0 and x<=9) else 0)+(R(dr) if x!=10 else 0))
    if front: raw(front)
    return im.resize((N*SCALE,N*SCALE),Image.NEAREST)

ALL={}
def save(name,seq):
    frames=[draw(*s[0]) if isinstance(s[0],tuple) else draw(s[0],**s[2]) for s in seq]
    durs=[s[1] for s in seq]
    frames[0].save(f'{out}/walle-{name}.gif',save_all=True,append_images=frames[1:],duration=durs,loop=0,transparency=0,disposal=2,optimize=False)
    ALL[name]=frames
F=lambda p,d,**kw:(p,d,kw)
mr=lambda a:((-a[0][0],a[0][1]),(-a[1][0],a[1][1]))
UP=((-3,-2),(-4,-8)); PUMP=((-4,0),(-4,-4)); OUT=((-3,0),(-6,1))
REST=pose()


import math
def farm(el,ha,sh=(23,22),palm=None):
    a={q:Y for q in bres(sh,el)+bres(el,ha)}; a[el]=O
    gx,gy=ha; ddx=ha[0]-el[0]; ddy=ha[1]-el[1]
    if palm:
        for j,row in enumerate(palm):
            for i,ch in enumerate(row):
                if ch=='#': a[(gx-len(row)//2+i,gy-1+j)]=M
    else:
        if abs(ddy)>=abs(ddx): s_=-1 if ddy<0 else 1; claw=[(0,0),(-1,0),(1,0),(-1,s_),(1,s_)]
        else: s_=-1 if ddx<0 else 1; claw=[(0,0),(0,-1),(0,1),(s_,-1),(s_,1)]
        for cx,cy in claw: a[(gx+cx,gy+cy)]=M
    return outlined(a)

def hl(p,loc):
    return {(OX+c+R(p['hx']),OY+r+R(p['hy'])+R(p.get('gy',0))+(R(p['droop']) if c!=10 else 0)):v for (c,r),v in loc.items()}
def G(rows,x,y,cmap):
    return {(x+i,y+j):cmap[ch] for j,row in enumerate(rows) for i,ch in enumerate(row) if ch in cmap}
def rectd(x0,y0,x1,y1,c): return {(x,y):c for x in range(x0,x1+1) for y in range(y0,y1+1)}
def plus(x,y,c=Y): return outlined({(x,y):c,(x-1,y):c,(x+1,y):c,(x,y-1):c,(x,y+1):c})
NEW=[]
def save2(name,seq): save(name,seq); NEW.append(name)

# wave
wa=((4,-2),(7,-6)); wb=((4,-2),(5,-8))
w0=pose(hx=1,kh=1,eyes='happy',Ra=wa); w1=P(w0,Ra=wb)
save('wave',[F(w0,160),F(w1,160),F(w0,160),F(w1,160),F(P(w0,eyes='open'),160),F(P(w1,eyes='open'),160)])

# thinking
Q=[".##.","#..#","..#.",".#..","....",".#.."]
t=pose(hy=-1)
save('thinking',[F(P(t,look=-1),350),F(P(t,look=1),350),F(P(t,look=1,pdy=-0),120),
    F(P(t,kh=-1,hx=-1,look=1),140,front=glyph(Q,26,4,Y)),F(P(t,kh=-1,hx=-1,look=1),450,front=glyph(Q,26,2,Y)),
    F(P(t,kh=-1,hx=-1,look=1,eyes='flat'),120,front=glyph(Q,26,2,Y)),F(P(t,kh=-1,hx=-1,look=1),450,front=glyph(Q,26,3,Y))])

# party
conf=[(2,1,PINK),(6,9,BLUE),(10,4,GREEN),(14,13,Y),(18,6,PINK),(22,11,BLUE),(26,2,GREEN),(29,8,Y),(4,14,GREEN),(12,10,PINK),(20,0,Y),(27,13,BLUE),(8,6,Y),(16,2,BLUE),(24,5,PINK)]
def confetti(f):
    d={}
    for x,y0,c in conf:
        for base in (0,16):
            y=(y0+2*f)%16+base; xx=x+(1 if (f+y0)%4<2 else 0)
            d[(xx,y)]=c; d[(xx,y+1)]=c
    return d
pa=pose(by=1,hy=2,eyes='happy',La=PUMP,Ra=mr(PUMP)); pb=pose(hy=-2,eyes='happy',La=UP,Ra=mr(UP))
pc=pose(by=1,hy=2,eyes='happy',La=UP,Ra=mr(PUMP)); pd=pose(hy=-2,eyes='happy',La=PUMP,Ra=mr(UP))
save('party',[F(q,110,back=confetti(i),phase=i%2) for i,q in enumerate([pa,pa,pb,pb,pc,pc,pb,pb])])

# yes
CHK=["....#","...#.","#.#..",".#..."]
ck=glyph(CHK,25,3,GREEN)
y0=pose(eyes='happy',Ra=mr(PUMP))
save('yes',[F(P(y0,hy=0),140,front=ck),F(P(y0,hy=2,by=1),140,front=ck),F(P(y0,hy=0),140,front=ck),F(P(y0,hy=2,by=1),140,front=ck),F(P(y0,hy=-1),300,front=ck)])

# no
XG=["#...#",".#.#.","..#..",".#.#.","#...#"]
xg=glyph(XG,26,2,XRED)
n0=pose(eyes='flat')
save('no',[F(P(n0,hx=-2,look=-1),130,front=xg),F(P(n0,hx=0),80,front=xg),F(P(n0,hx=2,look=1),130,front=xg),F(P(n0,hx=0),80,front=xg),
           F(P(n0,hx=-2,look=-1),130,front=xg),F(P(n0,hx=0),80,front=xg),F(P(n0,hx=2,look=1),130,front=xg),F(P(n0,hx=0,eyes='open'),400,front=xg)])

# sleep
ZS=["####","..#.",".#..","####"]; ZB=["#####","...#.","..#..",".#...","#####"]
s0=pose(hy=2,droop=1,eyes='closed'); s1=P(s0,by=1,hy=3)
def zz(a=None,b=None):
    d={}
    if a: d.update(glyph(ZS,a[0],a[1],ICE))
    if b: d.update(glyph(ZB,b[0],b[1],ICE))
    return d
save('sleep',[F(s0,450,front=zz((24,7))),F(s0,450,front=zz((25,5))),F(s1,450,front=zz((24,7),(26,1))),F(s1,450,front=zz(None,(26,0)))])

# sad
sd=pose(hy=2,droop=1,eyes='sad')
def tear(y,x=11): return {(x,y):BLUE,(x,y+1):BLUE}
save('sad',[F(sd,220),F(sd,220,front=tear(21)),F(P(sd,hy=3),220,front=tear(24)),F(P(sd,hy=3),220,front=tear(27)),F(P(sd,hy=3,eyes='closed'),160),F(sd,400)])

# love
HB=[".#.#.","#####","#####",".###.","..#.."]; HS=["#.#","###",".#."]
lv=pose(eyes='heart')
save('love',[F(P(lv,hy=0),200,front=glyph(HS,27,6,PINK)),F(P(lv,hy=1,by=1),200,front=glyph(HB,26,3,PINK)),
             F(P(lv,hy=0),200,front=glyph(HB,26,2,PINK)),F(P(lv,hy=1,by=1),200,front=glyph(HS,27,2,PINK))])

def mixp(a,b,t):
    o={}
    for k in a:
        if k in ('La','Ra'): o[k]=tuple(tuple(a[k][j][i]+(b[k][j][i]-a[k][j][i])*t for i in range(2)) for j in range(2))
        elif k in ('eyes','look','kh'): o[k]=b[k]
        else: o[k]=a[k]+(b[k]-a[k])*t
    return o
def mir(p): return P(p,bx=-p['bx'],lean=-p['lean'],hx=-p['hx'],kh=-p['kh'],look=-p['look'],La=mr(p['Ra']),Ra=mr(p['La']))
DIAG=((-3,-1),(-6,-4))
ROCK=pose(lean=-2,hx=-3,kh=-1,look=-1,La=OUT,Ra=mr(UP)); BOUNCE=pose(by=1,hy=2,eyes='happy',La=PUMP,Ra=mr(PUMP))
SLIDE=pose(bx=1,hx=-3,hy=-1,look=-1,La=PUMP,Ra=mr(DIAG)); STRETCH=pose(hy=-4,eyes='happy',La=UP,Ra=mr(UP)); DROP=pose(by=1,hy=2,La=OUT,Ra=mr(OUT))
KEYS=[ROCK,BOUNCE,mir(ROCK),BOUNCE,SLIDE,mir(SLIDE),STRETCH,DROP]; seq=[]
for i,k in enumerate(KEYS):
    settle=P(k,hy=k['hy']+1) if i in (0,2,4,5) else (P(k,hy=k['hy']-1) if k is STRETCH else k)
    seq+=[F(mixp(KEYS[i-1],k,0.5),70,phase=i%2),F(k,130,phase=(i+1)%2),F(settle,130,phase=i%2)]
save('dance',seq)
def plant(x,y,stage,sway=0):
    g={}
    for c in range(x-2,x+3): g[(c,y)]=BROWN; g[(c,y+1)]=BROWN
    g[(x+2,y+1)]=DBROWN
    for c in range(x-1,x+2): g[(c,y+2)]=DBROWN
    if stage==1: g[(x,y-1)]=DGREEN
    elif stage==2:
        g[(x,y-1)]=DGREEN; g[(x,y-2)]=DGREEN; g[(x-1,y-3)]=GREEN; g[(x+1,y-3)]=GREEN
    elif stage==3:
        a=sway; g[(x,y-1)]=DGREEN; g[(x+a,y-2)]=DGREEN
        for c in (x-2+a,x-1+a,x+1+a,x+2+a): g[(c,y-4)]=GREEN; g[(c,y-3)]=GREEN
        g[(x-1+a,y-3)]=DGREEN; g[(x+1+a,y-3)]=DGREEN
    elif stage==4:
        for c,r in ((x,y-1),(x,y-2),(x,y-3),(x,y-4),(x+1,y-4),(x+2,y-3),(x-1,y-3)): g[(c,r)]=WILT
        for c,r in ((x+2,y-2),(x+3,y-2),(x+2,y-1),(x+3,y-1),(x-2,y-2)): g[(c,r)]=O
    return outlined(g)
def hold(p,stage,sway=0,extra=None):
    h=p['Ra'][1]; d=plant(OX+R(p['bx'])+17+R(h[0]),OY+12+R(p['by'])+R(h[1])-3,stage,sway)
    if extra: d.update(extra)
    return d
HOLD=((4,2),(5,0)); MIDH=((4,1),(6,-1)); HIGH=((4,0),(6,-3))
SPK=[".#.","###",".#."]
# plant-grow
gb=pose(bx=-2,look=1,Ra=HOLD); gh=P(gb,eyes='happy')
save('plant-grow',[F(gb,500,front=hold(gb,0)),F(gb,300,front=hold(gb,1)),F(gb,300,front=hold(gb,2)),
    F(P(gb,hy=-1),220,front=hold(gb,3)),
    F(P(gh,by=1,hy=1),240,front=hold(P(gh,by=1),3,1,glyph(SPK,28,10,Y))),F(gh,240,front=hold(gh,3,-1)),
    F(P(gh,by=1,hy=1),240,front=hold(P(gh,by=1),3,1,glyph(SPK,20,9,Y))),F(gh,500,front=hold(gh,3,0))])
# plant-gift
g0=pose(bx=-2,eyes='happy',kh=1,Ra=HOLD); g1=P(g0,Ra=MIDH); g2=P(g0,Ra=HIGH,hy=-1)
save('plant-gift',[F(g0,350,front=hold(g0,3)),F(g1,90,front=hold(g1,3)),
    F(g2,260,front=hold(g2,3,0,glyph(HS,25,7,PINK))),F(g2,260,front=hold(g2,3,0,glyph(HB,24,3,PINK))),F(g2,260,front=hold(g2,3,0,glyph(HS,25,2,PINK))),
    F(g1,90,front=hold(g1,3))])
# plant-dance
d0=pose(bx=-2,hx=-2,look=-1,eyes='happy',La=PUMP,Ra=HIGH); d1=pose(bx=-2,by=1,hy=2,eyes='happy',La=OUT,Ra=HOLD)
d2=pose(bx=-2,hx=2,look=1,eyes='happy',La=UP,Ra=HIGH)
seq=[]
for i,(q,sw) in enumerate(((d0,-1),(d1,0),(d2,1),(d1,0))):
    q2=P(q,hy=q['hy']+1)
    seq+=[F(q,130,phase=i%2,front=hold(q,3,sw)),F(q2,130,phase=(i+1)%2,front=hold(q2,3,sw))]
save('plant-dance',seq)
# plant-wilt
w0=pose(bx=-2,look=1,Ra=HOLD); w2=pose(bx=-2,hy=2,droop=1,look=1,eyes='sad',Ra=HOLD); w3=P(w2,hy=3)
save('plant-wilt',[F(w0,600,front=hold(w0,3)),F(P(w0,hy=-1),350,front=hold(w0,4)),F(w2,400,front=hold(w2,4)),
    F(w2,220,front=hold(w2,4,0,tear(21,9))),F(w3,220,front=hold(w3,4,0,tear(24,9))),F(w3,220,front=hold(w3,4,0,tear(27,9))),F(w2,500,front=hold(w2,4))])


# eyes
e=pose()
save('eyes',[F(P(e,look=-1,hx=-1),420),F(P(e,look=-1,hx=-1,eyes='flat'),90),F(P(e,look=-1,hx=-1),200),
             F(P(e,look=1,hx=1),420),F(P(e,look=1,hx=1,eyes='flat'),90),F(P(e,look=1,hx=1),200)])

# shipit
def jet(gy,f,full=True):
    d={}; y=29+gy
    rows=[(11,20,Y),(11,20,Y),(12,19,O),(12,19,O),(13,18,O),(14,17,XRED),(15,16,XRED)] if full else [(13,18,Y),(14,17,O)]
    for i,(a,b,c) in enumerate(rows):
        if full and i==6 and f%2: continue
        for x in range(a+(f%2 if i>2 else 0),b+1-(f%2 if i>2 else 0)): d[(x,y+i)]=c
    return d
def smoke(k):
    d={}
    for cx,cy in ((13-3*k,29),(18+3*k,29),(9-4*k,28-k),(22+4*k,28-k),(15,30)):
        for x in range(cx-2,cx+3):
            for y in range(cy-1,cy+2):
                if abs(x-cx)+abs(y-cy)<3: d[(x,y)]=L if y<cy else M
    return d
c0=pose(by=1,hy=2); up=pose(eyes='happy',La=UP,Ra=mr(UP))
seq=[F(c0,260,back=jet(0,0,False)),F(P(c0,hx=1),110,back=jet(0,1,False)),F(P(c0,hx=-1),110,back={**jet(0,0,False),**smoke(0)})]
for i,g in enumerate((-2,-7,-13,-20,-28)):
    seq.append(F(P(up,gy=g),85,phase=i%2,back={**smoke(min(i+1,3)),**jet(g,i)}))
seq.append(F(P(up,gy=-60),160,back=smoke(3))); seq.append(F(P(up,gy=-60),450))
save('shipit',seq)

# fire
HT=[2,4,3,5,2,4,6,3,5,3]
def flames(f):
    d={}
    for x in range(32):
        h=HT[(x*7+f*3)%len(HT)]+(4 if x<6 or x>25 else 2 if x<9 or x>22 else 0)
        for i in range(h): d[(x,31-i)]=XRED if i<h*0.34 else O if i<h*0.7 else Y
    return d
fa=pose(hx=-1,look=-1,La=UP,Ra=mr(PUMP)); fb=pose(hx=1,look=1,La=PUMP,Ra=mr(UP))
save('fire',[F(fa,110,front=flames(0)),F(P(fa,hy=1),110,front=flames(1)),F(fb,110,front=flames(2)),F(P(fb,hy=1),110,front=flames(3))])

# lol
def tears(a):
    pts=((4,15),(2,18)) if a else ((3,13),(4,19))
    d={}
    for x,y in pts:
        for yy in (y,y+1): d[(x,yy)]=BLUE; d[(31-x,yy)]=BLUE
    return d
l0=pose(eyes='happy',hy=-1); l1=pose(eyes='happy',by=1,hy=2)
save('lol',[F(P(l0,kh=1),100,front=tears(0)),F(l1,100,front=tears(1)),F(P(l0,kh=-1),100,front=tears(0)),F(l1,100,front=tears(1))])

# shrug
SHRUG=((-5,1),(-6,-2))
r0=pose(La=OUT,Ra=mr(OUT)); r1=pose(hy=1,kh=1,hx=1,eyes='flat',La=SHRUG,Ra=mr(SHRUG))
save('shrug',[F(r0,350),F(P(r1,hy=0,eyes='open'),80),F(r1,750),F(P(r1,hy=2),160),F(r1,300),F(P(r1,hy=0,eyes='open'),80)])

# salute
s0=pose(); sm=pose(Ra=((4,-1),(5,-4))); ss=pose(hy=-1,Ra=((5,-1),(4,-6)))
save('salute',[F(s0,300),F(sm,70),F(ss,650),F(P(ss,eyes='flat'),90),F(ss,300),F(sm,70)])

# mindblown
def burst(k,n=2):
    d={}
    for (bx_,by_),(dx,dy) in (((5,3),(-1,-1)),((15,3),(0,-1)),((25,3),(1,-1)),((4,9),(-1,0)),((26,9),(1,0))):
        for j in range(n): d[(bx_+dx*(k+j),by_+dy*(k+j))]=O if j==0 else Y
    return d
m0=pose()
save('mindblown',[F(m0,400),F(P(m0,hy=1,by=1),110),F(P(m0,hy=-4),70,front=burst(0,1)),F(P(m0,hy=-5),160,front=burst(0,3)),
                  F(P(m0,hy=-5),160,front=burst(1,3)),F(P(m0,hy=-5,eyes='flat'),90,front=burst(1)),F(P(m0,hy=-5),300),F(P(m0,hy=-2),90)])


# lightbulb
def bulb(lit,k=None):
    g={}
    for j,row in enumerate([".###.","#####","#####",".###."]):
        for i,ch in enumerate(row):
            if ch=='#': g[(13+i,2+j)]=Y if lit else L
    if lit: g[(14,3)]=W
    for x in (14,15,16): g[(x,6)]=M
    g[(15,7)]=D
    d=outlined(g)
    if k is not None:
        for (bx_,by_),(dx,dy) in (((10,4),(-1,0)),((20,4),(1,0)),((11,1),(-1,-1)),((19,1),(1,-1))):
            d[(bx_+dx*k,by_+dy*k)]=O; d[(bx_+dx*(k+1),by_+dy*(k+1))]=Y
    return d
b0=pose(hy=1); bh=pose(hy=1,eyes='happy',Ra=((4,-2),(6,-7)))
save('lightbulb',[F(P(b0,look=-1),450),F(P(b0,look=1),450),F(P(b0,eyes='flat'),100),F(b0,130,front=bulb(False)),
    F(bh,180,front=bulb(True,0)),F(bh,180,front=bulb(True,1)),F(bh,180,front=bulb(True,0)),F(bh,180,front=bulb(True,1)),F(bh,500,front=bulb(True))])

# magnify
def lens(cx,cy,mode,look=0):
    g={}
    for x in range(cx-7,cx+8):
        for y in range(cy-7,cy+8):
            dd=math.hypot(x-cx,y-cy)
            if dd<=4.4: g[(x,y)]=W if mode=='eye' else ICE
            elif dd<=5.5: g[(x,y)]=DBROWN
    if mode=='eye':
        for x in range(cx-2+look,cx+3+look):
            for y in range(cy-2,cy+3):
                if g.get((x,y))==W: g[(x,y)]=D if (abs(x-cx-look)<2 and abs(y-cy)<2) else K
        g[(cx-1+look,cy-1)]=L
        for i in (4,5,6): g[(cx+i,cy+i)]=BROWN; g[(cx+i+1,cy+i)]=BROWN
    else:
        g[(cx-2,cy-1)]=W; g[(cx-1,cy-2)]=W; g[(cx-2,cy-2)]=W
        for y in (cy+6,cy+7,cy+8): g[(cx,y)]=BROWN; g[(cx+1,y)]=BROWN
    return outlined(g)
ms=pose(bx=-3,look=1,Ra=((4,2),(6,0))); me=pose(bx=-3,hy=1,Ra=((5,2),(4,-1)))
save('magnify',[F(ms,450,front=lens(25,13,'glass')),F(me,220,front=lens(16,14,'eye',0)),F(P(me,look=-1),380,front=lens(16,14,'eye',-1)),
    F(P(me,look=1),380,front=lens(16,14,'eye',1)),F(P(me,look=-1),380,front=lens(16,14,'eye',-1)),F(me,300,front=lens(16,14,'eye',0))])

# facepalm
PALM=["#.#.#.#","#######","#######",".#####."]
fp=pose(by=1,hy=2,eyes='flat')
def palm(hx): return farm((26,21),(15+hx,15),sh=(23,23),palm=PALM)
save('facepalm',[F(pose(),350),F(pose(eyes='flat'),220),F(pose(eyes='flat'),70,front=farm((27,20),(23,18))),
    F(fp,600,front=palm(0)),F(P(fp,hx=-1),150,front=palm(-1)),F(P(fp,hx=1),150,front=palm(1)),F(P(fp,hx=-1),150,front=palm(-1)),
    F(fp,550,front=palm(0)),F(pose(eyes='flat'),70,front=farm((27,20),(23,18)))])

# sunglasses
def shades(ox,oy,t=None):
    g={}
    for c in range(2,19): g[(c,2)]=K
    for r in (3,4):
        for c in list(range(3,10))+list(range(11,18)): g[(c,r)]=K
    for c in list(range(4,9))+list(range(12,17)): g[(c,5)]=K
    if t is not None:
        for cx0 in (2,10):
            for c,r in ((cx0+2+t,3),(cx0+1+t,4)):
                if cx0+1<=c<=cx0+7: g[(c,r)]=ICE
    return {(OX+c+ox,OY+r+oy):v for (c,r),v in g.items()}
def puton(ox,oy,el):
    d=shades(ox,oy); d.update(farm(el,(OX+18+ox+1,OY+2+oy+1))); return d
c0=pose(); cu=pose(hy=-1)
cl=P(c0,look=1)
save('sunglasses',[F(cl,550,front=puton(4,9,(26,25))),F(cl,150,front=puton(4,7,(27,24))),F(cl,150,front=puton(3,5,(27,22))),
    F(c0,160,front=puton(2,4,(27,21))),F(c0,170,front=puton(2,3,(27,21))),F(c0,190,front=puton(1,2,(27,20))),F(c0,220,front=puton(1,1,(27,20))),
    F(c0,450,front=puton(0,0,(27,19))),F(c0,300,front=shades(0,0)),F(P(c0,hy=1),130,front=shades(0,1)),
    F(cu,90,front=shades(0,-1,0)),F(cu,90,front=shades(0,-1,2)),F(cu,90,front=shades(0,-1,4)),F(cu,600,front=shades(0,-1)),
    F(P(cu,hy=0),130,front=shades(0,0)),F(cu,90,front=shades(0,-1,0)),F(cu,90,front=shades(0,-1,2)),F(cu,90,front=shades(0,-1,4)),F(cu,700,front=shades(0,-1))])


def shades(ox,oy,t=None,col=ICE):
    g={}
    for c in range(2,19): g[(c,2)]=K
    for r in (3,4):
        for c in list(range(3,10))+list(range(11,18)): g[(c,r)]=K
    for c in list(range(4,9))+list(range(12,17)): g[(c,5)]=K
    if t is not None:
        for cx0 in (2,10):
            for c,r in ((cx0+2+t,3),(cx0+1+t,4)):
                if cx0+1<=c<=cx0+7: g[(c,r)]=col
    return {(OX+c+ox,OY+r+oy):v for (c,r),v in g.items()}
NEONS=[MAG,CYAN,NEON,PURP]
TRI=[0,1,2,3,4,3,2,1]
def lasers(i):
    d={}; a=TRI[i]; b=TRI[(i+4)%8]
    beams=[((0,0),(5+3*a,31)),((0,0),(31,12+4*a)),((31,0),(26-3*b,31)),((31,0),(0,12+4*b))]
    for n,(p0,p1) in enumerate(beams):
        for q in bres(p0,p1): d[q]=NEONS[(n+i//2)%4]; d[(q[0]+1,q[1])]=NEONS[(n+i//2)%4]
    return d
seq=[]
for i in range(8):
    half=i//4; down=(i%2==0)
    q=pose(by=1 if down else 0,hy=2 if down else -1,hx=-1 if half==0 else 1,
           La=UP if half==0 else PUMP,Ra=mr(PUMP) if half==0 else mr(UP))
    fr=shades(q['hx'],q['hy'],(i*2)%6,NEONS[i%4])
    for sgn,arm,col in ((-1,q['La'],NEON),(1,q['Ra'],MAG)):
        hx_=OX+(3 if sgn<0 else 17)+arm[1][0]; hy_=OY+12+q['by']+arm[1][1]
        tilt=(1 if down else -1)*sgn
        fr.update(outlined({p_:col for p_ in bres((hx_,hy_-2),(hx_+tilt,hy_-6))}))
    seq.append(F(q,100,phase=i%2,back=lasers(i),front=fr))
save('rave',seq)

# clap
def clap(tog,by=0):
    lx,rx=(14,17) if tog else (11,20); y=24+by; d={}
    for x,sg in ((lx,1),(rx,-1)):
        g={(x,y):M,(x,y-1):M,(x,y+1):M,(x+sg,y-1):M,(x+sg,y+1):M,(x-sg,y):Y,(x-2*sg,y):Y}
        d.update(outlined(g))
    return d
save2('clap',[F(pose(eyes='happy'),140,front=clap(False)),F(pose(eyes='happy',by=1,hy=1),140,front=clap(True,1))])

# loading
def dots(k):
    d={}
    for n,x in enumerate((9,14,19)):
        on=(n==k); d.update(outlined(rectd(x,4 if on else 5,x+2,6,BLUE if on else M)))
    return d
save2('loading',[F(pose(hy=1,pdy=-1),170,phase=i%2,front=dots(i%3)) for i in range(6)])

# plusone
SIGN=["WWWWWWWWW","WWWWWWgWW","WWgWWggWW","WgggWWgWW","WWgWWWgWW","WWWWWgggW","WWWWWWWWW"]
def sign(dy):
    d=outlined(rectd(26,8+dy,26,12+dy,BROWN)); d.update(outlined(G(SIGN,22,1+dy,{'W':WHITE,'g':DGREEN}))); return d
save2('plusone',[F(pose(eyes='happy',Ra=((3,-2),(4,-8))),260,front=sign(0)),F(pose(eyes='happy',hy=1,Ra=((3,-2),(4,-7))),260,front=sign(1))])

# bug
def bug(x,sq=False):
    if sq: return outlined(rectd(x-1,30,x+3,30,XRED))
    g=rectd(x,28,x+2,29,XRED); g[(x-1,29)]=K; g[(x+1,28)]=K
    return outlined(g)
bp=lambda lk:pose(pdy=1,look=lk)
save2('bug',[F(bp(1),200,front=bug(27)),F(bp(1),200,front=bug(22)),F(bp(0),200,front=bug(16)),F(bp(-1),200,front=bug(10)),F(bp(-1),200,front=bug(5)),F(bp(-1),200,front=bug(2)),
    F(pose(look=-1,pdy=1,La=((-3,0),(-5,-3))),130,front=bug(2)),F(pose(eyes='happy',La=((-3,1),(-5,6))),650,front=bug(2,True))])

# coffee
MUG=["bbbb.","WWWWW","WWWWW","WWWW."]
def mug(x,y,st=None):
    d=outlined(G(MUG,x,y,{'b':DBROWN,'W':WHITE}))
    if st is not None:
        for q in (((x+1,y-2),(x+2,y-4)) if st else ((x+2,y-2),(x+1,y-4))): d[q]=L
    return d
HM=((4,2),(5,0))
def drink():
    d=farm((27,21),(24,19)); d.update(mug(19,15)); return d
save2('coffee',[F(pose(hy=1,eyes='sad',Ra=HM),380,front=mug(25,18,0)),F(pose(hy=1,eyes='sad',Ra=HM),380,front=mug(25,18,1)),
    F(pose(hy=-1,eyes='closed'),650,front=drink()),F(pose(hy=-1,Ra=HM),220,front=mug(25,18,0)),
    F(pose(by=1,hy=1,eyes='happy',Ra=HM),240,front=mug(25,19,1)),F(pose(eyes='happy',Ra=HM),450,front=mug(25,18,0))])

# lowbattery
def batt(on):
    g=rectd(11,2,18,6,L); g.update(rectd(12,3,17,5,K)); g.update(rectd(19,3,19,5,L))
    if on: g.update(rectd(12,3,13,5,XRED))
    return outlined(g)
save2('lowbattery',[F(pose(hy=1,droop=1,eyes='sad'),450,front=batt(True)),F(pose(hy=2,droop=1,eyes='sad'),450,front=batt(False)),
    F(pose(hy=3,by=1,droop=1,eyes='closed'),450,front=batt(True)),F(pose(hy=3,by=1,droop=1,eyes='closed'),450,front=batt(False))])

# brb
roll=lambda b,ph:F(pose(bx=b,hx=b,look=1),80,phase=ph)
save2('brb',[F(pose(),450),F(pose(look=1),220)]+[roll(b,i%2) for i,b in enumerate((3,8,14,21,29))]+[F(pose(bx=40,hx=40),380)]
    +[roll(b,i%2) for i,b in enumerate((-29,-21,-14,-8,-3))]+[F(pose(eyes='happy'),550)])

# nervous
DROPG=[".#.","###","###"]
def sweat(y):
    d=outlined(G(DROPG,25,y,{'#':BLUE})); d[(25,y+1)]=ICE; return d
save2('nervous',[F(pose(look=(-1 if (i//2)%2==0 else 1),hx=i%2),130,front=sweat(9+i)) for i in range(8)])

# angry
def brows(p):
    loc={}
    for cx0,left in ((2,True),(10,False)):
        for c in range(cx0+1,cx0+8):
            o=(c-cx0-1) if left else (cx0+7-c)
            d=1+o//2
            for r in range(1,d+1):
                if r==1 and c in (cx0+1,cx0+7): continue
                loc[(c,r)]=K if r==d else L
        loc[(cx0+4,4)]=XRED; loc[(cx0+5,4)]=XRED
    return hl(p,loc)
PUFF=[".##","###"]
seq=[]
for i in range(4):
    hi=((-4,0),(-4,-5)); a=i%2; b=(i+1)%2
    p=pose(hx=(-1,0,1,0)[i],La=hi if a else PUMP,Ra=mr(PUMP if a else hi))
    fr=brows(p)
    fr.update(outlined(G(PUFF,4-a,7-2*a,{'#':WHITE}))); fr.update(outlined(G(PUFF,24+b,7-2*b,{'#':WHITE})))
    seq.append(F(p,100,front=fr))
save2('angry',seq)

# dizzy
def dz(p,i):
    loc={}; pos=[(3,2),(5,3),(3,5),(1,3)]
    for cx0,k in ((2,i%4),(10,(-i)%4)):
        dx,dy=pos[k]; loc.update({(cx0+dx+a,dy+b):K for a in (0,1) for b in (0,1)})
    return hl(p,loc)
def stars(i):
    d={}
    for k in range(3):
        a=math.radians(i*45+k*120); d.update(plus(R(15+10*math.cos(a)),R(5+2*math.sin(a))))
    return d
seq=[]
for i in range(8):
    p=pose(eyes='none',hx=(-1,0,1,0)[i%4],hy=i%2)
    fr=stars(i); fr.update(dz(p,i)); seq.append(F(p,110,front=fr))
save2('dizzy',seq)

# peek
pk=lambda g,lk=0,e='open':P(pose(look=lk,eyes=e),gy=g)
save2('peek',[F(pk(24),380),F(pk(19),80),F(pk(15),80),F(pk(13,-1),450),F(pk(13,1),450),F(pk(13,1,'flat'),90),F(pk(13,0),260),F(pk(17),80),F(pk(21),80)])

# highfive
BURST=["#.#.#",".###.","#####",".###.","#.#.#"]
h0=pose(La=OUT,Ra=mr(OUT)); hm=pose(La=OUT,Ra=((4,-1),(6,-4))); hu=pose(eyes='happy',hy=-1,La=OUT,Ra=((4,-3),(6,-9)))
save2('highfive',[F(h0,320),F(hm,70),F(hu,150,front=outlined(G(BURST,26,7,{'#':Y}))),F(P(hu,by=1,hy=1),150,front=plus(28,9)),F(hu,320),F(hm,70)])

# bow
save2('bow',[F(pose(),420),F(pose(hy=1,eyes='flat'),70),F(pose(hy=3,by=1,eyes='closed'),780),F(pose(hy=1,eyes='flat'),70),F(pose(eyes='happy'),480)])

# popcorn
TUB=[".oWoWo.","rWrWrWr","rWrWrWr","rWrWrWr","rWrWrWr",".WrWrW.",".WrWrW."]
def tub(piece=None):
    g=G(TUB,22,15,{'r':XRED,'W':WHITE,'o':Y}); g[(24,14)]=WHITE; g[(26,14)]=Y
    d=outlined(g)
    if piece: d.update(outlined({piece:WHITE}))
    return d
pc_=lambda lk,hy=0:pose(bx=-2,hx=-2,look=lk,hy=hy,Ra=((4,2),(5,0)))
seq=[]
for lk in (-1,1):
    seq+=[F(pc_(lk),300,front=tub()),F(pc_(lk),90,front=tub((23,12))),F(pc_(lk),90,front=tub((19,11))),F(pc_(lk),90,front=tub((15,15))),
          F(pc_(lk,1),130,front=tub()),F(pc_(lk),130,front=tub()),F(pc_(lk,1),130,front=tub())]
save2('popcorn',seq)

# trophy
CUP=[".yyyyyyy.","hyyyyyyyh","hyyyyyyyh",".yyyyyyy.","..yyyyy..","....y....","...yyy...","..ooooo.."]
def cup(x,y,sp=None):
    g=G(CUP,x-4,y-8,{'h':O,'y':Y,'o':O}); g[(x-2,y-8)]=WHITE; g[(x-2,y-7)]=WHITE; g[(x-1,y-6)]=WHITE
    d=outlined(g)
    if sp: d.update(plus(*sp))
    return d
ta=pose(bx=-2,hx=-2,eyes='happy',by=1,hy=1,La=PUMP,Ra=((4,-2),(6,-7))); tb=pose(bx=-2,hx=-2,eyes='happy',hy=-1,La=UP,Ra=((4,-3),(6,-9)))
save2('trophy',[F(ta,230,front=cup(26,16)),F(tb,230,front=cup(26,13,(17,3))),F(ta,230,front=cup(26,16)),F(tb,230,front=cup(26,13,(13,5)))])

# typing
def laptop(i):
    g=rectd(23,29,30,30,L); g.update(rectd(23,29,30,29,WHITE)); g.update(rectd(29,21,30,28,D))
    g.update(rectd(28,22,28,27,ICE))
    for y,c in (((23,GREEN),(26,CYAN)) if i%2==0 else ((24,CYAN),(25,GREEN))): g[(28,y)]=c
    return outlined(g)
save2('typing',[F(pose(bx=-3,hx=-3,hy=1,pdy=1,look=1,Ra=((4,2),(6,4+i%2))),130,front=laptop(i)) for i in range(4)])

# headphones
def phones(p):
    loc={(c,-2):XRED for c in range(3,18)}
    for q in ((2,-1),(3,-1),(17,-1),(18,-1),(1,0),(19,0)): loc[q]=XRED
    for r in range(1,7):
        for c in (0,1): loc[(c,r)]=XRED; loc[(20-c,r)]=XRED
    return outlined(hl(p,loc))
NOTE=[".##",".#.",".#.","##.","##."]
def note(x,y,c): return outlined(G(NOTE,x,y,{'#':c}))
seq=[]
for i,(nts) in enumerate(([(27,4,MAG)],[(27,1,MAG),(1,5,CYAN)],[(1,2,CYAN)],[(27,6,MAG)])):
    p=pose(eyes='happy',hy=2 if i%2 else 0,by=1 if i%2 else 0)
    fr=phones(p)
    for x,y,c in nts: fr.update(note(x,y,c))
    seq.append(F(p,210,front=fr))
save2('headphones',seq)

# money
DOLLAR=["..#..","#####","#.#..","#####","..#.#","#####"]
def cash(p):
    loc={}
    for cx0 in (2,10): loc.update({(cx0+2+i,1+j):DGREEN for j,row in enumerate(DOLLAR) for i,ch in enumerate(row) if ch=='#'})
    return hl(p,loc)
COIN=[".##.","####","####",".##."]
def coin(x,y):
    d=outlined(G(COIN,x,y,{'#':Y})); d[(x+1,y+1)]=WHITE; d[(x+2,y+2)]=O; return d
PATH=[(6,17),(4,12),(3,8),(2,6),(2,8),(2,12)]
seq=[]
for i in range(6):
    p=pose(eyes='none',by=i%2,hy=i%2,La=PUMP,Ra=mr(PUMP))
    fr=coin(*PATH[i]); x,y=PATH[(i+3)%6]; fr.update(coin(28-x,y)); fr.update(cash(p)); seq.append(F(p,120,front=fr))
save2('money',seq)

# trashcube
CUBE=["mdmlmd","dlmdmm","mmdmld","dmlmdm","mdmmdl","lmdmmd"]
def cube(y):
    g=G(CUBE,13,y,{'m':M,'d':D,'l':L}); g[(14,y+1)]=XRED; g[(17,y+3)]=BLUE; g[(15,y+4)]=GREEN
    return outlined(g)
sq=lambda j:pose(by=1,hy=2,hx=j,bx=j,eyes='flat')
save2('trashcube',[F(pose(),350),F(sq(0),140),F(sq(-1),80),F(sq(1),80),F(sq(-1),80),F(sq(1),80),
    F(pose(hy=-1),120,front=cube(22)),F(pose(eyes='happy'),160,front=cube(25)),F(pose(eyes='happy',by=1,hy=1),160,front=cube(25)),F(pose(eyes='happy'),650,front=cube(25))])


HM=((4,2),(5,0))
HB=[".#.#.","#####","#####",".###.","..#.."]; HS=["#.#","###",".#."]
# boxup
def cube(dx=0):
    g=rectd(8+dx,20,22+dx,29,Y)
    for n,ch in enumerate("dmmllooooddo"): g[(10+dx+n,22)]={'d':D,'m':M,'l':L,'o':O}[ch]
    g.update(rectd(16+dx,26,18+dx,26,RD))
    for y in range(22,30):
        for x in (6,7): g[(x+dx,y)]=M if y%2 else D; g[(30-x+dx,y)]=M if y%2 else D
    return outlined(g)
OFF=P(pose(),gy=40); tuck=lambda h:pose(hy=h,by=1,eyes='flat')
save2('boxup',[F(pose(),420),F(tuck(2),90),F(tuck(5),90),F(OFF,130,front=cube(0)),F(OFF,100,front=cube(-1)),F(OFF,100,front=cube(1)),
    F(OFF,100,front=cube(-1)),F(OFF,480,front=cube(0)),F(tuck(5),80),F(pose(hy=-2,eyes='happy'),170),F(pose(eyes='happy'),480)])

# butterfly
BFO=["pp.pp","ppkpp",".pkp."]; BFC=[".p.p.",".pkp.","..k.."]
def bfly(x,y,o): return outlined(G(BFO if o else BFC,x-2,y-2,{'p':PINK,'k':K}))
def xeyes(p):
    loc={}
    for pc in (6,12):
        for r in range(1,5):
            for c in range(pc,pc+4): loc[(c,r)]=K
        loc[(pc+1,2)]=L; loc[(pc+2,2)]=D; loc[(pc+1,3)]=D; loc[(pc+2,3)]=D
    return hl(p,loc)
seq=[F(pose(look=1,pdy=-1),130,front=bfly(x,y,o)) for x,y,o in ((29,3,1),(25,6,0),(21,5,1),(18,8,0))]
pn=pose(eyes='none')
for o,d in ((1,320),(0,200),(1,320),(0,200),(1,320)):
    fr=bfly(15,9,o); fr.update(xeyes(pn)); seq.append(F(pn,d,front=fr))
seq+=[F(pose(look=-1,pdy=-1),130,front=bfly(x,y,o)) for x,y,o in ((11,6,1),(6,4,0),(2,2,1))]
seq.append(F(pose(eyes='happy'),350))
save2('butterfly',seq)

# balloon
BAL=[".####.","######","######","######","######",".####.","..##.."]
def balloon(dx,g):
    x=22+dx; y=1+g; d={}
    for q in bres((x+3,y+7),(25,15+g)): d[q]=M
    d.update(outlined(G(BAL,x,y,{'#':XRED}))); d[(x+1,y+1)]=WHITE; d[(x+1,y+2)]=WHITE
    return d
seq=[]
for g,dx in zip((0,-1,-3,-4,-4,-3,-1,0),(0,0,1,1,0,-1,-1,0)):
    p=P(pose(bx=-2,hx=-2,look=1,pdy=-1,eyes='happy' if g<=-3 else 'open',Ra=((4,-2),(5,-5))),gy=g)
    seq.append(F(p,150,front=balloon(dx,g)))
save2('balloon',seq)

# shy
PALMS=["#.#.#","#####","#####",".###."]
def hands(off,hy):
    d=farm((3,19),(11-off,13+hy),sh=(7,22),palm=PALMS); d.update(farm((27,19),(19+off,13+hy),sh=(23,22),palm=PALMS)); return d
def blush(p): return hl(p,{(4,6):PINK,(5,6):PINK,(15,6):PINK,(16,6):PINK})
def shyf(p,d,off=None):
    fr=blush(p)
    if off is not None: fr.update(hands(off,1))
    return F(p,d,front=fr)
cv=pose(hy=1,eyes='flat'); pk2=pose(hy=1)
save2('shy',[F(pose(),350),shyf(pose(pdy=1),320),shyf(cv,650,0),shyf(pk2,450,3),shyf(cv,350,0),shyf(P(pk2,eyes='happy'),600,3)])

# birthday
def hat(p):
    loc={(10,-6):Y,(10,-5):MAG}
    for r,(a,b),c in ((-4,(9,11),CYAN),(-3,(9,11),MAG),(-2,(8,12),CYAN),(-1,(8,12),MAG)):
        for x in range(a,b+1): loc[(x,r)]=c
    return outlined(hl(p,loc))
def cake(fl):
    g=rectd(23,19,27,20,MAG); g.update(rectd(24,21,26,21,MAG)); g[(24,19)]=PURP; g[(26,19)]=PURP; g[(24,20)]=PURP; g[(26,20)]=PURP
    g.update(rectd(23,18,27,18,WHITE)); g.update(rectd(24,17,26,17,WHITE)); g[(24,18)]=PINK; g[(27,18)]=PINK
    g[(25,15)]=CYAN; g[(25,16)]=CYAN
    if fl=='a': g[(25,13)]=Y; g[(25,14)]=O
    elif fl=='b': g[(25,14)]=Y
    elif fl=='blow': g[(26,14)]=O
    d=outlined(g)
    if fl=='s1': d[(25,13)]=L
    if fl=='s2': d[(26,11)]=L; d[(25,12)]=L
    return d
bd=lambda fl,d,**k:(lambda p:F(p,d,front={**cake(fl),**hat(p)}))(pose(bx=-2,Ra=HM,**{'hx':-2,**k}))
save2('birthday',[bd('a',230),bd('b',230),bd('a',230),bd('b',230),bd('blow',160,hx=-1,eyes='flat',look=1),bd('s1',220,hx=-1,look=1),bd('s2',300,eyes='happy'),bd(None,450,eyes='happy')])

# umbrella
def canopy():
    g={(15,4):BLUE}
    for y,(a,b) in ((5,(11,19)),(6,(8,22)),(7,(6,24)),(8,(5,25)),(9,(5,25))):
        for x in range(a,b+1):
            if y==9 and (x-5)%5==4: continue
            g[(x,y)]=BLUE if ((x-5)//5)%2==0 else CYAN
    d=outlined(g); d.update(outlined({(15,10):BROWN,(15,11):BROWN})); d.update(outlined(g)); return d
def rain(f):
    d={}
    for x,y0 in ((1,0),(3,14),(28,6),(30,20),(2,24),(29,28)):
        y=(y0+4*f)%32; d[(x,y)]=BLUE; d[(x,y+1)]=BLUE
    for x,lim,off in ((9,5,0),(15,3,3),(21,5,5)):
        y=(off+2*f)%8
        if y+1<lim: d[(x,y)]=BLUE; d[(x,y+1)]=BLUE
        elif y<lim+2: d[(x-2,lim-1)]=BLUE; d[(x+2,lim-1)]=BLUE
    return d
save2('umbrella',[F(pose(hy=2,look=(0,0,1,1,0,0,-1,-1)[f],eyes='happy' if f in (2,3) else 'open'),110,back=rain(f),front=canopy()) for f in range(8)])

# present
def box(dx=0,lid=0,lx=0,heart=None):
    g=rectd(22+dx,17,28+dx,21,PURP); g.update(rectd(25+dx,17,25+dx,21,Y)); d=outlined(g)
    if heart: d.update(outlined(G(heart[0],heart[1],heart[2],{'#':PINK})))
    if lid is not None:
        l=rectd(22+dx+lx,15-lid,28+dx+lx,16-lid,MAG); l[(25+dx+lx,15-lid)]=Y; l[(25+dx+lx,16-lid)]=Y; l[(24+dx+lx,14-lid)]=Y; l[(26+dx+lx,14-lid)]=Y
        d.update(outlined(l))
    return d
pp=pose(bx=-2,hx=-2,look=1,Ra=HM); ph=P(pp,eyes='heart')
save2('present',[F(pp,380,front=box())]+[F(pp,80,front=box(dx)) for dx in (-1,1,-1,1)]+
    [F(pp,140,front=box(0,3,1,(HS,24,13))),F(ph,200,front=box(0,8,2,(HB,23,9))),F(P(ph,by=1,hy=1),200,front=box(0,None,0,(HB,23,5))),F(ph,420,front=box(0,None,0,(HB,23,3)))])

# headpat
HAND=[".#####.","#######","#######",".#####."]
def pat(y,p=None):
    d=outlined(rectd(14,0,17,y-1,BLUE)); d.update(outlined(G(HAND,12,y,{'#':WHITE})))
    for x in (14,16):
        for yy in (y+2,y+3): d[(x,yy)]=K
    if p: d.update(blush(p))
    return d
hp=pose(eyes='happy'); hd_=pose(hy=1,eyes='happy')

# bird
BIRD=[".bbb.","obkbb",".iibt"]
def bird(x,y,flap=False):
    g=G(BIRD,x,y,{'b':BLUE,'o':O,'k':K,'i':ICE,'t':PURP})
    if flap: g[(x+2,y-1)]=BLUE; g[(x+3,y-1)]=BLUE
    return outlined(g)
up=lambda lk,e='open':pose(pdy=-1,look=lk,eyes=e)
save2('bird',[F(pose(look=1),130,front=bird(26,2,True)),F(up(1),130,front=bird(22,4)),F(up(1),450,front=bird(17,7)),F(up(0),110,front=bird(14,4,True)),
    F(up(-1),450,front=bird(9,7)),F(up(-1,'flat'),100,front=bird(9,7)),F(up(-1),320,front=bird(9,6)),F(up(-1),130,front=bird(4,4,True)),F(pose(look=-1),130,front=bird(0,1)),F(pose(eyes='happy'),320)])

# scarf
def scarf(i):
    g=rectd(11,18,19,19,XRED)
    for x in range(11,20):
        if (x-11)%3==1: g[(x,18)]=WHITE; g[(x,19)]=WHITE
    for n,x in enumerate(range(20,27)):
        y=18+((n//2+i)%2); c=WHITE if n%3==1 else XRED; g[(x,y)]=c; g[(x,y+1)]=c
    return outlined(g)
def snow(f):
    d={}
    for x0,y0 in ((2,1),(7,9),(12,3),(18,12),(24,6),(29,14),(4,13),(27,0),(15,7),(21,15)):
        for base in (0,16): d[(x0+(f//2)%2,(y0+2*f)%16+base)]=BLUE
    return d
save2('scarf',[F(pose(hx=i%2,eyes='flat') if i<5 else pose(eyes='happy'),110,back=snow(i),front=scarf(i)) for i in range(8)])

# bills
BILLH=["ggggg","ggdgg","ggggg"]; BILLV=["ggg","ggg","gdg","ggg","ggg"]
def bill(x,y,v=0): return outlined(G(BILLV if v else BILLH,x,y,{'g':GREEN,'d':DGREEN}))


# money-makeitrain
PATH=[(25,13),(26,9),(25,5),(23,2),(20,0),(17,-3)]
def stackat(x0,hy_):
    g=rectd(x0,hy_-4,x0+4,hy_-1,GREEN)
    for x in range(x0,x0+5): g[(x,hy_-3)]=DGREEN; g[(x,hy_-1)]=DGREEN
    return outlined(g)
seq=[]
for f in range(8):
    ru=f%2==1; lu=f%2==0
    p=pose(La=((-4,1),(-5,-1)) if lu else ((-4,2),(-5,0)),Ra=((4,1),(5,-1)) if ru else HM)
    fr=shades(p['hx'],p['hy'],(f*2)%6 if f<3 else None)
    fr.update(stackat(25,21 if ru else 22)); fr.update(stackat(1,21 if lu else 22))
    for ph in (0,3,6):
        i=(f+ph)%8
        if i<6:
            x,y=PATH[i]; v=(f+ph)%2; fr.update(bill(x,y,v))
        j=(f+ph+4)%8
        if j<6:
            x,y=PATH[j]; v=(f+ph+1)%2; fr.update(bill(31-x-(2 if v else 4),y,v))
    seq.append(F(p,120,front=fr))
save('money-makeitrain',seq)

print(f'wrote {len(ALL)} GIFs to {out}')
