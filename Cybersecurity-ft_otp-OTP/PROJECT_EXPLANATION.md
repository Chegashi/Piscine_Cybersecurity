# ft_otp Project Explanation

## Project Goal

`ft_otp` is a small TOTP utility for the 42 Cybersecurity Piscine.

The mandatory subject asks for a program named `ft_otp` that can:

- read a hexadecimal master key of at least 64 characters with `-g`;
- store that key safely in an encrypted `ft_otp.key` file;
- read the encrypted key with `-k`;
- generate a 6-digit one-time password on standard output;
- implement the HOTP/TOTP logic without using a ready-made TOTP library.

This project implements the HOTP/TOTP algorithm directly with Python's `hmac`,
`hashlib`, `struct`, and `time` modules. `cryptography.Fernet` is only used to
encrypt the stored key file, not to generate OTP values.

## Important Terms

### OTP

OTP means One-Time Password.

An OTP is a short authentication code intended to be valid only once or only for
a short period. The user proves that they know a secret without typing the secret
itself. If an attacker sees one OTP, that code should soon become useless.

In this project the OTP format is always 6 decimal digits, for example:

```text
836492
```

### HOTP

HOTP means HMAC-Based One-Time Password.

HOTP uses two inputs:

- `K`: a shared secret key;
- `C`: a counter value.

The simplified formula is:

```text
HOTP(K, C) = Truncate(HMAC-SHA1(K, C))
```

Each time the counter changes, the HMAC input changes, so the generated password
changes. HOTP is event-based because the counter normally increases after an
event, such as a button press or a login attempt.

### TOTP

TOTP means Time-Based One-Time Password.

TOTP is HOTP with time used as the counter. Instead of manually incrementing a
counter, both sides compute a counter from Unix time:

```text
T = floor((current_unix_time - T0) / X)
TOTP(K) = HOTP(K, T)
```

Common values are:

- `T0 = 0`, the Unix epoch;
- `X = 30`, a 30-second time step;
- `digits = 6`, the output length used by this project and by `oathtool` by default.

This means the same key produces the same OTP during the same 30-second window,
then a different OTP in the next window.

## Technical Glossary

This section explains technical words used in this project.

### `oathtool`

`oathtool` is a command-line program that can generate and verify HOTP/TOTP
codes. It is useful as a reference tool.

In this project, the test script compares our output with:

```bash
oathtool --totp "$KEY"
```

If our code and `oathtool` receive the same key during the same 30-second time
window, they should print the same OTP.

### RFC

RFC means Request for Comments.

RFCs are technical documents used on the Internet to describe protocols,
algorithms, formats, requirements, and best practices. In this project:

- RFC 6238 describes TOTP.
- RFC 4226 describes HOTP.
- RFC 2104 describes HMAC.

### Algorithm

An algorithm is a precise sequence of steps used to solve a problem.

For this project, the algorithm is:

1. take a secret key;
2. calculate a time counter;
3. compute HMAC-SHA1;
4. dynamically truncate the result;
5. reduce it to 6 digits.

### Secret Key

A secret key is private data shared by the OTP generator and verifier.

Anyone who knows the secret key can generate the same OTPs. That is why the key
must be random, encrypted at rest, and protected with file permissions.

### Hexadecimal

Hexadecimal, often shortened to hex, is base-16 text representation.

It uses:

```text
0123456789abcdef
```

Two hex characters represent one byte. Example:

```text
ff = 255
00 = 0
10 = 16
```

The subject asks for at least 64 hex characters, which equals 32 bytes.

### Byte

A byte is 8 bits.

Computers store binary data in bytes. A 64-character hex key represents 32 bytes
because each byte is written with 2 hex characters.

### Bit

A bit is a binary value: `0` or `1`.

When the explanation says "31-bit integer", it means an integer represented
using 31 binary positions.

### Unix Time

Unix time is the number of seconds since:

```text
1970-01-01 00:00:00 UTC
```

TOTP uses Unix time to calculate the moving counter.

### Counter

A counter is a number used as changing input.

In HOTP, the counter changes after events. In TOTP, the counter changes when
time moves into a new time window.

### Time Step

The time step is the length of each TOTP window.

This project uses:

```text
30 seconds
```

That means the time counter changes every 30 seconds.

### HMAC

HMAC means Hash-based Message Authentication Code.

It is a construction that combines:

- a secret key;
- a message;
- a hash function.

In this project, the message is the 8-byte counter and the hash function is
SHA-1.

### SHA-1

SHA-1 is a cryptographic hash function that outputs 160 bits, or 20 bytes.

This project uses SHA-1 because RFC 4226 defines HOTP with HMAC-SHA1, and common
TOTP tools use it by default.

### Hash Function

A hash function transforms input data into a fixed-size output.

Example idea:

```text
hash("hello") -> fixed-size digest
```

A cryptographic hash should make it difficult to reconstruct the input from the
output or predict output changes.

### Digest

A digest is the output of a hash or HMAC operation.

In this project:

```python
digest = hmac.new(key, message, hashlib.sha1).digest()
```

The digest is 20 bytes long because SHA-1 outputs 20 bytes.

### Dynamic Truncation

Dynamic truncation is the HOTP step that extracts a 31-bit number from the
20-byte HMAC digest.

It is called dynamic because the offset is not fixed. The offset depends on the
last byte of the digest.

### Big-Endian

Big-endian means the most significant byte is stored first.

Example:

```text
number 1 as 8-byte big-endian = 0000000000000001
```

HOTP uses big-endian counter encoding, so this project uses:

```python
struct.pack(">Q", counter)
```

### Modulo

Modulo gives the remainder after division.

Example:

```text
1234567 mod 1000000 = 234567
```

The project uses modulo `1_000_000` to turn a large integer into a 6-digit
range.

### Padding

Padding means adding extra characters to reach a required length.

In this project:

```python
"31805".zfill(6) -> "031805"
```

This keeps every OTP exactly 6 digits.

### Fernet

Fernet is an authenticated symmetric encryption format from the Python
`cryptography` package.

Authenticated encryption means it protects:

- confidentiality: attackers cannot read the plaintext without the key;
- integrity: tampering can be detected during decryption.

This project uses Fernet only to encrypt `ft_otp.key`.

### Symmetric Encryption

Symmetric encryption means the same secret key is used to encrypt and decrypt.

In this project, the hard-coded `FERNET_KEY` encrypts and decrypts the stored
hex key.

### Plaintext

Plaintext means readable, unencrypted data.

The original `key.hex` file is plaintext. The generated `ft_otp.key` file should
not contain the plaintext key.

### Ciphertext

Ciphertext means encrypted data.

`ft_otp.key` contains ciphertext produced by Fernet.

### Standard Output

Standard output, or stdout, is where a command-line program prints normal
results.

The subject requires `-k` to print the OTP on standard output.

### Standard Error

Standard error, or stderr, is where command-line programs usually print error
messages.

This project prints user-facing errors there.

### Exit Code

An exit code is the number a program returns to the shell when it finishes.

Common convention:

- `0`: success;
- non-zero: error.

This project returns `0` on success and `1` for user-facing errors.

### Virtual Environment

A Python virtual environment is an isolated folder for Python dependencies.

This project can use `venv/` so dependencies like `cryptography` do not need to
be installed globally.

### Dependency

A dependency is external code needed by a project.

Here, `cryptography` is needed for Fernet encryption.

## Algorithm Behind HOTP

The code follows the HOTP construction from RFC 4226.

### 1. Convert the Counter to 8 Bytes

HOTP does not hash the decimal text of the counter. It hashes an 8-byte,
big-endian binary representation of the counter.

In this project:

```python
message = struct.pack(">Q", counter)
```

`>Q` means:

- `>`: big-endian byte order;
- `Q`: unsigned 64-bit integer.

Using 64 bits matters because RFC 6238 requires support for time counters beyond
the 32-bit Unix time limit.

### 2. Compute HMAC-SHA1

The secret key and the 8-byte counter message are passed into HMAC-SHA1:

```python
digest = hmac.new(key, message, hashlib.sha1).digest()
```

The result is 20 bytes because SHA-1 produces a 160-bit digest.

HMAC is not plain SHA-1. Plain SHA-1 would only hash data. HMAC combines a secret
key with the message in a specific two-layer construction, which prevents several
attacks that affect naive keyed-hash designs.

### 3. Dynamic Truncation

The HMAC result is 20 bytes, but the user needs a short numeric code. HOTP uses
dynamic truncation to select 4 bytes from the digest.

In this project:

```python
offset = digest[-1] & 0x0F
selected = digest[offset : offset + 4]
```

The low 4 bits of the last digest byte give an offset between `0` and `15`.
Because the digest has 20 bytes, reading 4 bytes starting at offset `0..15` is
always safe.

### 4. Convert to a Positive 31-Bit Integer

The selected 4 bytes are interpreted as a big-endian unsigned integer, then the
highest bit is cleared:

```python
binary_code = struct.unpack(">I", selected)[0] & 0x7FFFFFFF
```

The mask `0x7FFFFFFF` keeps only 31 bits. This matches the RFC behavior and
avoids signed-integer ambiguity.

### 5. Reduce to 6 Digits

Finally, the 31-bit value is reduced modulo `10^6` and left-padded with zeros:

```python
otp = str(binary_code % 1_000_000).zfill(6)
```

Modulo `1_000_000` gives a value between `0` and `999999`. `zfill(6)` guarantees
the output is always exactly 6 digits, including values like `031805`.

## Algorithm Behind TOTP

TOTP reuses HOTP. The only difference is how the counter is chosen.

In this project:

```python
counter = int(time.time()) // 30
otp = hotp(key, counter)
```

`time.time()` returns the current Unix timestamp in seconds. Integer division by
`30` creates one counter value per 30-second window.

Example:

```text
time = 59 seconds  -> counter = 1
time = 60 seconds  -> counter = 2
time = 89 seconds  -> counter = 2
time = 90 seconds  -> counter = 3
```

So every 30 seconds, the moving factor changes, and the HOTP result changes with
it.

## Full Pseudocode

This is the complete logic in language-neutral form:

```text
function HOTP(secret_key, counter, digits = 6):
    counter_bytes = unsigned_64_bit_big_endian(counter)
    hmac_result = HMAC_SHA1(secret_key, counter_bytes)

    offset = last_byte(hmac_result) AND 0x0F
    four_bytes = hmac_result[offset : offset + 4]

    number = unsigned_32_bit_big_endian(four_bytes)
    number = number AND 0x7FFFFFFF

    otp = number modulo 10^digits
    return otp left-padded with zeroes to digits characters

function TOTP(secret_key, unix_time, step = 30, t0 = 0):
    time_counter = floor((unix_time - t0) / step)
    return HOTP(secret_key, time_counter)
```

The project code is almost a direct translation of this pseudocode:

```python
message = struct.pack(">Q", counter)
digest = hmac.new(key, message, hashlib.sha1).digest()
offset = digest[-1] & 0x0F
binary_code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
return str(binary_code % (10**OTP_DIGITS)).zfill(OTP_DIGITS)
```

## Worked Example With Intermediate Values

This example uses a 32-byte key, written as 64 hexadecimal characters:

```text
secret_hex =
000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
```

Use Unix timestamp `59` seconds and the default TOTP step of `30` seconds:

```text
counter = floor(59 / 30)
counter = 1
```

Convert counter `1` to an 8-byte big-endian message:

```text
message_hex = 0000000000000001
```

Compute HMAC-SHA1:

```text
digest_hex = d33fb107e4fac16345e31538047aeed05211ba3f
```

Find the dynamic truncation offset:

```text
last digest byte = 0x3f
offset = 0x3f & 0x0f
offset = 15
```

Take 4 bytes starting at offset `15`:

```text
selected_hex = d05211ba
```

Interpret those 4 bytes as an integer:

```text
selected_int = 3495039418
```

Clear the sign bit with `0x7fffffff`:

```text
binary_code = 3495039418 & 0x7fffffff
binary_code = 1347555770
```

Reduce to 6 digits:

```text
otp = 1347555770 mod 1000000
otp = 555770
```

So for this key and timestamp, the TOTP result is:

```text
555770
```

This example shows why the algorithm is deterministic. If the key and counter
are the same, the result is the same. The result changes only when the key
changes or the time window changes.

## Command Flow Examples

### Invalid Key

The subject shows that a non-hexadecimal key must fail:

```bash
printf "NEVER GONNA GIVE YOU UP" > key.txt
./ft_otp -g key.txt
```

Expected result:

```text
./ft_otp: error: key must be 64 hexadecimal characters.
```

Why it fails:

- the content is not hexadecimal;
- it is shorter than 64 hex characters;
- it cannot be decoded into the binary secret required by HOTP/TOTP.

### Valid Key

Create a valid 64-character hex key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))" > key.hex
./ft_otp -g key.hex
```

Expected result:

```text
Key was successfully saved in ft_otp.key.
```

At this point, `ft_otp.key` contains encrypted data, not the plaintext hex key.

Generate a TOTP:

```bash
./ft_otp -k ft_otp.key
```

Example result:

```text
836492
```

Run it again within the same 30-second window and the value is usually the same.
Run it after the next 30-second boundary and the value changes.

## How the Code Maps to the Algorithm

### `ft_otp`

`ft_otp` is the executable required by the subject. It is a small shell launcher
that runs `ft_otp.py` with the local virtual environment when available.

### `ft_otp.py`

`ft_otp.py` is the CLI layer.

It handles:

- argument count;
- accepted flags: `-g` and `-k`;
- user-facing error messages;
- exit codes.

It does not implement the cryptographic algorithm directly. It delegates that to
`ft_otp_core.py`.

### `ft_otp_core.py`

`ft_otp_core.py` contains the important logic:

- `normalize_hex_key`: validates the user key;
- `load_plain_hex_key`: reads the plaintext hex key file for `-g`;
- `save_encrypted_key`: encrypts the validated key and writes `ft_otp.key`;
- `load_encrypted_key`: decrypts `ft_otp.key` for `-k`;
- `hotp`: implements RFC 4226 HOTP;
- `totp`: implements RFC 6238 TOTP by deriving the HOTP counter from time.

## Key Handling

### Plain Input Key

The subject requires a hexadecimal key of at least 64 characters.

64 hexadecimal characters represent 32 bytes:

```text
2 hex characters = 1 byte
64 hex characters = 32 bytes = 256 bits
```

The code accepts longer even-length hex keys too, because the subject says "at
least 64 characters". It rejects:

- keys shorter than 64 hex characters;
- keys with non-hexadecimal characters;
- keys with an odd number of hex characters.

### Encrypted Storage

The plaintext key is not stored directly. With `-g`, the program encrypts the
normalized hex string and writes the ciphertext to:

```text
ft_otp.key
```

The file is written with mode `0600`, meaning only the owner can read and write
it.

This satisfies the project requirement that the key be stored safely in an
encrypted file. In a production system, the encryption key should not be
hard-coded in source code, but this is acceptable for a local piscine project
whose goal is to demonstrate encrypted storage and OTP generation.

## RFC Context

This project is mainly based on RFC 6238 and RFC 4226. The other RFCs explain
supporting concepts: HMAC, RFC requirement language, randomness, provisioning,
and RFC document status.

### RFC 6238: TOTP

RFC 6238 defines TOTP, the Time-Based One-Time Password algorithm.

Its key idea is simple: take HOTP and replace the event counter with a time
counter. The moving factor is:

```text
T = floor((current_unix_time - T0) / X)
```

Then:

```text
TOTP = HOTP(K, T)
```

Important points from RFC 6238:

- TOTP is built on HOTP.
- The prover and verifier must share the same secret.
- Both sides must agree on the time step.
- The default time step is 30 seconds.
- Keys should be randomly generated or derived securely.
- Secret keys should be protected against unauthorized access.

How this project follows it:

- `totp` uses Unix time from `time.time()`;
- `TIME_STEP_SECONDS = 30`;
- `totp` calls `hotp`;
- `ft_otp.key` is encrypted and owner-readable only.

Useful RFC 6238 sections:

- Section 1.1: explains that TOTP extends HOTP with a time-based moving factor.
- Section 1.2: explains that HOTP is based on HMAC-SHA1 and a counter.
- Section 3: lists requirements such as shared secrets, Unix time, HOTP usage,
  same time-step value, random keys, and protected key storage.
- Section 4.1: defines `X`, the time step, and `T0`, the epoch start.
- Section 4.2: defines `TOTP = HOTP(K, T)` and the time-counter formula.
- Section 5.1: explains that TOTP security depends on HOTP and HMAC.
- Section 5.2: discusses time-step size, replay risk, and validation windows.
- Section 6: discusses clock drift and resynchronization for real validators.

### RFC 4226: HOTP

RFC 4226 defines HOTP, the HMAC-Based One-Time Password algorithm.

HOTP depends on:

- a shared secret key `K`;
- a counter `C`;
- HMAC-SHA1;
- dynamic truncation;
- modulo reduction to the requested digit count.

The essential formula is:

```text
HOTP(K, C) = Truncate(HMAC-SHA1(K, C))
```

This project implements the RFC 4226 process manually:

1. encode `C` as 8 big-endian bytes;
2. compute `HMAC-SHA1(K, C)`;
3. use dynamic truncation to extract a 31-bit value;
4. reduce with modulo `10^6`;
5. left-pad to 6 digits.

Useful RFC 4226 sections:

- Section 5.1: introduces HOTP notation and parameters.
- Section 5.2: defines the HOTP formula.
- Section 5.3: describes the three main steps: HMAC-SHA1, dynamic truncation,
  and modulo reduction.
- Section 5.4: discusses security around the number of digits and brute force.
- Appendix D: provides HOTP test values that are useful for checking an
  implementation.

The most important implementation detail is dynamic truncation. It is not a
normal "take the first 4 bytes" operation. The offset is taken from the low 4
bits of the last HMAC byte, which makes the selected 4-byte window depend on the
HMAC output itself.

### RFC 2104: HMAC

RFC 2104 defines HMAC, Keyed-Hashing for Message Authentication.

HMAC combines:

- a cryptographic hash function;
- a secret key;
- a message.

For this project:

- hash function: SHA-1;
- key: the decoded hex secret;
- message: the 8-byte HOTP/TOTP counter.

Conceptually, HMAC hashes the key and message twice with two different padding
constants. This is why `HMAC-SHA1(key, message)` is stronger and better-defined
than simply doing `SHA1(key + message)`.

The Python call:

```python
hmac.new(key, message, hashlib.sha1).digest()
```

uses the RFC 2104 HMAC construction from the standard library.

Useful RFC 2104 sections:

- Section 2: defines HMAC and the inner/outer padding construction.
- Section 3: discusses HMAC key length and key generation.
- Section 6: discusses security considerations.

The HMAC construction can be summarized as:

```text
HMAC(K, text) = H((K xor opad) || H((K xor ipad) || text))
```

For this project:

- `H` is SHA-1;
- `K` is the binary secret decoded from the hex file;
- `text` is the 8-byte counter.

### RFC 2119: Requirement Keywords

RFC 2119 explains words such as:

- MUST;
- MUST NOT;
- SHOULD;
- SHOULD NOT;
- MAY;
- OPTIONAL.

These words appear throughout RFCs to indicate requirement strength.

Example in this project context:

- "MUST use HOTP" means it is mandatory for TOTP compatibility.
- "SHOULD protect keys" means it is a strong recommendation unless there is a
  justified reason not to.

RFC 2119 does not define OTP cryptography. It defines how to read requirement
language in RFC 6238 and RFC 4226.

Useful RFC 2119 idea:

- `MUST` means mandatory.
- `SHOULD` means strongly recommended, but exceptions may exist.
- `MAY` means optional.

For defense, when RFC 6238 says the algorithm `MUST` use HOTP, that is why the
project implements HOTP directly instead of inventing another time-based
formula.

### RFC 4086: Randomness Recommendations

RFC 4086 gives recommendations for generating randomness for security-sensitive
systems.

This matters because OTP security depends heavily on secret-key quality. If the
secret key is predictable, the OTPs are predictable too.

How this project relates:

- mandatory mode accepts a user-provided hex key;
- the user is responsible for creating the key with enough randomness.

The important defense point is: the OTP algorithm is deterministic once the key
and counter are known. The unpredictability comes from the secret key.

Useful RFC 4086 sections:

- Section 1: explains why security protocols need unpredictable values.
- Section 2: explains general randomness requirements.
- Later sections discuss randomness sources and how weak randomness can break
  cryptographic systems.

In this project, the mandatory CLI accepts a user-provided key, so the user is
responsible for key quality.

### RFC 6030: PSKC

RFC 6030 defines PSKC, Portable Symmetric Key Container.

PSKC is about provisioning and transporting symmetric keys and metadata, often
for OTP systems. It is not required by this project, because the subject only
asks for a local encrypted `ft_otp.key` file.

It is still relevant background because RFC 6238 mentions provisioning: in a
real deployment, the secret, issuer, algorithm, digit count, and time step may
need to be transferred between systems in a standard format. PSKC is one such
format.

Useful RFC 6030 sections:

- Section 1: explains the need for interoperable symmetric-key provisioning.
- Section 4: defines the basic PSKC key container structure.
- Section 6 and related sections describe key data and metadata.
- Section 13 discusses confidentiality and protection of key containers.

This project does not implement PSKC. Instead, it uses a simpler local encrypted
file because that is what the subject requires.

### RFC 5741

RFC 5741 is not part of the OTP algorithm.

It discusses RFC streams, headers, and boilerplate, including how to interpret
the status of RFC documents. RFC 6238 references it in the "Status of This Memo"
section to clarify that not every RFC is an Internet Standard.

For this project, RFC 5741 is useful only for understanding RFC status. It does
not change the HOTP/TOTP implementation.

Useful RFC 5741 section:

- Section 2 explains that not every RFC is an Internet Standard, even though it
  is published as an RFC.

This matters because RFC 6238 is marked informational. For this project, that is
not a problem: the subject explicitly asks us to follow RFC 6238.

## Defense Notes

Useful points to say during evaluation:

- "I do not use a TOTP library. I implement HOTP myself with HMAC-SHA1 and
  dynamic truncation."
- "`cryptography.Fernet` is only used to encrypt the stored key file."
- "`-g` validates the input hex key, encrypts it, and writes `ft_otp.key`."
- "`-k` decrypts `ft_otp.key`, derives the current time counter, and prints a
  6-digit TOTP."
- "The time counter is `floor(current_unix_time / 30)`."
- "The output matches `oathtool` because both use TOTP defaults: HMAC-SHA1,
  30-second step, Unix epoch, and 6 digits."
- "The key file is encrypted and written with owner-only permissions."

## Defense Q&A

This section collects questions that an evaluator, curious student, or professor
may ask, with direct answers you can use during defense.

### Subject and Usage

**Q: What is the goal of this project?**

A: The goal is to implement a local TOTP generator. It stores a hexadecimal
secret key in encrypted form with `-g`, then uses that stored key to generate
6-digit time-based one-time passwords with `-k`.

**Q: What are the mandatory flags?**

A: `-g <file>` reads a plaintext hexadecimal key file and creates encrypted
`ft_otp.key`. `-k <file>` reads an encrypted key file and prints the current
6-digit TOTP.

**Q: Why is the executable named `ft_otp`?**

A: The subject explicitly requires the executable to be named `ft_otp`. In this
project, `ft_otp` is a small launcher that runs the Python CLI implementation.

**Q: Why do you keep `ft_otp.py` if the subject asks for `ft_otp`?**

A: `ft_otp` is the executable entry point. `ft_otp.py` contains the Python CLI
logic. This keeps the required executable name while keeping the implementation
easy to import and test.

**Q: What does `./ft_otp -g key.hex` do exactly?**

A: It reads `key.hex`, validates that it contains at least 64 hexadecimal
characters, encrypts the normalized key string, writes the encrypted token to
`ft_otp.key`, and sets owner-only permissions on that file.

**Q: What does `./ft_otp -k ft_otp.key` do exactly?**

A: It reads the encrypted key file, decrypts it, converts the hex key to bytes,
computes the current TOTP from system time, and prints exactly 6 digits.

**Q: Why does the invalid key example fail?**

A: `NEVER GONNA GIVE YOU UP` is not hexadecimal and is shorter than 64 hex
characters, so it cannot be used as the binary secret required by HOTP/TOTP.

**Q: Does `-g` generate an OTP?**

A: No. `-g` only validates and stores the secret key. OTP generation happens
with `-k`.

**Q: Does `-k` generate a new random password?**

A: Not random in the usual sense. It deterministically computes a code from the
secret key and current time window. It looks unpredictable to attackers because
they do not know the secret key.

### OTP, HOTP, and TOTP Concepts

**Q: What is an OTP?**

A: OTP means One-Time Password. It is a short authentication code intended to be
valid for one use or for a short time, so leaked codes quickly become useless.

**Q: What is HOTP?**

A: HOTP means HMAC-Based One-Time Password. It computes an OTP from a secret key
and a counter using HMAC-SHA1, dynamic truncation, and modulo reduction.

**Q: What is TOTP?**

A: TOTP means Time-Based One-Time Password. It is HOTP where the counter is
derived from Unix time instead of manually incremented.

**Q: What is the difference between HOTP and TOTP?**

A: HOTP is event-counter based. TOTP is time-counter based. TOTP computes the
counter as `floor((current_time - T0) / X)`.

**Q: Which one does this project implement?**

A: It implements both layers. The `hotp` function implements RFC 4226 HOTP, and
the `totp` function implements RFC 6238 TOTP by calling HOTP with a time counter.

**Q: Why does RFC 6238 say TOTP must use HOTP?**

A: TOTP is designed as a time-based variant of HOTP. Reusing HOTP gives
interoperability with existing OTP tools and avoids inventing a custom scheme.

**Q: What is the moving factor?**

A: The moving factor is the changing value passed to HMAC. In HOTP it is the
event counter. In TOTP it is the time-step counter.

**Q: What are `K`, `C`, `T`, `X`, and `T0`?**

A: `K` is the secret key. `C` is the HOTP counter. `T` is the TOTP time counter.
`X` is the time step in seconds. `T0` is the starting Unix time, normally zero.

**Q: Why is the OTP the same if I run the command twice quickly?**

A: If both commands run inside the same 30-second window, the time counter is
the same, so HOTP receives the same input and returns the same output.

**Q: Why does the OTP change after some time?**

A: When system time crosses a 30-second boundary, the time counter changes, so
the HMAC input changes and the final OTP changes.

### HOTP Algorithm Details

**Q: What is the HOTP formula?**

A: `HOTP(K, C) = Truncate(HMAC-SHA1(K, C))`, where `K` is the secret key and
`C` is an 8-byte counter.

**Q: Why do you pack the counter with `struct.pack(">Q", counter)`?**

A: HOTP uses an 8-byte big-endian counter. `>Q` encodes the counter exactly in
that format: big-endian unsigned 64-bit integer.

**Q: Why big-endian?**

A: RFC 4226 treats HOTP values as big-endian. Using big-endian is required for
compatibility with tools such as `oathtool`.

**Q: Why 8 bytes for the counter?**

A: RFC 4226 uses an 8-byte counter. RFC 6238 also requires support for time
values larger than 32 bits, so a 64-bit representation is correct.

**Q: What is HMAC-SHA1 doing here?**

A: HMAC-SHA1 computes a keyed digest from the secret key and counter. The secret
key makes the output unpredictable to anyone who does not know the key.

**Q: Why not just hash the key and time with SHA-1?**

A: Plain hashing is not the RFC algorithm and is weaker as a keyed construction.
HMAC is specifically designed for keyed message authentication.

**Q: What does dynamic truncation mean?**

A: Dynamic truncation selects 4 bytes from the HMAC result. The start offset is
taken from the low 4 bits of the last HMAC byte.

**Q: Why not use the first 4 bytes of the HMAC result?**

A: RFC 4226 defines dynamic truncation, not fixed truncation. Using the first 4
bytes would not match the standard and would not match `oathtool`.

**Q: Why is the offset between 0 and 15?**

A: The offset is `digest[-1] & 0x0F`, which keeps only 4 bits. Four bits can
represent values from 0 to 15.

**Q: Why is it safe to read 4 bytes from that offset?**

A: SHA-1 produces 20 bytes. If the offset is at most 15, then `offset + 4` is at
most 19, which stays inside the 20-byte digest.

**Q: Why mask with `0x7FFFFFFF`?**

A: The selected 4 bytes are reduced to a positive 31-bit integer. This avoids
signed-integer ambiguity and follows RFC 4226.

**Q: Why modulo `10^6`?**

A: The project requires a 6-digit code. Modulo `10^6` maps the large integer to
the range `0..999999`.

**Q: Why use `zfill(6)`?**

A: Some valid OTPs start with zero. `zfill(6)` preserves the required fixed
6-digit format, for example `031805`.

**Q: Is modulo reduction perfectly uniform?**

A: It is not mathematically perfect because `2^31` is not exactly divisible by
`10^6`, but RFC 4226 analyzes this construction and accepts it for HOTP.

**Q: Can two different counters produce the same 6-digit OTP?**

A: Yes. The output space has only one million values, so collisions are
possible. Security comes from unpredictability and limited validity, not from
unique values forever.

### TOTP Algorithm Details

**Q: How is the TOTP counter calculated?**

A: `counter = floor((current_unix_time - T0) / X)`. This project uses `T0 = 0`
and `X = 30`.

**Q: Why use 30 seconds?**

A: RFC 6238 recommends 30 seconds as a balance between usability and security.
It is also the default used by common tools such as `oathtool`.

**Q: What happens if the system clock is wrong?**

A: The generated OTP may not match the verifier. Real systems allow a small
validation window or resynchronization, but this project only generates codes.

**Q: Does this project verify OTPs?**

A: No. The subject asks for generation. A real verifier would compare the
submitted code with one or more acceptable time windows and reject replayed
codes.

**Q: Why mention replay if this project only generates?**

A: TOTP values can be reused within their time window unless a verifier tracks
successful use. That is a limitation of generation-only tools.

**Q: Is the generated OTP truly one-time?**

A: In this local generator, it is time-limited, not enforced one-time. One-time
use must be enforced by a server or verifier.

### RFC Questions

**Q: Which RFC is the main subject requirement?**

A: RFC 6238, because the subject asks for a TOTP system.

**Q: Why is RFC 4226 important if the subject says TOTP?**

A: RFC 6238 builds TOTP from HOTP. To implement TOTP correctly, the project must
implement HOTP correctly.

**Q: What does RFC 2104 add?**

A: RFC 2104 defines HMAC. HOTP uses HMAC-SHA1, so RFC 2104 explains the keyed
hash construction used by HOTP.

**Q: What does RFC 2119 add?**

A: RFC 2119 defines requirement words such as MUST, SHOULD, MAY, and OPTIONAL.
It tells us how to interpret RFC requirement strength.

**Q: What does RFC 4086 add?**

A: RFC 4086 explains randomness requirements. It matters because OTP security
depends on an unpredictable secret key.

**Q: What does RFC 6030 add?**

A: RFC 6030 defines PSKC, a standard container for provisioning symmetric keys.
This project does not implement PSKC, but it is relevant to real OTP key
provisioning.

**Q: What does RFC 5741 add?**

A: RFC 5741 explains RFC document streams and status. It is not part of the OTP
algorithm, but RFC 6238 references it in its status text.

**Q: Is RFC 6238 an Internet Standard?**

A: RFC 6238 is informational, but the project subject explicitly requires using
it, so it is the correct reference for this project.

**Q: Does RFC 6238 allow SHA-256 or SHA-512?**

A: Yes, RFC 6238 allows HMAC-SHA-256 or HMAC-SHA-512 variants. This project uses
HMAC-SHA1 because HOTP in RFC 4226 uses SHA-1 and `oathtool --totp` defaults to
SHA-1.

### Code Implementation Questions

**Q: Where is the algorithm implemented?**

A: In `ft_otp_core.py`, specifically in `hotp` and `totp`.

**Q: Where is argument parsing implemented?**

A: In `ft_otp.py`, mainly in `parse_args` and `main`.

**Q: Why separate core logic from CLI logic?**

A: It makes the code easier to read and test. The cryptographic functions stay
separate from argument parsing and terminal error handling.

**Q: Why use `Path.read_text(encoding="ascii")` for the key?**

A: The input key is expected to be hexadecimal ASCII. Non-ASCII input is invalid
and should be rejected.

**Q: Why normalize the key to lowercase?**

A: Hexadecimal is case-insensitive. Lowercasing makes storage consistent without
changing the binary secret.

**Q: Why reject odd-length hex strings?**

A: Two hex characters represent one byte. An odd-length hex string cannot be
decoded cleanly into bytes.

**Q: Why accept keys longer than 64 hex characters?**

A: The subject says "at least 64 characters", so longer valid even-length hex
keys are allowed.

**Q: Why does the error say 64 characters if longer keys are allowed?**

A: The message matches the subject example. In practice, the code enforces
"at least 64" plus valid hex and even length.

**Q: What happens if `ft_otp.key` is corrupted?**

A: Decryption or validation fails, and the CLI prints an error instead of
generating an OTP from invalid data.

**Q: What happens if the file does not exist?**

A: The `OSError` is caught and displayed as a user-facing error message.

**Q: Why use a custom `OtpError` exception?**

A: It separates expected user errors from programming errors and keeps CLI error
handling clean.

**Q: Why disable bytecode writing in the launcher?**

A: `PYTHONDONTWRITEBYTECODE=1` avoids creating `__pycache__` files during normal
runs, keeping the submission folder cleaner.

### Encryption and Security Questions

**Q: What is encrypted?**

A: The normalized hexadecimal secret string is encrypted before being written to
`ft_otp.key`.

**Q: What is not encrypted?**

A: The source code and hard-coded Fernet key are not encrypted. The input
plaintext key file is also not modified or deleted by the program.

**Q: Why use Fernet?**

A: Fernet provides authenticated symmetric encryption. It protects
confidentiality and detects tampering of the encrypted token.

**Q: Does Fernet generate the OTP?**

A: No. Fernet only encrypts and decrypts the stored key. OTP generation is done
manually with HOTP/TOTP code.

**Q: Is hard-coding `FERNET_KEY` secure?**

A: Not for production. Anyone with the source can decrypt `ft_otp.key`. For this
school project, it demonstrates encrypted storage, but a real system would use a
secret manager, passphrase, hardware-backed key, or OS keychain.

**Q: Why set `ft_otp.key` permissions to `0600`?**

A: It limits access to the file owner. Even encrypted secrets should have
restricted file permissions.

**Q: Is the OTP itself encrypted?**

A: No. The OTP is printed to standard output because the user needs to type or
copy it. The secret key is what must remain protected.

**Q: Is SHA-1 broken? Is this unsafe?**

A: SHA-1 collision resistance is weak for some uses, but HOTP uses HMAC-SHA1.
HMAC-SHA1 remains the standard HOTP construction in RFC 4226 and is what common
TOTP tools use by default.

**Q: What is the main security assumption?**

A: The attacker does not know the secret key. If the secret key is exposed, the
attacker can generate the same OTPs.

**Q: Why is randomness important?**

A: If the secret is predictable, an attacker can guess it and compute OTPs.
Strong random keys make guessing infeasible.

### Testing and Compatibility Questions

**Q: How do you know the algorithm is correct?**

A: The test script compares generated OTPs with `oathtool --totp` for fixed and
random keys. Matching `oathtool` confirms interoperability.

**Q: Why compare with `oathtool`?**

A: The subject recommends comparing with reference software. `oathtool` is a
standard command-line tool for HOTP/TOTP.

**Q: What does the test script check?**

A: It checks invalid input, missing files, successful encrypted key generation,
key-file permissions, 6-digit output, and multiple `oathtool` comparisons.

**Q: Why can a test fail near a 30-second boundary?**

A: If this program and `oathtool` run on different sides of a time boundary,
they may compute different counters. The test runs them close together to reduce
that risk.

**Q: How could boundary testing be improved?**

A: Add tests around injected timestamps for `totp`, or retry comparison if the
current time is too close to a 30-second boundary.

**Q: Why does the output sometimes start with zero?**

A: Because valid OTPs may be below `100000`. The code pads with zeros to keep
exactly 6 digits.

### Improvement Questions

**Q: What would you change for production?**

A: I would remove the hard-coded encryption key, use an OS keychain or
passphrase-derived key, add a verifier with replay protection, support key
rotation, and add stronger operational logging and tests.

**Q: Would you support SHA-256 or SHA-512?**

A: It could be added as an option because RFC 6238 allows it. For this project,
SHA-1 is kept because it matches HOTP RFC 4226 and `oathtool` defaults.

**Q: Would you delete the plaintext input key after `-g`?**

A: The current program does not delete user files. In a real tool, secure cleanup
could be offered, but deleting user files automatically can be surprising.

**Q: Would you make the time step configurable?**

A: For interoperability, the project uses the common 30-second default. A real
tool could expose the time step as configuration if both prover and verifier
agree on it.

**Q: What is the biggest limitation of this project?**

A: It generates OTPs but does not verify them or prevent replay. Verification
and replay prevention belong on the server side.

**Q: What is the most important thing to understand for evaluation?**

A: TOTP is not a separate magic algorithm. It is HOTP where the counter is
derived from time. The project succeeds if HOTP is correct, time-counter
derivation is correct, and the secret key is stored encrypted.

## Why the Output Matches `oathtool`

`oathtool --totp <hex-key>` uses the usual TOTP defaults:

- HMAC-SHA1;
- 30-second time step;
- Unix epoch start;
- 6 decimal digits.

This project uses the same defaults. Therefore, for the same key and the same
time window, `./ft_otp -k ft_otp.key` should match `oathtool --totp`.

The test script verifies that comparison across several keys.

## Security Limitations

This project is correct for the subject, but it is not a production-grade OTP
server.

Important limitations:

- The Fernet encryption key is hard-coded in `ft_otp_core.py`.
- There is no verifier/server side that tracks used OTPs.
- The CLI only generates OTPs; it does not reject replayed OTPs.
- The encrypted key must still be protected by file permissions and local system
  security.

For the subject, that is fine: the required behavior is local generation of a
TOTP from an encrypted stored key.

## How to Test

Run from the project directory:

```bash
./test_ft_otp.sh
```

The test script checks:

- invalid non-hex keys;
- missing files;
- successful encrypted key generation;
- `ft_otp.key` is not plaintext;
- `ft_otp.key` permissions are `0600`;
- generated OTP has exactly 6 digits;
- generated OTP matches `oathtool`;
- multiple fixed and random keys match `oathtool`.

## Main References

- RFC 6238: <https://datatracker.ietf.org/doc/html/rfc6238>
- RFC 4226: <https://datatracker.ietf.org/doc/html/rfc4226>
- RFC 2104: <https://datatracker.ietf.org/doc/html/rfc2104>
- RFC 2119: <https://datatracker.ietf.org/doc/html/rfc2119>
- RFC 4086: <https://datatracker.ietf.org/doc/html/rfc4086>
- RFC 6030: <https://datatracker.ietf.org/doc/html/rfc6030>
- RFC 5741: <https://datatracker.ietf.org/doc/html/rfc5741>
