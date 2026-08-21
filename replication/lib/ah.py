from sympy import Rational, Integer, nsimplify
from fractions import Fraction as F

# Field K = Q(pi), pi^2 = -p^? ; we handle general: pi^e = c (c rational int)
# For p=2: pi^2 = -2.  Represent elements as tuples of Fractions of length e in basis 1,pi,...,pi^{e-1}
class NF:
    def __init__(self, e, c):   # pi^e = c
        self.e=e; self.c=F(c)
    def zero(self): return [F(0)]*self.e
    def one(self):
        z=self.zero(); z[0]=F(1); return z
    def frompi(self,k,coef=1):
        # coef * pi^k reduced
        q,r = divmod(k,self.e)
        z=self.zero(); z[r]=F(coef)*self.c**q
        return z
    def add(self,a,b): return [x+y for x,y in zip(a,b)]
    def smul(self,s,a): return [F(s)*x for x in a]
    def mul(self,a,b):
        out=self.zero()
        for i,x in enumerate(a):
            if x==0: continue
            for j,y in enumerate(b):
                if y==0: continue
                k=i+j
                if k>=self.e: out[k-self.e]+= x*y*self.c
                else: out[k]+= x*y
        return out

def v2(fr, p=2):
    if fr==0: return None
    n,d = fr.numerator, fr.denominator
    v=0
    while n% p==0: n//=p; v+=1
    while d% p==0: d//=p; v-=1
    return v

def val(nf, a, p, e):
    # normalized so v(p)=1 ; v(pi)=1/e ; returns Fraction
    best=None
    for i,x in enumerate(a):
        if x==0: continue
        vv = F(v2(x,p)) + F(i,e)
        if best is None or vv<best: best=vv
    return best   # None => zero

def exp_series(nf, fcoef, N):
    """theta = exp(f), f = sum_{n>=1} fcoef[n] x^n (list of NF elements, index 0 unused/zero).
       Uses theta' = f' theta:  n*c_n = sum_{k=1}^{n} k*f_k*c_{n-k}."""
    c=[nf.zero() for _ in range(N+1)]
    c[0]=nf.one()
    for n in range(1,N+1):
        acc=nf.zero()
        for k in range(1,n+1):
            if all(y==0 for y in fcoef[k]): continue
            acc = nf.add(acc, nf.smul(k, nf.mul(fcoef[k], c[n-k])))
        c[n]=nf.smul(F(1,n), acc)
    return c

def ah_pi(p, N):
    """theta(x) = AH(pi x) = exp( sum_{i>=0} pi^{p^i} x^{p^i} / p^i ), pi^{p-1} = -p."""
    e=p-1; nf=NF(e, -p)
    f=[nf.zero() for _ in range(N+1)]
    i=0
    while p**i<=N:
        n=p**i
        f[n]=nf.frompi(n, F(1,p**i))
        i+=1
    return nf, exp_series(nf,f,N)

def dwork_theta(p,N):
    """theta(x)=exp(pi(x-x^p))"""
    e=p-1; nf=NF(e,-p)
    f=[nf.zero() for _ in range(N+1)]
    f[1]=nf.frompi(1,1)
    if p<=N: f[p]=nf.frompi(1,-1)
    return nf, exp_series(nf,f,N)

def table(name,p,nf,c,N,e):
    print("="*72); print(name, " p=",p," (v normalized v(p)=1; w = e*v so w(pi)=1, e=%d)"%e)
    print(" k   coeff(in basis 1,pi,..)                v(c_k)      v/k        w/k")
    rates=[]
    for k in range(0,N+1):
        vv=val(nf,c[k],p,e)
        if vv is None:
            print("%3d  0"%k); continue
        r=vv/k if k else None
        rates.append((k,r))
        cs=" + ".join("%s*pi^%d"%(x,i) for i,x in enumerate(c[k]) if x!=0)
        print("%3d  %-38s %-10s %-10s %s"%(k,cs[:38],vv,(str(r) if r is not None else "-"),(str(e*r) if r is not None else "-")))
    if rates:
        m=min(r for k,r in rates)
        km=[k for k,r in rates if r==m]
        print("MIN v(c_k)/k over 1..%d = %s  attained at k=%s   -> in pi-units w/k = %s"%(N,m,km,e*m))
    return

def ah_gen(p, N, e, c=None):
    """theta(x)=AH(pi x)=exp( sum_i pi^{p^i} x^{p^i}/p^i ) with pi^e = c (default -p)."""
    if c is None: c=-p
    nf=NF(e,c)
    f=[nf.zero() for _ in range(N+1)]
    i=0
    while p**i<=N:
        n=p**i
        f[n]=nf.frompi(n, F(1,p**i))
        i+=1
    return nf, exp_series(nf,f,N)
