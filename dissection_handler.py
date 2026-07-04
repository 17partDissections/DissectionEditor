import struct

magic_bytes = b'\x44\x49\x53\x53\x45\x43\x54\x49\x4F\x4E'
shift = 17

def codec(data, shift):
    result = bytearray()
    for byte in data:
        if byte == 17 and shift < 0: result.append(32)
        elif byte == 32 and shift > 0: result.append(17)
        elif byte == 10 or byte == 13: result.append(byte)
        else:
            shifted = (byte + shift) % 256
            result.append(shifted)
    return bytes(result)

def pack(text):
    text_bytes = text.encode('utf-8')
    encrypted = codec(text_bytes, shift)
    packed = magic_bytes
    packed += struct.pack('<I', len(encrypted))
    packed += encrypted
    return packed

def unpack(data):
    if not data.startswith(magic_bytes):
        return None
    pos = len(magic_bytes)
    length = struct.unpack('<I', data[pos:pos + 4])[0]
    pos += 4
    decrypted = codec(data[pos:pos + length], -shift)
    return decrypted.decode('utf-8')