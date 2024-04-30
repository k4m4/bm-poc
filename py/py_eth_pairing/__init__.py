import eth_pairing_py
from py_ecc.bn128 import G1, G2, neg, curve_order

bar = (2**128)
# G2[0].coeffs = (11559732032986387107991004021392285783925812861821192530917403151452391805634, 4082367875863433681332203403145435568316851327593401208105741076214120093531)
# G2[1].coeffs = (10857046999023057135944570762232829481370756359578518086990519993285655852781, 8495653923123431417604973247489272438418190587263600148770280649306958101930)

def neg(pt):
  q = 21888242871839275222246405745257275088696311157297823662689037894645226208583
  if pt[0] == 0 and pt[1] == 0:
    return (0, 0)
  return (int(pt[0]), q - int(pt[1]))

def fq_to_lst(x):
  return [int(x)%bar, int(x)//bar]

def lst_to_int(lst):
  return lst[0] + lst[1]*bar

def lst_to_pt(lst):
  return (lst[0] + lst[1]*bar, lst[2] + lst[3]*bar)

def add(a, b):
  lst_a = fq_to_lst(a[0]) + fq_to_lst(a[1])
  lst_b = fq_to_lst(b[0]) + fq_to_lst(b[1])
  lst_c = eth_pairing_py.curve_add(lst_a, lst_b)
  c = lst_to_pt(lst_c)
  return c

def multiply(pt, sc):
  lst_pt = fq_to_lst(pt[0]) + fq_to_lst(pt[1])
  lst_sc = fq_to_lst(sc)
  lst_c = eth_pairing_py.curve_mul(lst_pt, lst_sc)
  c = lst_to_pt(lst_c)
  return c

def pairing(g1_1, g2_1, g1_2, g2_2):
  g1_pts = [g1_1, g1_2]
  g2_pts = [g2_1, g2_2]
  n = 2
  lst_input = []
  for i in range(n):
    lst_input += fq_to_lst(g1_pts[i][0]) + fq_to_lst(g1_pts[i][1])
    lst_input += fq_to_lst(g2_pts[i][0].coeffs[1]) + fq_to_lst(g2_pts[i][0].coeffs[0])
    lst_input += fq_to_lst(g2_pts[i][1].coeffs[1]) + fq_to_lst(g2_pts[i][1].coeffs[0])
  c = eth_pairing_py.pairing2(lst_input)
  # c = lst_to_int(lst_c)
  return c
