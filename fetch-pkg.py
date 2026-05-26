#!/usr/bin/env python

import hashlib
import json
import os
import shutil
import ssl
import sys
import time
import urllib.request

CHUNK_SIZE = 8 * 1024 # 8K


def get_package_json(url):
    response = urllib.request.urlopen(url, context=ssl._create_unverified_context())
    package_json = json.loads(response.read().decode('utf-8'))
    return package_json


def file_digest(fname):
    with open(fname, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest().lower()


def get_package_piece(url, size, digest, out_fname):
    if os.path.isfile(out_fname) and os.path.getsize(out_fname) == size and file_digest(out_fname) == digest:
        print(f"  {out_fname} | progress: {100:6.2f}% | speed: {'inf':>8} MBit/s\r")
        return True
    with urllib.request.urlopen(url, context=ssl._create_unverified_context()) as response, open(out_fname, 'wb') as out_file:
        bytes_read = bytes_start = 0
        out_digest = hashlib.sha256()
        time_start = time.perf_counter()
        
        while bytes_read < size:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            out_file.write(chunk)
            bytes_read += len(chunk)
            out_digest.update(chunk)

            time_delta = time.perf_counter() - time_start
            if time_delta >= 1.00 or bytes_read == size:
                bytes_delta = bytes_read - bytes_start
                print(f"  {out_fname} | progress: {100.0 * bytes_read / size:6.2f}% | speed: {(bytes_delta * 8e-6) / time_delta:8.2f} MBit/s\r", end="")
                bytes_start = bytes_read
                time_start += time_delta
    print()
    return os.path.getsize(out_fname) == size and out_digest.hexdigest().lower() == digest


def merge_pieces(pkg_pieces, pkg_fname, pkg_filesize, pkg_digest):
    with open(pkg_fname, "wb") as outfile:
        for p in pkg_pieces:
            with open(p['fname'], 'rb') as infile:
                offset = p['fileOffset']
                if offset != outfile.tell():
                    print(f"ERROR: mismatched offset {p['fname']}: expected: {offset}, actual: {outfile.tell()}")
                    return False
                shutil.copyfileobj(infile, outfile)
    pkg_fname_size = os.path.getsize(pkg_fname)
    if pkg_fname_size != pkg_filesize:
        print(f"ERROR: mismatched size {pkg_fname}: expected: {pkg_filesize}, actual: {pkg_fname_size}")
        return False
    # TODO(tnvu): Figure out how to calculate the pkg_fname digest so it matches with pkg_digest from the JSON
#    pkg_fname_digest = file_digest(pkg_fname)
#    if pkg_fname_digest != pkg_digest:
#        print(f"ERROR: mismatched digest {pkg_fname}: expected: {pkg_digest}, actual: {pkg_fname_digest}")
#        return False
    return True
 

def main(argv):
    for json_url in argv[1:]:
        if json_url.endswith('.crc'):
            json_url = json_url.removesuffix('.crc') + '.json'
        json_data = get_package_json(json_url)
        pkg_fname = os.path.basename(json_url).removesuffix('.json') + '.pkg'
        pkg_filesize = json_data['originalFileSize']
        pkg_digest = json_data['packageDigest'].lower()
        print(f'{pkg_fname} | {pkg_filesize} | {pkg_digest}')
        
        if os.path.isfile(pkg_fname) and os.path.getsize(pkg_fname) == pkg_filesize:
            print('  Package already downloaded')
            continue

        pkg_pieces = json_data['pieces']
        pkg_pieces.sort(key=lambda x: x['fileOffset']) # sort according to file offsets

        success = True
        for p in pkg_pieces:
            p['fname'] = os.path.basename(p['url'])
            if not get_package_piece(p['url'], p['fileSize'], p['hashValue'].lower(), p['fname']):
                success = False
        if not success:
            continue
        if not merge_pieces(pkg_pieces, pkg_fname, pkg_filesize, pkg_digest):
            print("Error merging package pieces")
            continue
        for p in pkg_pieces:
            os.remove(p['fname'])


if __name__ == '__main__':
    main(sys.argv)