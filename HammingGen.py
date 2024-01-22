import numpy as np

# def padList(list, pad, n):
#     "Pad 'list' with 'pad', to multiple of 'n'"
#     l = len(list)
#     list += [pad] * ((n - (l %n)) % n)
#     return list

def glom(list, bits=4):
    "Combine 4-bit numbers into word"
    result = 0;
    list.reverse()
    for i in list:
        result <<= bits
        result |= i
    return result

def printVar(list, n, bits, varName="array"):
    print("static const uint16_t")
    print(varName, "[] = {")
    assert 0 == (len(list) % 4)
#     list = padList(list, pad=0, n=n)
    for i in range(0, len(list), n):
        r = glom(list[i:i+n], bits=bits)
        assert(r >= 0)
        assert(r <= 0xFFFF)
        print(f"\t{r:#0{6}x},")
    print("};")
    
# # Function to get parity of number n. 
# # It returns 1 if n has odd parity, 
# # and returns 0 if n has even parity
# def getParity( n ):
#     parity = 0
#     while n:
#         parity = ~parity
#         n = n & (n - 1)
#     return parity
 
def bits(n, b=4):
    return np.array([n >> i & 1 for i in range(b)])

def unbits(l):
    result = 0
    for i,b in enumerate(l):
        result |= b << i
    return result
    
# generator matrix
Gt = np.array([
    [1,1,0,1],
    [1,0,1,1],
    [1,0,0,0],
    [0,1,1,1],
    [0,1,0,0],
    [0,0,1,0],
    [0,0,0,1]
    ])
# parity check matrix
H = np.array([
    [1,0,1,0,1,0,1],
    [0,1,1,0,0,1,1],
    [0,0,0,1,1,1,1]
    ])

def hamming7_4_encode(n):
    p = bits(n)
#     p = np.array(b)
    x = np.matmul(Gt,p)
    f = lambda x: x % 2
    y = f(x) # modulo-2
    return unbits(y)

def hamming7_4_parity(n):
    r = bits(n, 7)
#     p = np.array(b)
#     print("r =", r)
    x = np.matmul(H,r)
#     print("x =", x)
    f = lambda x: x % 2
    y = f(x) # modulo-2
#     print("y =", y)
    l = list(y)
#     l.reverse()
    p = unbits(l)
#     assert(0 == p)
    return p

def hamming7_4_decode(n):
    d = bits(n,7)
    p = hamming7_4_parity(n)
    if 0 != p:
#         print("Error in bit", p - 1)
        d[p - 1] = 1 - d[p - 1]
    e = [d[2], d[4], d[5], d[6]]
    return unbits(e)

encode = [ hamming7_4_encode(n) for n in range(16)]
decode = [ hamming7_4_decode(n) for n in range(128)]
print("encode =", encode)
print("decode =", decode)

# Test the encode and decode tables
for n in range(16):
    for c in range(8):
        h = encode[n]
        m = (h ^ (1 << c)) & 0x7F # corrupt each codeword bit in turn
#         print("data =", n, "codeword =", hex(m))
        y = decode[m]
        assert decode[h] == n
        errorDetected = (encode[y] != m)
        assert errorDetected == (c != 7)
#         print("y =", y) # , " decoded =", hex(unbits(y)))
        assert y == n

# If all is well then dump the C lookup arrays
printVar(encode, 2, 8, varName="hamming7_4_encode")
printVar(decode, 4, 4, varName="hamming7_4_decode")
      