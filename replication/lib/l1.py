from fractions import Fraction as F
from ah import v2, NF, exp_series

def AH_coeffs(p,N):
    """AH(x)=exp(sum_{i>=0} x^{p^i}/p^i) as exact rationals."""
    f=[F(0)]*(N+1); i=0
    while p**i<=N: f[p**i]=F(1,p**i); i+=1
    c=[F(0)]*(N+1); c[0]=F(1)
    for n in range(1,N+1):
        acc=F(0)
        for k in range(1,n+1):
            if f[k]: acc+= k*f[k]*c[n-k]
        c[n]=acc/n
    return c

def AH_product(p,N):
    """prod_{n>=1,(n,p)=1} (1-x^n)^{-mu(n)/n}, truncated; exact rationals.
       (1-y)^{-a} = sum_k binom(a+k-1,k) y^k."""
    from sympy import mobius, binomial, Rational
    res=[F(0)]*(N+1); res[0]=F(1)
    for n in range(1,N+1):
        if n%p==0: continue
        mu=int(mobius(n))
        if mu==0: continue
        a=F(-mu,n)     # exponent is -mu(n)/n, series (1-x^n)^{-mu/n} = (1-y)^{a'} ... careful
        # (1-x^n)^{e} with e = -mu(n)/n ; expand: sum_k binom(e,k) (-1)^k x^{nk}
        e=Rational(-mu,n)
        fac=[F(0)]*(N+1); 
        k=0
        while n*k<=N:
            b=binomial(e,k)*(-1)**k
            fac[n*k]=F(int(b.p),int(b.q))
            k+=1
        new=[F(0)]*(N+1)
        for i,x in enumerate(res):
            if x==0: continue
            for j in range(0,N+1-i,1):
                if fac[j]==0: continue
                new[i+j]+= x*fac[j]
        res=new
    return res

if __name__ == "__main__":
    p=2; N=40
    c=AH_coeffs(p,N); d=AH_product(p,N)
    print("AH exp-form == product-form up to x^%d ? %s"%(N, c==d))
    bad=[(k,c[k]) for k in range(N+1) if v2(c[k],p) is not None and v2(c[k],p)<0]
    print("non-integral AH coefficients at p=2 (should be empty):", bad)
    print("AH(x) p=2 coefficients a_k and v_2(a_k):")
    units=[]
    for k in range(0,N+1):
        vv = v2(c[k],p)
        if vv==0: units.append(k)
        print("  a_%-3d = %-28s v_2 = %s"%(k,c[k],vv))
    print("k with a_k a 2-adic UNIT (=> v(theta_k)/k == v(pi) exactly):", units)
    print("count of units up to %d: %d"%(N,len(units)))
