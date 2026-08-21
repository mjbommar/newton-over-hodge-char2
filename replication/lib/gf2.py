"""GF(2^a) arithmetic, P^1 maps and the degree-3 classification.

Rescued verbatim from workstream 20's `code/audit05.py` (the adversarial
verifier's own GF(2^a) implementation, written from scratch for the Lemma B
audit).  The only edit is the split into a module: the printing/asserting part
now lives in `verify-lemma-b/check_degree3_maps.py`, so importing this file
computes nothing.
"""
# ---------- GF(2^a) as ints, poly basis ----------
IRR={1:0b11,2:0b111,3:0b1011,4:0b10011,5:0b100101,6:0b1000011}
class GF:
    def __init__(s,a): s.a=a; s.q=1<<a; s.irr=IRR[a]
    def mul(s,x,y):
        r=0
        while y:
            if y&1: r^=x
            y>>=1; x<<=1
            if x>>s.a & 1: x^=s.irr
        return r
    def pw(s,x,n):
        r=1
        while n:
            if n&1: r=s.mul(r,x)
            x=s.mul(x,x); n>>=1
        return r
    def inv(s,x): return s.pw(x,s.q-2)
INF='oo'
def ev(F,num,den,z):
    """evaluate (num,den) as lists of coeffs (low->high) at z in P^1."""
    def p(c,z):
        r=0
        for co in reversed(c): r=F.mul(r,z)^co
        return r
    if z is INF:
        dn,dd=len(num)-1,len(den)-1
        while dn>=0 and num[dn]==0: dn-=1
        while dd>=0 and den[dd]==0: dd-=1
        if dn>dd: return INF
        if dn<dd: return 0
        return F.mul(num[dn],F.inv(den[dd]))
    n,d=p(num,z),p(den,z)
    if d==0: return INF if n!=0 else None
    return F.mul(n,F.inv(d))
def polmul(F,A,B):
    C=[0]*(len(A)+len(B)-1)
    for i,x in enumerate(A):
        if x:
            for j,y in enumerate(B):
                if y: C[i+j]^=F.mul(x,y)
    return C
def cube(F,A): return polmul(F,polmul(F,A,A),A)

def classify(a):
    """Enumerate degree-3 tame h: P^1->P^1 over GF(2^a) with:
       Branch(h) subset {0,1,oo}; h({0,1,oo}) subset {0,1,oo}; h(1)=0;
       h^{-1}(1) a single point alpha of index 3 with alpha not in {0,1,oo}.
       h = mu( ((z-alpha)/(z-beta))^3 ), mu in PGL2 with mu(0)=1, mu(oo)=v in {0,oo}."""
    F=GF(a); q=F.q; found=[]
    pts=list(range(q))+[INF]
    for alpha in range(q):
        if alpha in (0,1): continue
        for beta in pts:
            if beta==alpha: continue
            # N/D = ((z-alpha)/(z-beta))^3   (char 2: z-x = z+x)
            N=cube(F,[alpha,1])
            D=[1] if beta is INF else cube(F,[beta,1])
            for v in (0,INF):
                for w in range(q):          # mu(1) = w
                    if w==1 or (v==0 and w==0): continue
                    # mu: 0->1, oo->v, 1->w   (Mobius through 3 points)
                    # build mu(y) = (A y + B)/(C y + E)
                    if v is INF:
                        # mu(0)=1 -> B/E=1 ; mu(oo)=oo -> C=0 ; mu(1)=w -> (A+B)/E=w
                        E=1; B=1; C=0; A=w^1
                        if A==0: continue
                    else:
                        # v=0: mu(oo)=0 -> A=0 ; mu(0)=1 -> B/E=1 ; mu(1)=w -> B/(C+E)=w
                        A=0; B=1; E=1
                        if w==0: continue
                        C=F.mul(B,F.inv(w))^E
                        if C==0: continue
                    num=[F.mul(A,c) for c in N]
                    dn=[F.mul(B,c) for c in D]
                    num=[num[i]^(dn[i] if i<len(dn) else 0) for i in range(max(len(num),len(dn)))]
                    den1=[F.mul(C,c) for c in N]; den2=[F.mul(E,c) for c in D]
                    den=[ (den1[i] if i<len(den1) else 0)^(den2[i] if i<len(den2) else 0)
                          for i in range(max(len(den1),len(den2)))]
                    ok=True
                    if ev(F,num,den,1)!=0: ok=False
                    if ok:
                        for z in (0,INF):
                            r=ev(F,num,den,z)
                            if r not in (0,1,INF): ok=False; break
                    if ok and ev(F,num,den,alpha)!=1: ok=False
                    if ok: found.append((alpha,beta,v,w))
    return F,found
