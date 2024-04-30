extern crate eth_pairings;

use eth_pairings::public_interface::eip196::EIP196Executor;

// use pyo3::types::PyInt;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

fn put_u8(input: &[u128]) -> [u8; 32] {
    let mut res: [u8; 32] = [0; 32];
    let n_elem = 128/8;
    let n_total_elem = 256/8;
    for i in 0..n_total_elem {
        let idx_arr = i / n_elem;
        let idx_elem = i % n_elem;
        res[i] = ((input[idx_arr] >> 8*idx_elem) & 0xff) as u8;
    }
    res.reverse();
    return res;
}

fn put_u32(input: &[u8]) -> [u128; 2] {
    const SZ_INPUT: usize = 128*2/8;
    let mut res: [u128; 2] = [0; 2];
    let n_input = 256/8;
    let n_elem = 128/8;
    for i in 0..n_input {
        let idx_arr = i / n_elem;
        let idx_elem = i % n_elem;
        res[idx_arr] += (input[SZ_INPUT-1-i] as u128) << (8*idx_elem);
        // res[idx_arr] += (input[i] as u128) << (8*idx_elem);
    }
    return res;
}

#[pyfunction]
fn curve_add(a: Vec<u128>, b: Vec<u128>) -> Vec<u128> {
    const SZ_INPUT: usize = 256*2*2/8;
    const SZ_U8: usize = 256/8;
    const SZ_U128: usize = 256/128;

    let mut input: [u8; SZ_INPUT] = [0; SZ_INPUT];
    let mut count = 0;
    input[count*SZ_U8..(count+1)*SZ_U8].copy_from_slice(&put_u8(&a[0..2]));
    count += 1;
    input[count*SZ_U8..(count+1)*SZ_U8].copy_from_slice(&put_u8(&a[2..4]));
    count += 1;
    input[count*SZ_U8..(count+1)*SZ_U8].copy_from_slice(&put_u8(&b[0..2]));
    count += 1;
    input[count*SZ_U8..(count+1)*SZ_U8].copy_from_slice(&put_u8(&b[2..4]));


    let eip_result = EIP196Executor::add(&input).unwrap();
    let mut output = vec![0 as u128; 4];
    count = 0;
    output[count*SZ_U128..(count+1)*SZ_U128].copy_from_slice(&put_u32(&eip_result[count*SZ_U8..(count+1)*SZ_U8]));
    count += 1;
    output[count*SZ_U128..(count+1)*SZ_U128].copy_from_slice(&put_u32(&eip_result[count*SZ_U8..(count+1)*SZ_U8]));

    return output;
}

#[pyfunction]
fn curve_mul(pt: Vec<u128>, sc: Vec<u128>) -> Vec<u128> {
    const SZ_INPUT: usize = 256*(2+1)/8;
    const SZ_U8: usize = 256/8;
    const SZ_U128: usize = 256/128;

    let mut input: [u8; SZ_INPUT] = [0; SZ_INPUT];

    let mut count = 0;
    input[count*SZ_U8..(count+1)*SZ_U8].copy_from_slice(&put_u8(&pt[0..2]));
    count += 1;
    input[count*SZ_U8..(count+1)*SZ_U8].copy_from_slice(&put_u8(&pt[2..4]));
    count += 1;
    input[count*SZ_U8..(count+1)*SZ_U8].copy_from_slice(&put_u8(&sc[0..2]));

    let eip_result = EIP196Executor::mul(&input).unwrap();
    let mut output = vec![0 as u128; 4];
    count = 0;
    output[count*SZ_U128..(count+1)*SZ_U128].copy_from_slice(&put_u32(&eip_result[count*SZ_U8..(count+1)*SZ_U8]));
    count += 1;
    output[count*SZ_U128..(count+1)*SZ_U128].copy_from_slice(&put_u32(&eip_result[count*SZ_U8..(count+1)*SZ_U8]));

    return output;
}

#[pyfunction]
fn pairing2(pts: Vec<u128>) -> bool {
    // const N_INT256: usize = 6*2;
    const N_INT256: usize = 6*2;
    const SZ_INPUT: usize = 256*(N_INT256)/8;
    const SZ_U8: usize = 256/8;
    // const SZ_U128: usize = 256/128;

    let mut input = [0u8; SZ_INPUT];

    for count in 0..N_INT256 {
        input[count*SZ_U8..(count+1)*SZ_U8].copy_from_slice(&put_u8(&pts[count*2..(count+1)*2]));
    }

    let eip_result = EIP196Executor::pair(&input).unwrap();
    return eip_result[31] != 0;
    // let mut output = vec![0 as u128; 2];
    // let count = 0;
    // output[count*SZ_U128..(count+1)*SZ_U128].copy_from_slice(&put_u32(&eip_result[count*SZ_U8..(count+1)*SZ_U8]));

    // return output;
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let a: Vec<u128> = vec![0 as u128; 4];
        let b: Vec<u128> = vec![0 as u128; 4];
        let c: Vec<u128> = curve_add(a, b);
    }
}

#[pymodule]
fn eth_pairing_py(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(curve_add))?;
    m.add_wrapped(wrap_pyfunction!(curve_mul))?;
    m.add_wrapped(wrap_pyfunction!(pairing2))?;

    Ok(())
}
