
import unittest
import time
from binascii import hexlify, unhexlify
import ed25519
import _ed25519 as raw

def flip_bit(s, bit=0, in_byte=-1):
    as_bytes = [ord(b) for b in s]
    as_bytes[in_byte] = as_bytes[in_byte] ^ (0x01<<bit)
    return "".join([chr(b) for b in as_bytes])
def b(hexlified):
    return unhexlify(hexlified)

# the pure-python demonstration code (on my 2010 MacBookPro) takes 5s to
# generate a public key, 9s to sign, 14s to verify

class Basic(unittest.TestCase):
    timer = None
    def log(self, msg):
        return
        now = time.time()
        if self.timer is None:
            self.timer = now
        else:
            elapsed = now - self.timer
            self.timer = now
            print " (%f elapsed)" % elapsed
        print msg

    def test_constants(self):
        # the secret key we get from raw.keypair() are 64 bytes long, and
        # are mostly the output of a sha512 call. The first 32 bytes are the
        # private exponent (random, with a few bits stomped).
        self.failUnlessEqual(raw.SECRETKEYBYTES, 64)
        # the public key is the encoded public point
        self.failUnlessEqual(raw.PUBLICKEYBYTES, 32)
        self.failUnlessEqual(raw.SIGNATUREKEYBYTES, 64)

    def test_raw(self):
        return
        sk_s = "\x00" * 32 # usually urandom(32)
        self.log("computing public key..")
        vk_s = raw.publickey(sk_s)
        self.failUnlessEqual(len(vk_s), 32)
        exp_vks = unhexlify("3b6a27bcceb6a42d62a3a8d02a6f0d73"
                            "653215771de243a63ac048a18b59da29")
        self.failUnlessEqual(vk_s, exp_vks)
        msg = "hello world"
        self.log("signing..")
        sig = raw.signature(msg, sk_s, vk_s)
        self.failUnlessEqual(len(sig), 64)
        exp_sig = unhexlify("b0b47780f096ae60bfff8d8e7b19c36b"
                            "321ae6e69cca972f2ff987ef30f20d29"
                            "774b53bae404485c4391ddf1b3f37aaa"
                            "8a9747f984eb0884e8aa533386e73305")
        self.failUnlessEqual(sig, exp_sig)
        self.log("checking (good)..")
        ret = raw.checkvalid(sig, msg, vk_s) # don't raise exception
        self.failUnlessEqual(ret, None)
        self.log("checking (bad msg 1)..")
        self.failUnlessRaises(Exception,
                              raw.checkvalid,
                              sig, msg+".. NOT!", vk_s)
        self.log("checking (bad msg 2)..")
        self.failUnlessRaises(Exception,
                              raw.checkvalid,
                              sig, flip_bit(msg), vk_s)
        self.log("checking (bad key 1)..")
        self.failUnlessRaises(Exception,
                              raw.checkvalid,
                              sig, msg, flip_bit(vk_s))
        self.log("checking (bad key 2)..")
        self.failUnlessRaises(Exception,
                              raw.checkvalid,
                              sig, msg, flip_bit(vk_s, in_byte=2))
        self.log("done")

    def test_keypair(self):
        sk, vk = ed25519.create_keypair()
        self.failUnless(isinstance(sk, ed25519.SigningKey), sk)
        self.failUnless(isinstance(vk, ed25519.VerifyingKey), vk)
        sk2, vk2 = ed25519.create_keypair()
        #print
        #print "sk", hexlify(sk.to_string())
        #print "vk", hexlify(vk.to_string())
        #print hexlify(sk2.to_string())
        self.failIfEqual(hexlify(sk.to_string()), hexlify(sk2.to_string()))

    def test_publickey(self):
        seed = unhexlify("4ba96b0b5303328c7405220598a587c4"
                         "acb06ed9a9601d149f85400195f1ec3d")
        sk = ed25519.SigningKey(seed)
        self.failUnlessEqual(hexlify(sk.to_string()),
                             ("4ba96b0b5303328c7405220598a587c4"
                              "acb06ed9a9601d149f85400195f1ec3d"
                              "a66d161e090652b054740748f059f92a"
                              "5b731f1c27b05571f6d942e4f8b7b264"))
        self.failUnlessEqual(hexlify(sk.to_seed()),
                             ("4ba96b0b5303328c7405220598a587c4"
                              "acb06ed9a9601d149f85400195f1ec3d"))
        self.failUnlessRaises(ValueError,
                              ed25519.SigningKey, "wrong length")
        sk2 = ed25519.SigningKey(seed)
        self.failUnlessEqual(sk, sk2)

    def test_OOP(self):
        sk_s = unhexlify("4ba96b0b5303328c7405220598a587c4"
                         "acb06ed9a9601d149f85400195f1ec3d"
                         "a66d161e090652b054740748f059f92a"
                         "5b731f1c27b05571f6d942e4f8b7b264")
        sk = ed25519.SigningKey(sk_s)
        self.failUnlessEqual(len(sk.to_string()), 64)
        self.failUnlessEqual(sk.to_string(), sk_s)

        sk2_seed = unhexlify("4ba96b0b5303328c7405220598a587c4"
                             "acb06ed9a9601d149f85400195f1ec3d")
        sk2 = ed25519.SigningKey(sk2_seed)
        self.failUnlessEqual(sk2.to_string(), sk.to_string())

        vk = sk.get_verifying_key()
        self.failUnlessEqual(len(vk.to_string()), 32)
        exp_vks = unhexlify("a66d161e090652b054740748f059f92a"
                            "5b731f1c27b05571f6d942e4f8b7b264")
        self.failUnlessEqual(vk.to_string(), exp_vks)
        self.failUnlessEqual(ed25519.VerifyingKey(vk.to_string()), vk)
        msg = "hello world"
        sig = sk.sign(msg)
        self.failUnlessEqual(len(sig), 64)
        exp_sig = unhexlify("6eaffe94f2972b35158b6aaa9b69c1da"
                            "97f0896aca29c41b1dd7b32e6c9e2ff6"
                            "76fc8d8b034709cdcc37d8aeb86bebfb"
                            "173ace3c319e211ea1d7e8d8884c1808")
        self.failUnlessEqual(sig, exp_sig)
        self.failUnlessEqual(vk.verify(sig, msg), None) # also, don't throw
        self.failUnlessRaises(ed25519.BadSignatureError,
                              vk.verify, sig, msg+".. NOT!")

    def test_object_identity(self):
        sk1_s = unhexlify("ef32972ae3f1252a5aa1395347ea008c"
                          "bd2fed0773a4ea45e2d2d06c8cf8fbd4"
                          "c024601a9c5b854fb100ff3116cf4f22"
                          "a311565f027391cb49d3bbe11c44399d")
        sk2_s = unhexlify("3d550c158900b4c2922b6656d2f80572"
                          "89de4ee65043745179685ae7d29b944d"
                          "672b8a2cb23f9e75e1d46ce249cd9c04"
                          "68f816f1c734a102822b60e18b41eacd")
        sk1a = ed25519.SigningKey(sk1_s)
        sk1b = ed25519.SigningKey(sk1_s)
        vk1a = sk1a.get_verifying_key()
        vk1b = sk1b.get_verifying_key()
        sk2 = ed25519.SigningKey(sk2_s)
        vk2 = sk2.get_verifying_key()
        self.failUnlessEqual(sk1a, sk1b)
        self.failIfEqual(sk1a, sk2)
        self.failUnlessEqual(vk1a, vk1b)
        self.failIfEqual(vk1a, vk2)

        self.failIfEqual(sk2, "not a SigningKey")
        self.failIfEqual(vk2, "not a VerifyingKey")


class KnownAnswerTests(unittest.TestCase):
    def test_all(self):
        # kat-ed25519.txt comes from "sign.input" on ed25519.cr.yp.to . The
        # pure-python ed25519.py in the same distribution uses a very
        # different key format than the one used by NaCl.
        for i,line in enumerate(open("kat-ed25519.txt")):
            x = line.split(":")
            A,B,C,D = [unhexlify(i) for i in x[:4]]
            # A[:32] is the 32 byte seed (the entropy input to H())
            # A[32:] == B == the public point (pubkey)
            # C is the message
            # D is 64 bytes of signature (R+S) prepended to the message

            seed = A[:32]
            vk_s = B
            # the NaCl signature is R+S, which happens to be the same as ours
            msg = C
            sig = D[:64]
            # note that R depends only upon the second half of H(seed). S
            # depends upon both the first half (the exponent) and the second
            # half

            #if len(msg) % 16 == 1:
            #    print "msg len = %d" % len(msg), time.time()

            sk = ed25519.SigningKey(seed)
            vk = sk.get_verifying_key()
            self.failUnlessEqual(vk.to_string(), vk_s)
            vk2 = ed25519.VerifyingKey(vk_s)
            self.failUnlessEqual(vk2, vk) # objects should compare equal
            self.failUnlessEqual(vk2.to_string(), vk_s)
            newsig = sk.sign(msg)
            sig_R,sig_S = sig[:32],sig[32:]
            newsig_R,newsig_S = newsig[:32],newsig[32:]
            self.failUnlessEqual(hexlify(newsig), hexlify(sig)) # deterministic sigs
            self.failUnlessEqual(vk.verify(sig, msg), None) # no exception

if __name__ == '__main__':
    unittest.main()